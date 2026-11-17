"""Check Twelve Data against saved CRSP results; print only derived results."""
import argparse
import csv
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
import getpass
import json
import math
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, quote_plus, urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
NASDAQ = frozenset('NVDA MSFT AAPL ADI AMAT AMD INTC KLAC LRCX MU QCOM TXN WMT'.split())
NYSE = frozenset('JPM XOM BAC CVX JNJ UNH PG'.split())
SYMBOLS = sorted(NASDAQ | NYSE)
COLS = ('rule_return_pct', 'buy_hold_return_pct')
HOLIDAYS = set(map(date.fromisoformat, '''
2025-01-01 2025-01-09 2025-01-20 2025-02-17 2025-04-18
2025-05-26 2025-06-19 2025-07-04 2025-09-01 2025-11-27 2025-12-25
2026-01-01 2026-01-19 2026-02-16 2026-04-03 2026-05-25
2026-06-19 2026-07-03 2026-09-07 2026-11-26 2026-12-25
'''.split()))
STOCK_TOLERANCE_PP = 1.0
PORTFOLIO_TOLERANCE_PP = 0.25
# KLA issuer filings/announcements: 2025 ex dates and cash dividends, plus
# 2026 declarations through Nov 16. All amounts below are per post-split share.
# The June 2026 10-for-1 split is already reflected in adjust=splits prices.
KLAC_DIVIDENDS = {date.fromisoformat(d): Decimal(a) for d, a in (
    ('2025-02-24', '0.17'), ('2025-05-19', '0.19'), ('2025-08-18', '0.19'),
    ('2025-11-17', '0.19'), ('2026-02-17', '0.19'), ('2026-05-18', '0.23'),
    ('2026-08-17', '0.23'), ('2026-11-16', '0.23'),
)}
KLAC_VERIFIED_THROUGH = date(2026, 11, 16)


def expected_days(first, last):
    return [d for i in range((last - first).days + 1)
            if (d := first + timedelta(days=i)).weekday() < 5 and d not in HOLIDAYS]


def error_detail(data, key):
    if not isinstance(data, dict):
        return ''
    message = data.get('message')
    if not isinstance(message, str):
        return ''
    for secret in {key, quote(key, safe=''), quote_plus(key)}:
        if secret:
            message = message.replace(secret, '[redacted]')
    message = re.sub(r'https?://\S+', '[URL omitted]', message)
    return ': ' + ' '.join(message.split())[:300] if message.strip() else ''


def request_series(key, **params):
    query = urlencode(params)
    req = Request('https://api.twelvedata.com/time_series?' + query,
                  headers={'Authorization': 'apikey ' + key})
    try:
        with urlopen(req, timeout=20) as response:
            data = json.load(response)
    except HTTPError as exc:
        with exc:
            try:
                detail = error_detail(json.loads(exc.read(8192)), key)
            except (ValueError, OSError):
                detail = ' (no JSON error details)'
        raise ValueError(f'Twelve Data HTTP {exc.code}{detail}') from None
    except (URLError, TimeoutError, OSError, ValueError):
        raise ValueError('Twelve Data connection or response failed') from None
    if not isinstance(data, dict) or data.get('status') == 'error' or 'values' not in data:
        code = data.get('code') if isinstance(data, dict) else None
        raise ValueError(f'Twelve Data rejected request '
                         f'(code {code if isinstance(code, int) else "unknown"}){error_detail(data, key)}')
    return data


def listing_venue(meta):
    mic = str(meta.get('mic_code') or '').strip().upper()
    exchange = ' '.join(str(meta.get('exchange') or '').strip().upper().split())
    if mic:
        return {'XNAS': 'NASDAQ', 'XNGS': 'NASDAQ', 'XNMS': 'NASDAQ',
                'XNCM': 'NASDAQ', 'XNYS': 'NYSE'}.get(mic)
    if exchange in {'NASDAQ', 'NASDAQ GLOBAL SELECT MARKET', 'NASDAQ GLOBAL MARKET',
                    'NASDAQ CAPITAL MARKET'}:
        return 'NASDAQ'
    if exchange in {'NYSE', 'NEW YORK STOCK EXCHANGE'}:
        return 'NYSE'
    return None


