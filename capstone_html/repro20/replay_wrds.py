"""Read-only replay of the saved 20-stock WRDS analysis and its 140-row table.

This uses the saved WRDS inputs in place; it never fetches data or writes outputs.
"""
import argparse
import hashlib
import json
import runpy
from pathlib import Path

import numpy as np
import pandas as pd


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(directory, manifest):
    for name, receipt in manifest['files'].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()):
            raise ValueError('Manifest points outside its saved run directory')
        if digest(path) != receipt['sha256']:
            raise ValueError(f'Input hash mismatch: {name}')


def build_table(daily, calendar, core, aggregate, cohorts):
    pieces = []
    all_result = None
    for label, names in cohorts.items():
        result = aggregate(daily[daily.pilot_ticker.isin(names)].copy(), calendar, core)
        if label == 'All 20':
            all_result = result
        part = result[0][['period', 'strategy', 'cumulative_return']].copy()
        part['sample'] = label
        pieces.append(part)
    if all_result is None:
        raise ValueError('Missing All 20 cohort')
    samples = pd.concat(pieces, ignore_index=True).pivot(
        index=['sample', 'period'], columns='strategy', values='cumulative_return'
    ).reset_index().rename(columns={'lagged_positive_return': 'rule', 'always_long': 'buy'})
    stocks = all_result[2].pivot(
        index=['period', 'ticker'], columns='strategy', values='cumulative_return'
    ).reset_index().rename(columns={'lagged_positive_return': 'rule', 'always_long': 'buy'})
    def as_table(frame, item, level):
        return pd.DataFrame({'period': frame.period, 'level': level, 'item': frame[item],
                             'rule_return_pct': frame.rule * 100,
                             'buy_hold_return_pct': frame.buy * 100,
                             'difference_pp': (frame.rule - frame.buy) * 100})
    report = pd.concat([as_table(samples, 'sample', 'Sample'), as_table(stocks, 'ticker', 'Stock')],
                       ignore_index=True).sort_values(['period', 'level', 'item']).reset_index(drop=True)
    return report, all_result


