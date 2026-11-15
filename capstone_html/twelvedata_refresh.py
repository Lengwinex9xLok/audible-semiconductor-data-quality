"""Refresh a Power BI CSV from Twelve Data. No trading or order functionality."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import getpass
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

from quote_universe import SYMBOLS

FIELDS = ("symbol", "exchange", "currency", "quote_date", "bar_open_unix",
          "last_quote_unix", "close", "is_market_open", "source", "retrieved_at_utc")
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "twelvedata_quotes_latest.csv"
REQUEST_SPACING_SECONDS = 12


def fetch(symbol, key):
    query = urllib.parse.urlencode({"symbol": symbol})
    req = urllib.request.Request("https://api.twelvedata.com/quote?" + query,
                                 headers={"Authorization": "apikey " + key})
    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.load(response)
    if not isinstance(data, dict) or data.get("status") == "error" or data.get("code"):
        raise ValueError("API returned an error")
    if data.get("symbol") != symbol or not data.get("datetime"):
        raise ValueError("missing or mismatched symbol/date")
    try:
        price = Decimal(str(data["close"]))
        datetime.strptime(data["datetime"][:10], "%Y-%m-%d")
        if not price.is_finite() or price <= 0:
            raise ValueError("invalid close")
    except (KeyError, InvalidOperation, TypeError) as exc:
        raise ValueError("missing or invalid close/date") from exc
    if not data.get("exchange") or data.get("currency") != "USD":
        raise ValueError("missing exchange or unexpected currency")
    return {"symbol": symbol, "exchange": data["exchange"], "currency": data["currency"],
            "quote_date": data["datetime"][:10], "bar_open_unix": data.get("timestamp"),
            "last_quote_unix": data.get("last_quote_at"), "close": str(price),
            "is_market_open": data.get("is_market_open"), "source": "Twelve Data"}


def refresh(key, output, fetcher=fetch, sleeper=time.sleep, progress=None):
    rows = []
    for index, symbol in enumerate(SYMBOLS):
        if index:
            sleeper(REQUEST_SPACING_SECONDS)
        if progress is not None:
            progress(index + 1, len(SYMBOLS), symbol)
        try:
            row = fetcher(symbol, key)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"quote unavailable for {symbol} ({type(exc).__name__})") from exc
        row["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rows.append(row)
    retrieved = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output = Path(output)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8-sig", newline="", delete=False,
                                         dir=output.parent, prefix=".quotes_", suffix=".tmp") as f:
            tmp_path = Path(f.name)
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        os.replace(tmp_path, output)
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()
    return retrieved


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true", help="Refresh once, then exit")
    parser.add_argument("--interval", type=int, default=3600, help="Seconds to wait after each full refresh (minimum 3600; default 3600)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.interval < 3600:
        parser.error("interval must be at least 3600 seconds")
    key = os.environ.get("TWELVE_DATA_API_KEY")
    if not key:
        if not sys.stdin.isatty():
            print("TWELVE_DATA_API_KEY is required for noninteractive use.", file=sys.stderr)
            return 2
        key = getpass.getpass("Twelve Data API key: ")
    if not key.strip():
        print("No API key provided.", file=sys.stderr)
        return 2
    while True:
        try:
            updated = refresh(key, args.output, progress=lambda n, total, symbol:
                              print(f"Fetching {n}/{total}: {symbol}", flush=True))
            print(f"Saved {len(SYMBOLS)} quotes at {updated}: {args.output}", flush=True)
        except (urllib.error.URLError, TimeoutError, ValueError, OSError, json.JSONDecodeError) as exc:
            print(f"Refresh failed: {exc}; previous CSV was not replaced.", file=sys.stderr, flush=True)
            if args.once:
                return 1
        if args.once:
            return 0
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("Stopped.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
