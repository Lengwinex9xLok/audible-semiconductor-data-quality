import json
import threading
import csv
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

import html_dashboard as dashboard
from quote_universe import SYMBOLS


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = dashboard.ThreadingHTTPServer(('127.0.0.1', 0), dashboard.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get_json(self, path):
        with urlopen(self.url + path, timeout=3) as response:
            self.assertEqual(response.headers['Cache-Control'], 'no-store')
            return json.load(response)

    def test_historical_results_match_research_evidence(self):
        rows = self.get_json('/api/historical')['rows']
        self.assertEqual(len(rows), 140)
        row = next(r for r in rows if r['period'] == 'All' and r['level'] == 'Sample' and r['item'] == 'All 20')
        self.assertAlmostEqual(float(row['rule_return_pct']), 46.993897694, places=6)
        self.assertAlmostEqual(float(row['buy_hold_return_pct']), 92.649689524, places=6)

    def test_saved_quote_coverage_and_snapshot_status(self):
        # Fictional rows check the endpoint without publishing provider records.
        from pathlib import Path
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'quotes.csv'
            with path.open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['symbol', 'quote_date', 'retrieved_at_utc'])
                writer.writeheader()
                writer.writerows({'symbol': symbol, 'quote_date': '2000-01-01',
                                  'retrieved_at_utc': '2000-01-01T00:00:00Z'} for symbol in SYMBOLS)
            with patch.object(dashboard, 'QUOTES', path):
                response = self.get_json('/api/quotes')
        self.assertEqual({r['symbol'] for r in response['rows']}, set(SYMBOLS))
        self.assertEqual(response['status']['mode'], 'snapshot')

    def test_only_explicit_assets_are_served(self):
        with urlopen(self.url + '/', timeout=3) as response:
            self.assertEqual(response.status, 200)
            self.assertIn("default-src 'self'", response.headers['Content-Security-Policy'])
        with self.assertRaises(HTTPError) as ctx:
            urlopen(self.url + '/html_dashboard.py', timeout=3)
        self.assertEqual(ctx.exception.code, 404)


if __name__ == '__main__':
    unittest.main()
