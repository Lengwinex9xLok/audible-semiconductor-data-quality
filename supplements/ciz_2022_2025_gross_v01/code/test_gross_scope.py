import unittest,runpy
from pathlib import Path
import numpy as np
from ciz_aggregation import expanded_evaluate,gross_only_evaluate
from test_expansion import fixture
CORE=runpy.run_path(str(Path(__file__).parent/'benchmark_core_v02.py'))
class GrossScopeTests(unittest.TestCase):
    def test_gross_matches_original_on_clean_data(self):
        from expansion_core import expanded_evaluate as strict
        d,c=fixture();g={**CORE,'COST_CASES':{'gross_zero_cost':0.0}}
        a=gross_only_evaluate(d,c,g);b=strict(d,c,g)
        import pandas as pd
        for x,y in zip(a,b):pd.testing.assert_frame_equal(x,y)
    def test_crossed_gross_does_not_change_return(self):
        d,c=fixture();g={**CORE,'COST_CASES':{'gross_zero_cost':0.0}}
        baseline=gross_only_evaluate(d,c,g)[0]
        d.loc[1,'bid']=102.
        changed=gross_only_evaluate(d,c,g)
        np.testing.assert_allclose(baseline.cumulative_return,changed[0].cumulative_return,atol=1e-12,rtol=0)
        self.assertGreater(changed[-1].cost_required.sum(),0)
    def test_net_with_crossed_still_rejected(self):
        d,c=fixture();d.loc[1,'bid']=102.
        with self.assertRaisesRegex(ValueError,'Crossed quote'):expanded_evaluate(d,c,CORE)
    def test_gross_entry_point_rejects_cost_mode(self):
        d,c=fixture()
        with self.assertRaisesRegex(ValueError,'gross only'):gross_only_evaluate(d,c,CORE)
if __name__=='__main__':unittest.main()