def fetch(symbol, key, start, end, adjust):
    venues = {'NASDAQ', 'NYSE'} if symbol == 'WMT' else {
        'NASDAQ' if symbol in NASDAQ else 'NYSE'}
    # The account's `symbol + mic_code` request failed, while the otherwise
    # identical symbol-only query worked. Validate the listing after the fetch.
    # Date-only end_date can exclude that day's bar. Ask through the next
    # midnight, then explicitly discard that boundary bar if it is returned.
    boundary = end + timedelta(days=1)
    try:
        data = request_series(key, symbol=symbol, interval='1day',
                              start_date=start, end_date=boundary, adjust=adjust, dp=11)
    except ValueError as exc:
        raise ValueError(f'{symbol} adjust={adjust}: {exc}') from None
    meta = data.get('meta', {})
    if (meta.get('symbol') != symbol or listing_venue(meta) not in venues or
            meta.get('currency') != 'USD' or meta.get('interval') != '1day'):
        raise ValueError(f'{symbol}: wrong instrument, exchange, currency, or interval')
    prices = {}
    for row in data['values']:
        try:
            d = date.fromisoformat(row['datetime'][:10])
            if d == boundary:
                continue
            price = Decimal(row['close'])
            if d in prices or not start <= d <= end or not price.is_finite() or price <= 0:
                raise ValueError
            prices[d] = price
        except (ValueError, TypeError, KeyError, InvalidOperation):
            raise ValueError(f'{symbol}: invalid or duplicate daily bar') from None
    if not prices:
        raise ValueError(f'{symbol}: empty history')
    return prices


def diagnose(key):
    base = dict(symbol='NVDA', interval='1day')
    historic = dict(start_date='2024-06-07', end_date='2024-06-11')
    checks = [
        ('recent default', dict(outputsize=3)),
        ('recent adjust=all', dict(outputsize=3, adjust='all')),
        ('2024 adjust=all without MIC', dict(historic, adjust='all', dp=11)),
        ('2024 original request', dict(historic, adjust='all', dp=11, mic_code='XNAS')),
    ]
    for i, (label, params) in enumerate(checks):
        if i:
            time.sleep(12)
        try:
            data = request_series(key, **base, **params)
            dates = sorted(str(row['datetime'])[:10] for row in data['values'])
            print(f'{label}: {len(dates)} rows; {dates[0] if dates else "-"} to '
                  f'{dates[-1] if dates else "-"}', flush=True)
        except (ValueError, TypeError, KeyError) as exc:
            print(f'{label}: {exc if isinstance(exc, ValueError) else "invalid response"}',
                  flush=True)


def sleeve_totals(prices, days, first, cash_dividends=None):
    selected = [prices[d] for d in days]
    cash_dividends = cash_dividends or {}
    returns = [float((b + cash_dividends.get(d, 0)) / a - 1)
               for a, b, d in zip(selected, selected[1:], days[1:])]
    i = days.index(first) - 1   # Return index is one earlier than price-date index.
    if i < 2:
        raise ValueError('Missing two prior returns for the first holding interval')
    return (math.prod(1 + returns[j] if returns[j-2] > 0 else 1.0
                      for j in range(i, len(returns))),
            math.prod(1 + r for r in returns[i:]))


def diagnose_klac(key, reference):
    """Locate differences in return factors without printing licensed prices."""
    start, end = date(2024, 12, 27), date(2026, 6, 15)
    prices = {}
    for i, adjustment in enumerate(('all', 'splits', 'none')):
        if i:
            time.sleep(12)
        lo, hi = (date(2026, 6, 11), end) if adjustment == 'none' else (start, end)
        print(f'KLAC request {i+1}/3: adjust={adjustment}', file=sys.stderr, flush=True)
        prices[adjustment] = fetch('KLAC', key, lo, hi, adjustment)
    days = expected_days(start, date(2025, 12, 31))
    report = {'crsp_2025': dict(zip(COLS, reference['2025', 'Stock', 'KLAC']))}
    for adjustment in ('all', 'splits'):
        actual = sleeve_totals(prices[adjustment], days, date(2025, 1, 2))
        report[f'twelve_data_2025_{adjustment}'] = dict(zip(COLS, ((x-1)*100 for x in actual)))

    def factor(adjustment, prev, curr):
        return prices[adjustment][curr] / prices[adjustment][prev]

    changes = []
    for prev, curr in zip(days, days[1:]):
        difference = float((factor('all', prev, curr) / factor('splits', prev, curr) - 1) * 100)
        if abs(difference) >= 0.001 and curr.year == 2025:
            changes.append({'date': curr.isoformat(), 'adjustment_pct': round(difference, 5)})
    before, after = date(2026, 6, 11), date(2026, 6, 12)
    report['2025_adjustment_days'] = changes
    report['2026_split_probe'] = {
        'date': after.isoformat(),
        'all_vs_none_factor': float(factor('all', before, after) / factor('none', before, after)),
        'splits_vs_none_factor': float(factor('splits', before, after) / factor('none', before, after)),
    }
    print(json.dumps(report, indent=2))


