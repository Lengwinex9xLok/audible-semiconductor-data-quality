import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from replay_wrds import build_table, check_manifest, compare_tables, digest


class ReplayChecks(unittest.TestCase):
    def reference(self):
        return pd.DataFrame([{'period': 'All', 'level': 'Stock', 'item': f'T{i}',
                              'rule_return_pct': float(i), 'buy_hold_return_pct': float(i + 1),
                              'difference_pp': -1.0} for i in range(140)])

    def test_matching_rows_pass_in_any_order(self):
        expected = self.reference()
        self.assertEqual(compare_tables(expected.iloc[::-1], expected), 0.0)

    def test_changed_number_fails(self):
        expected = self.reference()
        changed = expected.copy()
        changed.loc[0, 'rule_return_pct'] += 0.01
        with self.assertRaises(AssertionError):
            compare_tables(changed, expected)

    def test_missing_row_fails(self):
        expected = self.reference()
        with self.assertRaises(ValueError):
            compare_tables(expected.iloc[:-1], expected)

    def test_manifest_rejects_modified_file_and_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            item = directory / 'synthetic.txt'
            item.write_text('fictional', encoding='utf-8')
            check_manifest(directory, {'files': {'synthetic.txt': {'sha256': digest(item)}}})
            with self.assertRaises(ValueError):
                check_manifest(directory, {'files': {'synthetic.txt': {'sha256': 'incorrect'}}})
            with self.assertRaises(ValueError):
                check_manifest(directory, {'files': {'../outside': {'sha256': 'unused'}}})

    def test_build_table_uses_separate_sample_and_stock_results(self):
        daily = pd.DataFrame({'pilot_ticker': ['A', 'B']})
        def aggregate(group, calendar, core):
            count = len(group)
            summary = pd.DataFrame([{'period': 'All', 'strategy': name, 'cumulative_return': value}
                                    for name, value in [('lagged_positive_return', count / 100), ('always_long', count / 50)]])
            detail = pd.DataFrame([{'period': 'All', 'ticker': ticker, 'strategy': name, 'cumulative_return': value}
                                   for ticker in group.pilot_ticker
                                   for name, value in [('lagged_positive_return', .03), ('always_long', .04)]])
            return (summary, None, detail)
        report, _ = build_table(daily, None, None, aggregate, {'All 20': ['A', 'B'], 'A only': ['A']})
        self.assertEqual(len(report), 4)
        self.assertEqual(report.loc[report.item.eq('All 20'), 'rule_return_pct'].iloc[0], 2.0)
        self.assertEqual(report.loc[report.item.eq('A'), 'rule_return_pct'].iloc[0], 3.0)


if __name__ == '__main__':
    unittest.main()
