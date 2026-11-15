import csv
import tempfile
import unittest
from pathlib import Path

import twelvedata_refresh as quotes


def fake_quote(symbol, key):
    return {"symbol": symbol, "exchange": "TEST", "currency": "USD",
            "quote_date": "2000-01-03", "bar_open_unix": 1,
            "last_quote_unix": 2, "close": "100.00", "is_market_open": False,
            "source": "Twelve Data"}


class RefreshTests(unittest.TestCase):
    def test_success_writes_all_symbols_and_retrieval_time(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "quotes.csv"
            waits = []
            retrieved = quotes.refresh("dummy", target, fake_quote, waits.append)
            with target.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([row["symbol"] for row in rows], list(quotes.SYMBOLS))
            self.assertTrue(all(row["retrieved_at_utc"] for row in rows))
            self.assertEqual(waits, [quotes.REQUEST_SPACING_SECONDS] * (len(quotes.SYMBOLS) - 1))
            self.assertGreaterEqual(retrieved, rows[-1]["retrieved_at_utc"])

    def test_failure_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "quotes.csv"
            target.write_bytes(b"previous")
            def fail(symbol, key):
                if symbol == "MSFT":
                    raise ValueError("test error")
                return fake_quote(symbol, key)
            with self.assertRaises(ValueError):
                quotes.refresh("dummy", target, fail, lambda _: None)
            self.assertEqual(target.read_bytes(), b"previous")


if __name__ == "__main__":
    unittest.main()
