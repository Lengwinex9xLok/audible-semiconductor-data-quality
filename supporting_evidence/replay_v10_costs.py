"""New 2026-10-27 cash/share replay; not the contributor's missing original script.
Reads frozen derived inputs only. Standard library; no database or network calls.
Run from repository/package root: python supporting_evidence/replay_v10_costs.py extracted_v09
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

PUBLIC = 'lagged_positive_return'
PASSIVE = 'always_long'
TOL = 1e-12
EXPECTED = {
    'stock_daily_summary.csv': '7f4d65b8e170f3416f9b5feb3e0923d5426e160a356bced223ce9096bc57c8ea',
    'stock_performance_summary.csv': '64ee06912a73ec52621b0b9bfcffccd9d5bffd2af5dd9db8ffb1a78e6646c8c2',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def require_close(actual, expected, label):
    if not math.isfinite(actual) or abs(actual - expected) > TOL:
        raise ValueError(f'{label}: {actual!r} differs from {expected!r}')

def sleeve_wealth(prices, positions, bps):
    """Track cash and shares using the passive normalized price path.
    Sell at the end of the last active interval, including terminal liquidation.
    A continuing active signal incurs no additional round trip.
    """
    rate = float(bps) / 10000
    if not math.isfinite(rate) or not 0 <= rate < 1:
        raise ValueError('Invalid one-way cost')
    if len(prices) < 2 or len(positions) != len(prices) - 1:
        raise ValueError('Price/interval lengths differ')
    if any(not math.isfinite(x) or x <= 0 for x in prices):
        raise ValueError('Invalid price; legitimate exits require a separate event engine')
    if any(q not in (0, 1) for q in positions):
        raise ValueError('Invalid position')
    cash, shares = 1.0, 0.0
    values, buys, sells = [1.0], 0, 0
    for j, held in enumerate(positions):
        if held and shares == 0:
            shares = cash / (prices[j] * (1 + rate))
            cash = 0.0
            buys += 1
        if not held and shares != 0:
            raise ValueError('Open shares in a cash interval')
        if held and (j == len(positions)-1 or positions[j+1] == 0):
            cash = shares * prices[j+1] * (1 - rate)
            shares = 0.0
            sells += 1
        value = cash + shares * prices[j+1]
        if not math.isfinite(value) or value <= 0:
            raise ValueError('Invalid wealth')
        values.append(value)
    return values, buys, sells

def load_sleeves(inputs):
    summaries = [r for r in read_csv(inputs/'stock_performance_summary.csv') if r['period'] == '2025']
    paths = [r for r in read_csv(inputs/'stock_daily_summary.csv') if r['period'] == '2025']
    if not summaries or any(r['cost_case'] != 'gross_zero_cost' or float(r['spread_multiplier']) != 0 for r in summaries+paths):
        raise ValueError('Expected saved gross 2025 inputs')
    if {r['strategy'] for r in summaries} != {PUBLIC, PASSIVE} or {r['strategy'] for r in paths} != {PUBLIC, PASSIVE}:
        raise ValueError('Expected both strategies')
    tickers = sorted({r['ticker'] for r in summaries})
    if len(tickers) != 10 or {r['ticker'] for r in paths} != set(tickers):
        raise ValueError('Expected the frozen ten-stock sample')
    sleeves, calendar = [], None
    for ticker in tickers:
        summary = {}
        blocks = {}
        for strategy in (PUBLIC, PASSIVE):
            candidates = [r for r in summaries if r['ticker']==ticker and r['strategy']==strategy]
            if len(candidates) != 1:
                raise ValueError('Duplicate/missing stock summary')
            summary[strategy] = candidates[0]
            block = sorted([r for r in paths if r['ticker']==ticker and r['strategy']==strategy], key=lambda r:r['date'])
            dates = [r['date'] for r in block]
            if len(dates)<2 or len(set(dates))!=len(dates):
                raise ValueError('Invalid dates')
            if calendar is None:
                calendar = dates
            if dates != calendar:
                raise ValueError('Calendar mismatch')
            if [int(r['is_initial']) for r in block] != [1]+[0]*(len(block)-1):
                raise ValueError('Invalid baseline markers')
            for row in block:
                if not math.isfinite(float(row['wealth'])) or float(row['wealth'])<=0:
                    raise ValueError('Invalid saved wealth')
            require_close(float(block[0]['wealth']), 1.0, 'Initial wealth')
            blocks[strategy] = block
        # Baseline position is intentionally blank; only actual intervals need q.
        positions = [float(r['position']) for r in blocks[PUBLIC][1:]]
        prices = [float(r['wealth']) for r in blocks[PASSIVE]]
        gross, _, _ = sleeve_wealth(prices, positions, 0)
        for actual, row in zip(gross, blocks[PUBLIC]):
            require_close(actual, float(row['wealth']), 'Gross public path')
        require_close(gross[-1]-1, float(summary[PUBLIC]['cumulative_return']), 'Public summary')
        require_close(prices[-1]-1, float(summary[PASSIVE]['cumulative_return']), 'Passive summary')
        weight = float(summary[PUBLIC]['initial_portfolio_weight'])
        if not math.isfinite(weight) or weight<0:
            raise ValueError('Invalid sleeve weight')
        sleeves.append((weight, prices, positions))
    require_close(sum(s[0] for s in sleeves), 1, 'Weight sum')
    return sleeves, calendar

def replay(bundle, expected_csv):
    inputs = bundle/'inputs'
    before = {name:digest(inputs/name) for name in EXPECTED}
    if before != EXPECTED:
        raise ValueError('Frozen input hashes differ')
    expected_digest = digest(expected_csv)
    expected_rows = read_csv(expected_csv)
    if len(expected_rows)!=4 or {float(r['one_way_bps']) for r in expected_rows}!={0,.5,1,2}:
        raise ValueError('Expected four distinct published cases')
    if any(r['period']!='2025' or r['convention']!='annual_matched_cash_start' for r in expected_rows):
        raise ValueError('Unexpected experiment convention')
    sleeves, calendar = load_sleeves(inputs)
    def portfolio(bps, active):
        total, buys, sells = 0.0, 0, 0
        for weight, prices, positions in sleeves:
            path, nb, ns = sleeve_wealth(prices, positions if active else [1]*(len(prices)-1), bps)
            total += weight*path[-1]
            buys += nb
            sells += ns
        return total-1, buys, sells
    gross_public = portfolio(0, True)[0]
    gross_passive = portfolio(0, False)[0]
    results, max_error = [], 0.0
    for reference in sorted(expected_rows, key=lambda r:float(r['one_way_bps'])):
        bps = float(reference['one_way_bps'])
        public, entries, exits = portfolio(bps, True)
        passive, _, _ = portfolio(bps, False)
        gap = public-passive
        extra = (gross_public-public)-(gross_passive-passive)
        row = dict(one_way_bps=bps, net_public=public, net_matched_passive=passive, net_gap=gap, extra_drag=extra)
        for key in ('net_public','net_matched_passive','net_gap','extra_drag'):
            error = abs(row[key]-float(reference[key]))
            max_error = max(max_error,error)
            require_close(row[key],float(reference[key]),key)
        require_close(gap,(gross_public-gross_passive)-extra,'Relative drag identity')
        row.update(public_entries=entries,public_exits=exits)
        results.append(row)
    if before != {name:digest(inputs/name) for name in EXPECTED} or expected_digest != digest(expected_csv):
        raise ValueError('Input files changed')
    return dict(status='PASS',implementation='new_cash_and_share_replay_20261027',
        provenance='New reconstruction after 5e622d6; not the missing contributor M11 source or original receipt',
        executed_at_utc=datetime.now(timezone.utc).isoformat(),period='2025',
        convention='annual_matched_cash_start',inputs_sha256=before,expected_csv_sha256=expected_digest,
        script_sha256=digest(Path(__file__)),securities=len(sleeves),intervals_per_security=len(calendar)-1,
        tolerance=TOL,max_absolute_error=max_error,cases=results,inputs_unchanged=True,
        raw_wrds_queried=False,continuous_four_year_replayed=False,independent_human_verification=False)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('extracted_v09',type=Path)
    parser.add_argument('--expected',type=Path,default=Path(__file__).with_name('cost_sensitivity_2025_v10.csv'))
    parser.add_argument('--receipt',type=Path,help='Optional NEW output file; existing files are rejected')
    args=parser.parse_args()
    result=replay(args.extracted_v09,args.expected)
    text=json.dumps(result,indent=2)
    if args.receipt:
        with args.receipt.open('x',encoding='utf-8') as stream:
            stream.write(text+'\n')
    print(text)

if __name__=='__main__':
    main()