def reconcile(totals, reference):
    comp = {}
    for j, column in enumerate(COLS):
        differences = {s: (totals[s][j] - 1) * 100 - reference['2025', 'Stock', s][j]
                       for s in SYMBOLS}
        worst = max(differences, key=lambda s: abs(differences[s]))
        # CRSP's 2025 sample row starts with weights that drifted since 2022.
        weights = {s: math.prod(1 + reference[year, 'Stock', s][j] / 100
                                for year in ('2022', '2023', '2024')) for s in SYMBOLS}
        observed = 100 * (sum(weights[s] * totals[s][j] for s in SYMBOLS) / sum(weights.values()) - 1)
        expected = reference['2025', 'Sample', 'All 20'][j]
        comp[column] = dict(twelve_data_pct=observed, crsp_pct=expected,
                            gap_pp=observed-expected, worst_stock=worst,
                            worst_stock_gap_pp=differences[worst])
    return comp, all(abs(row['gap_pp']) <= PORTFOLIO_TOLERANCE_PP and
                     abs(row['worst_stock_gap_pp']) <= STOCK_TOLERANCE_PP for row in comp.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--diagnose', action='store_true',
                      help='Run four small NVDA requests; no backtest or price output')
    mode.add_argument('--diagnose-klac', action='store_true',
                      help='Isolate KLAC dividend and split differences without printing daily prices')
    mode.add_argument('--repair-klac', action='store_true',
                      help='Check issuer-sourced KLAC dividends against CRSP before proceeding')
    parser.add_argument('--through', type=date.fromisoformat, default=date(2026, 11, 16),
                        help='Last completed and published trading day to include')
    args = parser.parse_args()
    if args.through.year != 2026 or args.through < date(2026, 1, 2):
        parser.error('--through must be in the 2026 evaluation period')
    if args.repair_klac and args.through > KLAC_VERIFIED_THROUGH:
        parser.error('KLAC issuer dividend schedule has only been checked through 2026-11-16')
    key = os.environ.get('TWELVE_DATA_API_KEY') or getpass.getpass('Twelve Data API key: ')
    if not key.strip():
        parser.error('No key supplied')
    if args.diagnose:
        diagnose(key.strip())
        return 0
    with (ROOT / 'powerbi_cross_industry_20_gross_2022_2025.csv').open(encoding='utf-8-sig', newline='') as f:
        reference = {(r['period'], r['level'], r['item']): tuple(float(r[c]) for c in COLS)
                     for r in csv.DictReader(f)}
    try:
        if args.diagnose_klac:
            diagnose_klac(key.strip(), reference)
            return 0
        calls = 0

        def get(symbol, start, end, adjustment):
            nonlocal calls
            if calls:
                time.sleep(12)
            calls += 1
            print(f'Request {calls}/23: {symbol}, adjust={adjustment}', file=sys.stderr, flush=True)
            return fetch(symbol, key.strip(), start, end, adjustment)

        # Same-day return comparisons remove arbitrary adjusted price levels.
        cash = {'KLAC': KLAC_DIVIDENDS} if args.repair_klac else {}
        start = date(2024, 12, 27)
        all_prices = {}
        if args.repair_klac:
            all_prices['KLAC'] = get('KLAC', start, args.through, 'splits')
            days_2025 = expected_days(start, date(2025, 12, 31))
            klac = sleeve_totals(all_prices['KLAC'], days_2025, date(2025, 1, 2), KLAC_DIVIDENDS)
            deltas = [(wealth-1)*100 - baseline for wealth, baseline in
                      zip(klac, reference['2025', 'Stock', 'KLAC'])]
            print(f'KLAC corrected 2025 gap (pp): rule {deltas[0]:+.6f}, '
                  f'buy & hold {deltas[1]:+.6f}', flush=True)
            if max(map(abs, deltas)) > STOCK_TOLERANCE_PP:
                raise ValueError('KLAC still exceeds the original CRSP tolerance; no 20-stock rerun')
        start, end = date(2024, 6, 7), date(2024, 6, 11)
        before, after = date(2024, 6, 7), date(2024, 6, 10)
        split_adjusted = get('NVDA', start, end, 'all')
        split_raw = get('NVDA', start, end, 'none')
        factor = float((split_adjusted[after] / split_adjusted[before]) /
                       (split_raw[after] / split_raw[before]))
        if not 9.9 < factor < 10.1:
            raise ValueError(f'NVDA 2024 split probe did not verify adjustment (factor {factor:.4f})')
        start = date(2024, 12, 27)
        all_prices['AAPL'] = get('AAPL', start, args.through, 'all')
        a = date(2025, 2, 10)
        b = date(2025, 2, 7)
        div_probe = get('AAPL', b, date(2025, 2, 11), 'splits')
        uplift = float((all_prices['AAPL'][a] / all_prices['AAPL'][b]) /
                       (div_probe[a] / div_probe[b]) - 1)
        if not 0.0005 < uplift < 0.002:
            raise ValueError(f'AAPL 2025 dividend probe failed (relative change {uplift:.6f})')
        print(f'Corporate action probes passed: split factor {factor:.4f}; dividend uplift {uplift:.6f}.',
              file=sys.stderr, flush=True)
        for s in SYMBOLS:
            if s not in all_prices:
                # WMT transferred to Nasdaq on 2025-12-09. Use its continuous
                # history only if this listing returns the entire panel; do not
                # splice separately adjusted series across the transfer.
                all_prices[s] = get(s, start, args.through, 'all')
        days = expected_days(start, args.through)
        shared_end = min(max(p) for p in all_prices.values())
        if shared_end < date(2026, 1, 2):
            raise ValueError('No common 2026 daily history across all 20 stocks')
        days = [d for d in days if d <= shared_end]
        for s, p in all_prices.items():
            missing = set(days) - set(p)
            unexpected = {d for d in p if d <= shared_end} - set(days)
            if missing or unexpected:
                raise ValueError(f'{s}: calendar mismatch ({len(missing)} missing, {len(unexpected)} unexpected)')
        audit_2025, passes = reconcile(
            {s: sleeve_totals(p, [d for d in days if d.year <= 2025], date(2025, 1, 2),
                              cash.get(s))
             for s, p in all_prices.items()}, reference)
        report = dict(status='PASS' if passes else 'CRSP_MISMATCH', symbols=len(SYMBOLS),
                      through=shared_end.isoformat(), split_probe_factor=factor,
                      dividend_probe_uplift=uplift, crsp_overlap=audit_2025,
                      comparison_tolerances_pp={'portfolio': PORTFOLIO_TOLERANCE_PP,
                                                 'per_stock': STOCK_TOLERANCE_PP},
                      sessions_behind_requested_end=sum(d > shared_end for d in expected_days(start, args.through)))
        if passes:
            totals = [sleeve_totals(p, days, date(2026, 1, 2), cash.get(s))
                      for s, p in all_prices.items()]
            rule, buy = [(sum(t[j] for t in totals) / len(totals) - 1) * 100 for j in range(2)]
            report.update(ytd_rule_pct=rule, ytd_buy_hold_pct=buy, ytd_gap_pp=rule-buy,
                          ytd_sessions=sum(d.year == 2026 for d in days),
                          scope='Hypothetical; fresh 5% sleeves; gross; Twelve Data adjusted daily returns',
                          klac_dividends='issuer cash dividends on split-adjusted prices'
                          if args.repair_klac else 'Twelve Data adjust=all')
        print(json.dumps(report, indent=2))
        return 0 if passes else 1
    except (ValueError, KeyError) as exc:
        print(f'Check stopped: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
