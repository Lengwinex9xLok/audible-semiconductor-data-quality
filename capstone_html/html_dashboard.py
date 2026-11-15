"""Local, read-only capstone dashboard; no brokerage or trading functions."""
import argparse
import csv
import json
import os
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


def quote_worker(key):
    import twelvedata_refresh
    while True:
        with LOCK:
            STATUS.update(mode='refreshing', message='Fetching the 20-symbol snapshot. The previous snapshot remains visible until all requests succeed.')
        try:
            timestamp = twelvedata_refresh.refresh(key, QUOTES)
            with LOCK:
                STATUS.update(mode='connected', message='Last complete refresh: ' + timestamp + '. The next cycle begins after one hour.')
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
                rows = read_csv(HISTORY if path.endswith('historical') else QUOTES)
                with LOCK:
                    status = dict(STATUS)
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
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    key = os.environ.get('TWELVE_DATA_API_KEY', '').strip()
    if key and not args.no_refresh:
        threading.Thread(target=quote_worker, args=(key,), daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}/'
    print('Dashboard:', url, flush=True)
    print('Automatic quotes:', 'enabled' if key and not args.no_refresh else 'off; using saved snapshot', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