def compare_tables(actual, reference):
    keys = ['period', 'level', 'item']
    columns = ['rule_return_pct', 'buy_hold_return_pct', 'difference_pp']
    actual = actual.sort_values(keys).reset_index(drop=True)
    reference = reference.sort_values(keys).reset_index(drop=True)
    if len(actual) != 140 or len(reference) != 140 or not actual[keys].equals(reference[keys]):
        raise ValueError('Result rows do not match the 140-row reference')
    np.testing.assert_allclose(actual[columns].to_numpy(float), reference[columns].to_numpy(float),
                               rtol=0, atol=1e-8)
    return float(np.abs(actual[columns].to_numpy(float) - reference[columns].to_numpy(float)).max())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=Path.home() / 'audible_cross_industry_20261115')
    parser.add_argument('--project', type=Path, default=Path.home() / 'audible_semiconductors_20261025' / 'Audible-Semiconductor')
    args = parser.parse_args()
    old = args.base / 'run_20261115T101618Z_07eb6156'
    current = args.base / 'twenty_stock_20261115T183448Z_35a432fa'
    prior = args.project / 'data/semiconductors/expansion_runs/ciz_2022_2025_20261026T165706Z_16656648'
    for directory, filename in [(old, 'manifest.json'), (current, 'new_data_manifest.json')]:
        check_manifest(directory, json.loads((directory / filename).read_text()))
    manifest = json.loads((prior / 'ciz_manifest.json').read_text())
    core_file = args.project / 'ciz_supplement_v01/benchmark_core_v02.py'
    aggregation_file = args.project / 'ciz_supplement_v01/ciz_aggregation.py'
    calendar_file = prior / 'raw/calendar.csv'
    for path in [core_file, aggregation_file]:
        if digest(path) != manifest['code_hashes'][path.name]:
            raise ValueError(f'Code hash mismatch: {path.name}')
    if digest(calendar_file) != manifest['input_hashes']['raw/calendar.csv']:
        raise ValueError('Calendar hash mismatch')
    reference_file = current / 'powerbi_gross_20.csv'
    if digest(reference_file) != '86463bd682eaaccab45aa1c160bb6f05abfba19b65b513c68f9969dae044f383':
        raise ValueError('Saved reference differs from the dashboard table')
    raw = pd.concat([pd.read_csv(old / 'daily_crsp_ciz.csv'), pd.read_csv(current / 'daily_new_six.csv')], ignore_index=True)
    ident = pd.concat([pd.read_csv(old / 'identity_asof_2025-12-31.csv'),
                       pd.read_csv(current / 'identity_new_six.csv')], ignore_index=True)[['permno', 'ticker']]
    if len(ident) != 20 or not ident.permno.is_unique or not ident.ticker.is_unique:
        raise ValueError('Expected 20 unique security identities')
    daily = (raw.rename(columns={'dlycaldt': 'date', 'dlyret': 'ret', 'dlyretx': 'retx', 'dlybid': 'bid', 'dlyask': 'ask'})
             .merge(ident, on='permno', validate='many_to_one').rename(columns={'ticker': 'pilot_ticker'})
             .sort_values(['permno', 'date']).reset_index(drop=True))
    if len(daily) != 20100 or daily.permno.nunique() != 20 or daily.duplicated(['permno', 'date']).any():
        raise ValueError('Unexpected stock-date panel')
    calendar = pd.to_datetime(pd.read_csv(calendar_file).trading_date)
    if not all(pd.DatetimeIndex(pd.to_datetime(part.date)).equals(pd.DatetimeIndex(calendar))
               for _, part in daily.groupby('permno')):
        raise ValueError('Stock dates do not match the saved calendar')
    core = runpy.run_path(str(core_file))
    core['COST_CASES'] = {'gross_zero_cost': 0.0}
    aggregate = runpy.run_path(str(aggregation_file))['gross_only_evaluate']
    cohorts = json.loads((current / 'cohorts_before_results.json').read_text())['cohorts']
    actual, result = build_table(daily, calendar, core, aggregate, cohorts)
    max_difference = compare_tables(actual, pd.read_csv(reference_file))
    drawdowns = {}
    for strategy in ['lagged_positive_return', 'always_long']:
        path = result[1].loc[result[1].period.eq('All') & result[1].strategy.eq(strategy)].sort_values('date')
        wealth = path.wealth.to_numpy(float)
        if len(wealth) != 1004 or not np.isfinite(wealth).all():
            raise ValueError('Unexpected full-period wealth path')
        dd = 100 * (wealth / np.maximum.accumulate(wealth) - 1)
        drawdowns[strategy] = {'max_drawdown_pct': float(dd.min()), 'trough': str(path.date.iloc[int(np.argmin(dd))])}
    events = result[5]
    counts = {status.lower(): int(((events.quote_status == status) & (events.cost_required == 1)).sum())
              for status in ['CROSSED', 'LOCKED']}
    np.testing.assert_allclose([drawdowns['lagged_positive_return']['max_drawdown_pct'],
                                drawdowns['always_long']['max_drawdown_pct']],
                               [-21.274674782767956, -25.355233489553463], rtol=0, atol=1e-8)
    if (drawdowns['lagged_positive_return']['trough'] != '2022-10-12' or
            drawdowns['always_long']['trough'] != '2022-09-30' or counts != {'crossed': 3, 'locked': 23}):
        raise ValueError('Drawdown dates or required quote-event counts differ from the saved run')
    print(json.dumps({'status': 'PASS', 'rows_checked': len(actual), 'maximum_absolute_difference_pp': max_difference,
                      'drawdowns': drawdowns, 'required_quote_events': counts,
                      'scope': 'saved 2022-2025 gross-only inputs; no source data fetched or written'}, indent=2))


if __name__ == '__main__':
    main()
