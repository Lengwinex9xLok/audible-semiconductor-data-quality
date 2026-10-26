from pathlib import Path
import sys,runpy,unittest,hashlib,json
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pandas as pd,numpy as np
from expansion_core import expanded_evaluate
CORE=runpy.run_path(str(Path(__file__).resolve().parent/'benchmark_core_v02.py'))
def fixture():
 days=pd.DatetimeIndex(['2021-12-30','2021-12-31','2022-01-03','2022-01-04','2022-12-30','2023-01-03','2023-01-04'])
 rows=[dict(permno=i+1,pilot_ticker=t,date=d.strftime('%Y-%m-%d'),ret=r*(i+1),bid=99.,ask=101.) for i,t in enumerate(['A','B']) for d,r in zip(days,[.01,.01,.02,.03,.04,.02,.01])]
 return pd.DataFrame(rows),days
class ExpansionTests(unittest.TestCase):
 def test_matches_unchanged_engine(self):
  d,c=fixture();expected,paths=CORE['evaluate'](d,c);s,p,*_=expanded_evaluate(d,c,CORE)
  a=s[s.period.eq('All')].reset_index(drop=True)
  for col in expected:
   if pd.api.types.is_numeric_dtype(expected[col]):np.testing.assert_allclose(a[col],expected[col],atol=1e-12,rtol=0)
   else:self.assertEqual(a[col].tolist(),expected[col].tolist())
  b=p[p.period.eq('All')&p.is_initial.eq(0)].reset_index(drop=True)
  np.testing.assert_allclose(b.wealth,paths.wealth,atol=1e-12,rtol=0)
 def test_compound_annual_and_weight_drift(self):
  d,c=fixture();s,p,ds,*_=expanded_evaluate(d,c,CORE)
  q=ds[ds.period.eq('2023')&ds.strategy.eq('always_long')&ds.cost_case.eq('gross_zero_cost')]
  self.assertFalse(np.isclose(q.initial_portfolio_weight.iloc[0],.5))
  self.assertAlmostEqual(q.initial_portfolio_weight.sum(),1)
 def test_unused_crossed_quote_preserved(self):
  d,c=fixture();d.loc[2,'bid']=102.;before=d.copy(deep=True)
  out=expanded_evaluate(d,c,CORE);pd.testing.assert_frame_equal(d,before)
  event=out[-1].query("quote_status=='CROSSED'")
  self.assertEqual(event.cost_required.sum(),0)
 def test_required_crossed_quote_rejected(self):
  d,c=fixture();d.loc[1,'bid']=102.
  with self.assertRaisesRegex(ValueError,'Crossed quote'):expanded_evaluate(d,c,CORE)
 def test_locked_entry_explicit(self):
  d,c=fixture();d.loc[1,'bid']=101.;out=expanded_evaluate(d,c,CORE)
  event=out[-1].query("quote_status=='LOCKED'")
  self.assertEqual(event.cost_required.sum(),2)
 def test_missing_date_rejected(self):
  d,c=fixture()
  with self.assertRaisesRegex(ValueError,'stock-date'):expanded_evaluate(d.drop(index=2),c,CORE)
 def test_missing_return_rejected(self):
  d,c=fixture();d.loc[2,'ret']=np.nan
  with self.assertRaises(ValueError):expanded_evaluate(d,c,CORE)
 def test_no_annual_forced_trades(self):
  d,c=fixture();s,*_=expanded_evaluate(d,c,CORE)
  q=s[s.strategy.eq('always_long')&s.cost_case.eq('gross_zero_cost')]
  self.assertEqual(q.loc[q.period.eq('2023'),'entries'].iloc[0],0)
  self.assertEqual(q.loc[q.period.eq('2022'),'exits'].iloc[0],0)
if __name__=='__main__':unittest.main()

