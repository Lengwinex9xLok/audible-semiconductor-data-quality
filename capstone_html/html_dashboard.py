"""Local, read-only capstone dashboard; no brokerage or trading functions."""
import argparse
import csv
import json
import os
import sys
from pathlib import Path
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import webbrowser

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'audible_html'
HISTORY = ROOT / 'powerbi_cross_industry_20_gross_2022_2025.csv'
QUOTES = ROOT / 'twelvedata_quotes_latest.csv'
STATUS = {'mode': 'snapshot', 'message': 'Showing the last saved snapshot. Automatic collection is off.'}
LOCK = threading.Lock()


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def refresh_quotes(key):
    import twelvedata_refresh
    with LOCK:
        STATUS.update(mode='refreshing', message='Fetching the 20-symbol snapshot. The previous snapshot remains visible until all requests succeed.')
    timestamp = twelvedata_refresh.refresh(key, QUOTES)
    with LOCK:
        STATUS.update(mode='connected', message='Last complete refresh: ' + timestamp + '. The next cycle begins after one hour.')
    return timestamp


def quote_worker(key, wait_before_first=False):
    if wait_before_first:
        time.sleep(3600)
    while True:
        try:
            refresh_quotes(key)
        except Exception:
            # Do not expose errors or URLs that might contain credentials.
            with LOCK:
                STATUS.update(mode='error', message='Refresh failed. Showing the last complete saved snapshot, if available.')
        time.sleep(3600)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path in ('/api/historical', '/api/quotes'):
            try:
                if path.endswith('quotes') and not QUOTES.exists():
                    rows = []
                else:
                    rows = read_csv(HISTORY if path.endswith('historical') else QUOTES)
                with LOCK:
                    status = dict(STATUS)
                if path.endswith('quotes') and not rows and status['mode'] == 'snapshot':
                    status['message'] = 'No saved quotes. Automatic collection is off; configure a key for fresh quotes.'
                body = json.dumps({'rows': rows, 'status': status}, allow_nan=False).encode('utf-8')
                self.send_payload(200, 'application/json; charset=utf-8', body)
            except (OSError, ValueError):
                self.send_payload(503, 'application/json; charset=utf-8', b'{"error":"Data file unavailable"}')
            return
        files = {'/': ('index.html', 'text/html; charset=utf-8'),
                 '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                 '/styles.css': ('styles.css', 'text/css; charset=utf-8')}
        if path not in files:
            self.send_error(404)
            return
        filename, mime = files[path]
        try:
            self.send_payload(200, mime, (ASSETS / filename).read_bytes())
        except OSError:
            self.send_error(404)

    def send_payload(self, code, mime, body):
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--no-refresh', action='store_true', help='Use saved quotes only, even if a key is configured')
    parser.add_argument('--require-live', action='store_true', help='Require a key and a successful first complete quote refresh before opening the dashboard')
    args = parser.parse_args()
    key = os.environ.get('TWELVE_DATA_API_KEY', '').strip()
    if args.require_live and args.no_refresh:
        parser.error('--require-live cannot be combined with --no-refresh')
    if args.require_live and not key:
        parser.error('--require-live needs TWELVE_DATA_API_KEY to be configured before launch')
    required = [HISTORY, ASSETS / 'index.html', ASSETS / 'app.js', ASSETS / 'styles.css']
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        parser.error('missing required project files: ' + ', '.join(missing))
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    try:
        if args.require_live:
            print('Fetching all 20 quotes before opening the dashboard; this can take several minutes.', flush=True)
            try:
                refresh_quotes(key)
            except Exception:
                print('Initial quote refresh failed; the dashboard was not started. Check the key, connection, and provider limits.', file=sys.stderr, flush=True)
                return 1
        if key and not args.no_refresh:
            threading.Thread(target=quote_worker, args=(key, args.require_live), daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/'
        print('Dashboard:', url, flush=True)
        print('Automatic quotes:', 'enabled' if key and not args.no_refresh else 'off; using saved snapshot', flush=True)
        if not args.no_browser:
            webbrowser.open(url)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
