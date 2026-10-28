"""Focused validation regressions and one hand-derived portfolio example."""

from pathlib import Path
import unittest
from unittest.mock import patch

from cost_replay.accounting import Sleeve, portfolio_return, require_close
from cost_replay.inputs import CONVENTION, load_reference_cases


class ReplayValidation(unittest.TestCase):
    def test_nonfinite_expected_values_are_rejected(self):
        # abs(finite - NaN) > tolerance is False, so check finiteness explicitly.
        for expected in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(expected=expected):
                with self.assertRaises(ValueError):
                    require_close(1.0, expected, 'reference')

    def test_nonfinite_actual_values_are_rejected(self):
        for actual in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(actual=actual):
                with self.assertRaises(ValueError):
                    require_close(actual, 1.0, 'calculation')

    def test_weighted_portfolio_has_a_hand_derived_return(self):
        sleeves = [Sleeve(0.25, [100.0, 200.0], [1]),
                   Sleeve(0.75, [100.0, 50.0], [0])]
        self.assertEqual(portfolio_return(sleeves, 0, active=True), (0.25, 1, 1))
        self.assertEqual(portfolio_return(sleeves, 0, active=False), (-0.125, 2, 2))

    def reference_rows(self):
        return [dict(period='2025', convention=CONVENTION, one_way_bps=bps,
                     net_public=0.1, net_matched_passive=0.2,
                     net_gap=-0.1, extra_drag=0.0)
                for bps in [0, 0.5, 1, 2]]

    def test_nonfinite_reference_csv_values_are_rejected(self):
        rows = self.reference_rows()
        rows[0]['net_gap'] = 'nan'
        with patch('cost_replay.inputs.read_csv', return_value=rows):
            with self.assertRaisesRegex(ValueError, 'must be finite'):
                load_reference_cases(Path('cases.csv'))

    def test_duplicate_published_cases_are_rejected(self):
        rows = self.reference_rows()
        rows[-1]['one_way_bps'] = rows[0]['one_way_bps']
        with patch('cost_replay.inputs.read_csv', return_value=rows):
            with self.assertRaisesRegex(ValueError, 'four distinct'):
                load_reference_cases(Path('cases.csv'))

    def test_unrelated_experiment_convention_is_rejected(self):
        rows = self.reference_rows()
        rows[0]['convention'] = 'continuous_four_year'
        with patch('cost_replay.inputs.read_csv', return_value=rows):
            with self.assertRaisesRegex(ValueError, 'experiment convention'):
                load_reference_cases(Path('cases.csv'))


if __name__ == '__main__':
    unittest.main()
