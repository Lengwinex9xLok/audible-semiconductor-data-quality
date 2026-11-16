import unittest

import pandas as pd

from check_invested_share import verify_shares


class InvestedShareChecks(unittest.TestCase):
    def synthetic(self):
        dates = pd.date_range('2022-01-01', periods=5)
        daily = pd.DataFrame([
            {'permno': i, 'date': date, 'ret': (1 if i % 2 else -1)}
            for i in range(20) for date in dates
        ])
        paths, summaries = [], []
        for strategy, share in [('lagged_positive_return', .5), ('always_long', 1.)]:
            summaries.append({'period': 'All', 'strategy': strategy, 'cost_case': 'gross_zero_cost',
                              'average_invested_sleeve_share': share})
            paths.append({'period': 'All', 'strategy': strategy, 'cost_case': 'gross_zero_cost',
                          'date': dates[1].strftime('%Y-%m-%d'), 'is_initial': 1,
                          'invested_sleeve_share': 0.0})
            paths.extend({'period': 'All', 'strategy': strategy, 'cost_case': 'gross_zero_cost',
                          'date': date.strftime('%Y-%m-%d'), 'is_initial': 0,
                          'invested_sleeve_share': share} for date in dates[2:])
        return daily, dates, (pd.DataFrame(summaries), pd.DataFrame(paths))

    def test_mean_excludes_initial_row(self):
        daily, dates, result = self.synthetic()
        checked = verify_shares(daily, dates, result)
        self.assertEqual(checked['intervals'], 3)
        self.assertEqual(checked['strategies']['lagged_positive_return']['held_sleeve_intervals'], 30)
        self.assertEqual(checked['strategies']['always_long']['mean_sleeve_share'], 1.)

    def test_rejects_mismatched_share(self):
        daily, dates, result = self.synthetic()
        result[1].loc[1, 'invested_sleeve_share'] = .6
        with self.assertRaises(AssertionError):
            verify_shares(daily, dates, result)


if __name__ == '__main__':
    unittest.main()
