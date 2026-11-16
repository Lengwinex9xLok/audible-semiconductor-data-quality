"""Read-only check of invested-sleeve share from saved WRDS inputs.

Place alongside replay_wrds.py. No source records are written or displayed.
"""
import hashlib
import json
import runpy
from pathlib import Path

import numpy as np
import pandas as pd
import replay_wrds as replay


def verify_shares(daily, calendar, result):
    """Cross-check output vs raw lagged-return signals, excluding the base row."""
    dates = pd.DatetimeIndex(pd.to_datetime(calendar, errors='raise'))
    groups = [(int(permno), p.sort_values('date').reset_index(drop=True))
              for permno, p in daily.groupby('permno', sort=True)]
    if len(groups) != 20 or any(not pd.DatetimeIndex(pd.to_datetime(p.date)).equals(dates) for _, p in groups):
        raise ValueError('Expected 20 complete, calendar-aligned stock sleeves')
    n = len(dates) - 2
    if n <= 0:
        raise ValueError('Not enough observations for the two-session timing rule')
    wanted_dates = dates[2:].strftime('%Y-%m-%d').tolist()
    direct = np.stack([(p['ret'].to_numpy(float)[:-2] > 0).astype(int) for _, p in groups])
    if direct.shape != (20, n):
        raise ValueError('Unexpected direct signal matrix shape')
    paths = result[1]
    summary = result[0]
    result_json = {}
    for strategy in ('lagged_positive_return', 'always_long'):
        subset = paths.loc[paths.period.eq('All') & paths.strategy.eq(strategy) &
                           paths.cost_case.eq('gross_zero_cost')].copy()
        actual = subset.loc[subset.is_initial.eq(0)].sort_values('date')
        initial = subset.loc[subset.is_initial.eq(1)]
        if len(initial) != 1 or len(actual) != n or actual.date.astype(str).tolist() != wanted_dates:
            raise ValueError('Unexpected period paths or initial row')
        independent = direct if strategy == 'lagged_positive_return' else np.ones((20, n), dtype=int)
        calculated = independent.mean(axis=0)
        reported = actual.invested_sleeve_share.to_numpy(float)
        if not np.isfinite(reported).all():
            raise ValueError('Missing invested-share values')
        np.testing.assert_allclose(reported, calculated, rtol=0, atol=1e-12)
        row = summary.loc[summary.period.eq('All') & summary.strategy.eq(strategy) &
                          summary.cost_case.eq('gross_zero_cost')]
        if len(row) != 1:
            raise ValueError('Expected a single full-period summary')
        mean = float(calculated.mean())
        np.testing.assert_allclose(row.average_invested_sleeve_share.iloc[0], mean, rtol=0, atol=1e-12)
        result_json[strategy] = {'mean_sleeve_share': mean, 'mean_sleeve_share_pct': mean * 100,
                                 'held_sleeve_intervals': int(independent.sum()),
                                 'total_sleeve_intervals': int(independent.size)}
    return {'intervals': n, 'sleeves': 20, 'first_interval_end': wanted_dates[0],
            'last_interval_end': wanted_dates[-1], 'strategies': result_json}


def main():
    base = Path.home() / 'audible_cross_industry_20261115'
    project = Path.home() / 'audible_semiconductors_20261025' / 'Audible-Semiconductor'
    old = base / 'run_20261115T101618Z_07eb6156'
    current = base / 'twenty_stock_20261115T183448Z_35a432fa'
    prior = project / 'data/semiconductors/expansion_runs/ciz_2022_2025_20261026T165706Z_16656648'
    for directory, filename in ((old, 'manifest.json'), (current, 'new_data_manifest.json')):
        replay.check_manifest(directory, json.loads((directory / filename).read_text()))
    manifest = json.loads((prior / 'ciz_manifest.json').read_text())
    core_file = project / 'ciz_supplement_v01/benchmark_core_v02.py'
    aggregation_file = project / 'ciz_supplement_v01/ciz_aggregation.py'
    calendar_file = prior / 'raw/calendar.csv'
    for path in (core_file, aggregation_file):
        if replay.digest(path) != manifest['code_hashes'][path.name]:
            raise ValueError('Code hash mismatch: ' + path.name)
    if replay.digest(calendar_file) != manifest['input_hashes']['raw/calendar.csv']:
        raise ValueError('Calendar hash mismatch')
    reference = current / 'powerbi_gross_20.csv'
    if replay.digest(reference) != '86463bd682eaaccab45aa1c160bb6f05abfba19b65b513c68f9969dae044f383':
        raise ValueError('The saved results differ from the dashboard reference')
    raw = pd.concat([pd.read_csv(old / 'daily_crsp_ciz.csv'), pd.read_csv(current / 'daily_new_six.csv')], ignore_index=True)
    ident = pd.concat([pd.read_csv(old / 'identity_asof_2025-12-31.csv'),
                       pd.read_csv(current / 'identity_new_six.csv')], ignore_index=True)[['permno', 'ticker']]
    if len(ident) != 20 or not ident.permno.is_unique or not ident.ticker.is_unique:
        raise ValueError('Expected 20 unique security identities')
    daily = (raw.rename(columns={'dlycaldt':'date','dlyret':'ret','dlyretx':'retx','dlybid':'bid','dlyask':'ask'})
             .merge(ident, on='permno', validate='many_to_one').rename(columns={'ticker':'pilot_ticker'})
             .sort_values(['permno','date']).reset_index(drop=True))
    if len(daily) != 20100 or daily.duplicated(['permno','date']).any():
        raise ValueError('Unexpected stock-date panel')
    calendar = pd.to_datetime(pd.read_csv(calendar_file).trading_date)
    core = runpy.run_path(str(core_file))
    core['COST_CASES'] = {'gross_zero_cost': 0.0}
    aggregate = runpy.run_path(str(aggregation_file))['gross_only_evaluate']
    cohorts = json.loads((current / 'cohorts_before_results.json').read_text())['cohorts']
    actual, result = replay.build_table(daily, calendar, core, aggregate, cohorts)
    diff = replay.compare_tables(actual, pd.read_csv(reference))
    output = verify_shares(daily, calendar, result)
    output.update(status='PASS', rows_checked=len(actual), max_return_diff_pp=diff,
                  metric='mean fraction of 20 sleeves invested per holding interval, not value-weighted exposure',
                  scope='saved WRDS/CRSP inputs; gross-only; no raw data output')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
