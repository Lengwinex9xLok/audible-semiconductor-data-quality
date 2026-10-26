"""A fixed public daily benchmark. No network, broker, account or order access."""
from __future__ import annotations
import numpy as np
import pandas as pd

COST_CASES = {'gross_zero_cost': 0.0, 'quoted_spread_proxy': 1.0, 'double_spread_stress': 2.0}
STRATEGIES = ('lagged_positive_return', 'always_long')


def validate_panel(daily, calendar):
    required = {'permno', 'pilot_ticker', 'date', 'ret', 'bid', 'ask'}
    if not required.issubset(daily.columns):
        raise ValueError('Required columns missing: ' + ', '.join(sorted(required-set(daily.columns))))
    # Construct normalized columns without DataFrame.__setitem__ refcount checks.
    d = pd.DataFrame({
        **{c: daily[c].copy(deep=True) for c in daily.columns},
        'date': pd.to_datetime(daily['date'], format='%Y-%m-%d', errors='raise'),
        **{c: pd.to_numeric(daily[c], errors='raise') for c in ['permno', 'ret', 'bid', 'ask']},
    }, index=daily.index)
    days = pd.DatetimeIndex(pd.to_datetime(calendar, errors='raise'))
    if days.hasnans or days.has_duplicates or len(days)<4 or not days.is_monotonic_increasing:
        raise ValueError('Calendar must contain at least four distinct ordered dates')
    if d['date'].isna().any() or d[['permno', 'pilot_ticker']].isna().any().any():
        raise ValueError('Missing key or date')
    for c in ['permno', 'ret', 'bid', 'ask']:
        if not np.isfinite(d[c].to_numpy(dtype=float)).all():
            raise ValueError('Non-finite ' + c)
    if ((d['permno']<=0) | (d['permno']%1!=0)).any():
        raise ValueError('Invalid PERMNO')
    if (d['ret']<=-1).any():
        raise ValueError('Missing-code, delisting/loss boundary or invalid RET: review required')
    if ((d['bid']<=0) | (d['ask']<=d['bid'])).any():
        raise ValueError('All pilot quotes must be finite, positive and strictly uncrossed')
    if d.duplicated(['permno', 'date']).any():
        raise ValueError('Duplicate stock-date key')
    if d.groupby('permno')['pilot_ticker'].nunique().ne(1).any() or d.groupby('pilot_ticker')['permno'].nunique().ne(1).any():
        raise ValueError('Ambiguous stock label')
    for _, part in d.groupby('permno'):
        if not pd.DatetimeIndex(part.sort_values('date')['date']).equals(days):
            raise ValueError('Missing or unexpected stock-date: no silent row dropping or carry-forward')
    if d.empty:
        raise ValueError('Empty panel')
    return d.sort_values(['permno','date']).reset_index(drop=True), days


def sleeve_path(frame, strategy, multiplier):
    """Single fixed-capital sleeve; RET is a wealth reference, costs are a proxy."""
    if strategy not in STRATEGIES or not np.isfinite(multiplier) or multiplier<0:
        raise ValueError('Unknown strategy or invalid cost multiplier')
    n = len(frame)
    if n<4:
        raise ValueError('At least four dates required')
    # Interval i is close(i) -> close(i+1); signal uses RET(i-1).
    i = np.arange(1,n-1)
    ret = frame['ret'].to_numpy(dtype=float)
    q = (ret[i-1]>0).astype(int) if strategy=='lagged_positive_return' else np.ones(len(i), dtype=int)
    previous = np.r_[0,q[:-1]]
    following = np.r_[q[1:],0]  # terminal liquidation is fixed before the run
    entries = ((q==1)&(previous==0)).astype(int)
    exits = ((q==1)&(following==0)).astype(int)
    bid,ask = (frame[c].to_numpy(dtype=float) for c in ['bid','ask'])
    half = (ask-bid)/(ask+bid)
    if (multiplier*half>=1).any():
        raise ValueError('Cost haircut must remain below 100%')
    gross = np.where(q==1,1+ret[i+1],1.0)
    factors = gross / (1+multiplier*half[i]*entries) * (1-multiplier*half[i+1]*exits)
    return pd.DataFrame({'entry_date':frame['date'].iloc[i].to_numpy(),
        'date':frame['date'].iloc[i+1].to_numpy(), 'position':q,
        'entries':entries,'exits':exits,'wealth':np.cumprod(factors),
        'factor':factors})


def evaluate(daily, calendar):
    d, days = validate_panel(daily,calendar)
    grouped = list(d.groupby('permno',sort=True))
    summaries, paths = [], []
    for strategy in STRATEGIES:
        for case,multiplier in COST_CASES.items():
            sleeves = [sleeve_path(part.reset_index(drop=True),strategy,multiplier) for _,part in grouped]
            # Equal initial capital, no cross-stock daily rebalancing. Idle cash earns zero.
            wealth = np.mean([s['wealth'].to_numpy() for s in sleeves],axis=0)
            exposure = np.mean([s['position'].to_numpy() for s in sleeves],axis=0)
            entries = np.sum([s['entries'].to_numpy() for s in sleeves],axis=0)
            exits = np.sum([s['exits'].to_numpy() for s in sleeves],axis=0)
            dates = sleeves[0]['date']
            for j in range(len(wealth)):
                paths.append(dict(strategy=strategy,cost_case=case,spread_multiplier=multiplier,
                    date=pd.Timestamp(dates.iloc[j]).strftime('%Y-%m-%d'),wealth=float(wealth[j]),
                    invested_sleeve_share=float(exposure[j]),entries=int(entries[j]),exits=int(exits[j])))
            summaries.append(dict(strategy=strategy,cost_case=case,spread_multiplier=multiplier,
                cumulative_return=float(wealth[-1]-1),stocks=len(grouped),holding_intervals=len(wealth),
                first_entry=days[1].strftime('%Y-%m-%d'),final_exit=days[-1].strftime('%Y-%m-%d'),
                average_invested_sleeve_share=float(exposure.mean()),entries=int(entries.sum()),exits=int(exits.sum())))
    result = pd.DataFrame(summaries)
    for strategy in STRATEGIES:
        values=result.loc[result['strategy'].eq(strategy),'cumulative_return'].to_numpy()
        if not (values[0]+1e-12>=values[1]>=values[2]-1e-12):
            raise AssertionError('Cost monotonicity failed')
    gross_map=result.loc[result['cost_case'].eq('gross_zero_cost')].set_index('strategy')['cumulative_return']
    passive=result.loc[result['strategy'].eq('always_long')].set_index('cost_case')['cumulative_return']
    result = pd.DataFrame({
        **{c: result[c].copy(deep=True) for c in result.columns},
        'cost_drag_return_difference': result['strategy'].map(gross_map)-result['cumulative_return'],
        'difference_from_always_long': result['cumulative_return']-result['cost_case'].map(passive),
    }, index=result.index)
    return result,pd.DataFrame(paths)
