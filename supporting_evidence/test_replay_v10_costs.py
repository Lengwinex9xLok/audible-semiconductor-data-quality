import unittest
from replay_v10_costs import sleeve_wealth

class CashAndShareAccounting(unittest.TestCase):
    def test_flat_round_trip(self):
        path, buys, sells=sleeve_wealth([100.,100.],[1],10)
        self.assertAlmostEqual(path[-1],.999/1.001,14)
        self.assertEqual((buys,sells),(1,1))

    def test_continuing_long_has_one_round_trip(self):
        path, buys, sells=sleeve_wealth([100.,110.,120.],[1,1],10)
        self.assertAlmostEqual(path[-1],1.2*.999/1.001,14)
        self.assertEqual((buys,sells),(1,1))

    def test_cash_ignores_price_changes(self):
        self.assertEqual(sleeve_wealth([100.,10.,200.],[0,0],10),([1.,1.,1.],0,0))

    def test_reentry_pays_two_round_trips(self):
        path, buys, sells=sleeve_wealth([100.,100.,100.,100.],[1,0,1],10)
        self.assertAlmostEqual(path[-1],(.999/1.001)**2,14)
        self.assertEqual((buys,sells),(2,2))

    def test_delayed_entry_excludes_prior_jump(self):
        path, buys, sells=sleeve_wealth([100.,200.,300.],[0,1],10)
        self.assertAlmostEqual(path[-1],1.5*.999/1.001,14)
        self.assertEqual((buys,sells),(1,1))

    def test_zero_cost_matches_hand_example(self):
        path, _, _=sleeve_wealth([100.,110.,55.,60.],[1,0,1],0)
        self.assertAlmostEqual(path[-1],1.2,14)

    def test_invalid_inputs_rejected(self):
        cases=[([1.,0.],[1],1),([1.,float('nan')],[1],1),([1.,2.],[2],1),
               ([1.,2.],[],1),([1.,2.],[1],-1),([1.,2.],[1],10000)]
        for prices,q,bps in cases:
            with self.subTest(prices=prices,q=q,bps=bps):
                with self.assertRaises(ValueError):sleeve_wealth(prices,q,bps)

if __name__=='__main__':unittest.main()
