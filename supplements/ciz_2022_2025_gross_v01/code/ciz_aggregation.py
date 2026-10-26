"""Expanded time coverage with unchanged v02 financial engine and explicit quote eligibility."""
import numpy as np
import pandas as pd

def expanded_evaluate(daily,calendar,core):
    req={'permno','pilot_ticker','date','ret','bid','ask'}
    if not req.issubset(daily):raise ValueError('Missing columns')
    d=pd.DataFrame({**{c:daily[c].copy() for c in daily},'date':pd.to_datetime(daily['date'],errors='raise'),**{c:pd.to_numeric(daily[c],errors='raise') for c in ['permno','ret','bid','ask']}})
    days=pd.DatetimeIndex(pd.to_datetime(calendar,errors='raise'))
    if days.hasnans or days.has_duplicates or not days.is_monotonic_increasing or len(days)<4:raise ValueError('Invalid calendar')
    if d.duplicated(['permno','date']).any() or d.pilot_ticker.isna().any():raise ValueError('Duplicate or missing key')
    if not np.isfinite(d[['permno','ret','bid','ask']].to_numpy(float)).all():raise ValueError('Missing/invalid numeric input')
    if (d.ret<=-1).any() or (d.permno<=0).any() or (d.permno%1!=0).any():raise ValueError('Invalid return or identifier')
    if d.groupby('permno').pilot_ticker.nunique().ne(1).any() or d.groupby('pilot_ticker').permno.nunique().ne(1).any():raise ValueError('Ambiguous identities')
    groups=[];events=[]
    for ident,part in d.groupby('permno',sort=True):
        part=part.sort_values('date').reset_index(drop=True)
        if not pd.DatetimeIndex(part.date).equals(days):raise ValueError('Missing/unexpected stock-date')
        # Only retained diagnostic flags for positive locked quotes and one unused crossed quote are allowed.
        for col,allowed in [('core_flags',{'CROSSED_QUOTE'}),('diagnostic_flags',{'LOCKED_QUOTE'})]:
            if col in part:
                seen={f for value in part[col].fillna('') for f in str(value).split(';') if f}
                if not seen.issubset(allowed):raise ValueError('Unexpected quality flag: '+str(seen))
        if (part.bid<=0).any() or (part.ask<=0).any():raise ValueError('Nonpositive quotes need review')
        for strategy in core['STRATEGIES']:
            # v02 financial accounting and lag are reused byte-for-byte.
            path=core['sleeve_path'](part,strategy,0.0)
            required=np.zeros(len(part),dtype=bool)
            required[1:-1] |= path.entries.to_numpy(bool)
            required[2:] |= path.exits.to_numpy(bool)
            crossed=part.bid.to_numpy()>part.ask.to_numpy()
            locked=part.bid.to_numpy()==part.ask.to_numpy()
            if (crossed & required).any() and any(float(k)>0 for k in core['COST_CASES'].values()):raise ValueError('Crossed quote is required for transaction cost; no repair/imputation')
            for j in np.flatnonzero(crossed|locked):
                events.append(dict(ticker=str(part.pilot_ticker.iloc[0]),date=part.date.iloc[j].strftime('%Y-%m-%d'),strategy=strategy,quote_status='CROSSED' if crossed[j] else 'LOCKED',cost_required=int(required[j])))
        groups.append(part)
    count=len(groups);paths=[];stocks=[];full=[]
    for strategy in core['STRATEGIES']:
        for case,k in core['COST_CASES'].items():
            sleeves=[core['sleeve_path'](part,strategy,k) for part in groups]
            means=np.mean([s.wealth.to_numpy() for s in sleeves],axis=0)
            for j,day in enumerate(days[2:]):
                paths.append(dict(strategy=strategy,cost_case=case,spread_multiplier=k,date=day.strftime('%Y-%m-%d'),wealth=float(means[j]),invested_sleeve_share=float(np.mean([s.position.iloc[j] for s in sleeves])),entries=int(sum(s.entries.iloc[j] for s in sleeves)),exits=int(sum(s.exits.iloc[j] for s in sleeves))))
            for part,s in zip(groups,sleeves):
                ticker=str(part.pilot_ticker.iloc[0])
                for r in s.itertuples(index=False):
                    stocks.append(dict(ticker=ticker,strategy=strategy,cost_case=case,spread_multiplier=k,date=pd.Timestamp(r.date).strftime('%Y-%m-%d'),entry_date=pd.Timestamp(r.entry_date).strftime('%Y-%m-%d'),wealth=float(r.wealth),position=int(r.position),entries=int(r.entries),exits=int(r.exits)))
    paths=pd.DataFrame(paths);stocks=pd.DataFrame(stocks)
    periods=['All']+sorted(set(paths.date.str[:4]))
    summaries=[];stock_summaries=[];period_paths=[];period_stock_paths=[]
    for period in periods:
        for strategy in core['STRATEGIES']:
            for case,k in core['COST_CASES'].items():
                allp=paths.loc[paths.strategy.eq(strategy)&paths.cost_case.eq(case)].sort_values('date')
                p=allp if period=='All' else allp.loc[allp.date.str.startswith(period)]
                first=str(p.date.iloc[0]);before=allp.loc[allp.date.lt(first)]
                startwealth=1.0 if before.empty else float(before.wealth.iloc[-1])
                base_date=days[1].strftime('%Y-%m-%d') if before.empty else str(before.date.iloc[-1])
                ss=stocks.loc[stocks.strategy.eq(strategy)&stocks.cost_case.eq(case)]
                rec=dict(period=period,strategy=strategy,cost_case=case,spread_multiplier=k,cumulative_return=float(p.wealth.iloc[-1]/startwealth-1),stocks=count,holding_intervals=len(p),first_entry=base_date,final_exit=str(p.date.iloc[-1]),average_invested_sleeve_share=float(p.invested_sleeve_share.mean()),entries=int(p.entries.sum()),exits=int(p.exits.sum()))
                summaries.append(rec)
                period_paths.append(dict(period=period,**{**p.iloc[0].to_dict(),'date':base_date,'wealth':1.0,'invested_sleeve_share':None,'entries':0,'exits':0},is_initial=1))
                for row in p.to_dict('records'):period_paths.append(dict(period=period,**{**row,'wealth':row['wealth']/startwealth},is_initial=0))
                for ticker,allstock in ss.groupby('ticker',sort=True):
                    allstock=allstock.sort_values('date');sub=allstock.loc[allstock.date.ge(first)&allstock.date.le(str(p.date.iloc[-1]))]
                    b=allstock.loc[allstock.date.lt(first)];stock_start=1.0 if b.empty else float(b.wealth.iloc[-1])
                    weight=stock_start/(count*startwealth)
                    sr=float(sub.wealth.iloc[-1]/stock_start-1)
                    stock_summaries.append(dict(period=period,ticker=ticker,strategy=strategy,cost_case=case,spread_multiplier=k,cumulative_return=sr,initial_portfolio_weight=weight,contribution_to_portfolio_return=weight*sr,holding_intervals=len(sub),first_entry=base_date,final_exit=str(sub.date.iloc[-1]),average_held_share=float(sub.position.mean()),entries=int(sub.entries.sum()),exits=int(sub.exits.sum())))
                    period_stock_paths.append(dict(period=period,**{**sub.iloc[0].to_dict(),'date':base_date,'entry_date':base_date,'wealth':1.0,'position':None,'entries':0,'exits':0},is_initial=1))
                    for row in sub.to_dict('records'):period_stock_paths.append(dict(period=period,**{**row,'wealth':row['wealth']/stock_start},is_initial=0))
    summary=pd.DataFrame(summaries);detail=pd.DataFrame(stock_summaries)
    for frame,keys,passive_keys in [(summary,['period','strategy'],['period','cost_case']),(detail,['period','ticker','strategy'],['period','ticker','cost_case'])]:
        gross=frame.loc[frame.cost_case.eq('gross_zero_cost')].set_index(keys).cumulative_return.to_dict()
        passive=frame.loc[frame.strategy.eq('always_long')].set_index(passive_keys).cumulative_return.to_dict()
        # Constructor style avoids the known Python 3.14/pandas assignment warning.
        values=frame.to_dict('records')
        updated=[dict(r,cost_drag_return_difference=gross[tuple(r[k] for k in keys)]-r['cumulative_return'],difference_from_always_long= r['cumulative_return']-passive[tuple(r[k] for k in passive_keys)]) for r in values]
        if frame is summary:summary=pd.DataFrame(updated)
        else:detail=pd.DataFrame(updated)
    pp=pd.DataFrame(period_paths);sp=pd.DataFrame(period_stock_paths)
    # Every period's contributions use actual starting weights, so annual returns reconcile despite drift.
    for r in summary.itertuples(index=False):
        sub=detail.loc[detail.period.eq(r.period)&detail.strategy.eq(r.strategy)&detail.cost_case.eq(r.cost_case)]
        assert np.isclose(sub.contribution_to_portfolio_return.sum(),r.cumulative_return,atol=1e-11,rtol=0)
        assert np.isclose(sub.initial_portfolio_weight.sum(),1,atol=1e-12,rtol=0)
        assert sub.entries.sum()==r.entries and sub.exits.sum()==r.exits
    for strategy in core['STRATEGIES']:
        for case in core['COST_CASES']:
            sub=summary.loc[summary.strategy.eq(strategy)&summary.cost_case.eq(case)]
            assert np.isclose(np.prod(1+sub.loc[sub.period.ne('All'),'cumulative_return']),1+sub.loc[sub.period.eq('All'),'cumulative_return'].iloc[0],atol=1e-10,rtol=0)
    monthly=[]
    for (strategy,case),allp in paths.groupby(['strategy','cost_case']):
        previous=1.0
        for month,g in allp.groupby(allp.date.str[:7],sort=True):
            ending=float(g.wealth.iloc[-1]);monthly.append(dict(month=month,strategy=strategy,cost_case=case,cumulative_return=ending/previous-1,holding_intervals=len(g),entries=int(g.entries.sum()),exits=int(g.exits.sum()),average_held_share=float(g.invested_sleeve_share.mean())));previous=ending
    return summary,pp,detail,sp,pd.DataFrame(monthly),pd.DataFrame(events)


def gross_only_evaluate(daily,calendar,core):
    if core["COST_CASES"] != {"gross_zero_cost":0.0}:
        raise ValueError("This supplementary entry point permits gross only")
    return expanded_evaluate(daily,calendar,core)
