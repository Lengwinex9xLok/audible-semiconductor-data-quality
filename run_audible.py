"""Independent Audible plan, identity check and verified summary handoff."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import shutil
import uuid

from src.common import config
from src.common.io_utils import sql_list
from src.common.wrds_conn import connect
from src.stocks.pull import preflight, resolve_seeds, sha256, window
from src.stocks.history_audit import load_inputs

ROOT = Path(__file__).resolve().parent


def load_settings():
    settings = json.loads((ROOT / 'config/audible.json').read_text(encoding='utf-8'))
    window(settings['start'], settings['end'])
    window(settings['sample_start'], settings['sample_end'])
    window(settings['universe_asof'], settings['universe_asof'])
    tickers = config.load_universe()
    if len(tickers) != 10:
        raise ValueError('This Audible configuration requires exactly ten distinct labels')
    sql_list(tickers)
    return settings


def independent_data_root():
    # Recommended workflow never inherits the group's environment/data location.
    return (ROOT / 'data' / 'semiconductors').resolve()


def fresh_name(prefix):
    return prefix + '_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8]


def identity_check(connect_factory=None):
    settings = load_settings()
    labels = config.load_universe()
    folder = independent_data_root() / 'identity_checks' / fresh_name('identity')
    folder.mkdir(parents=True, exist_ok=False)
    db = None
    query = ('select permno, ticker, namedt, nameenddt, shrcd from crsp.stocknames '
             f'where ticker in {sql_list(labels)}')
    try:
        db = (connect_factory or connect)()
        schemas = preflight(db)
        seed = db.raw_sql(query)
        seed.to_csv(folder / 'seed_names.csv', index=False)
        resolved = resolve_seeds(seed, labels, as_of=settings['universe_asof'])
        resolved.to_csv(folder / 'resolved.csv', index=False)
        record = dict(status='complete', created_at_utc=datetime.now(timezone.utc).isoformat(),
                      universe_asof=settings['universe_asof'], labels=labels, query=query,
                      schemas=schemas, universe_sha256=sha256(ROOT/'config/universe.csv'),
                      files={n:sha256(folder/n) for n in ['seed_names.csv','resolved.csv']})
        (folder/'manifest.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
        return folder, resolved
    except BaseException as exc:
        (folder/'failure.json').write_text(json.dumps(dict(status='incomplete',
            error_type=type(exc).__name__,message=str(exc)),indent=2),encoding='utf-8')
        raise
    finally:
        if db is not None:
            db.close()


def summary_bundle(audit_dir):
    settings = load_settings()
    root = independent_data_root()
    audit = Path(audit_dir).resolve()
    try:
        audit.relative_to(root / 'processed' / 'stocks')
    except ValueError:
        raise ValueError('Audit must be inside this independent Audible data root') from None
    manifest = json.loads((audit/'audit_manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') != 'complete':
        raise ValueError('A completed audit is required')
    start, end = manifest['window']
    allowed_windows = [(settings['start'], settings['end']),
                       (settings['sample_start'], settings['sample_end'])]
    if (start, end) not in allowed_windows:
        raise ValueError('Audit window does not match the Audible configuration')
    processed, daily, pilot, _, raw_manifest = load_inputs(root, start, end)
    if audit.parent != processed / 'repro_audits':
        raise ValueError('Audit path does not match its manifest window')
    if sorted(pilot['pilot_ticker'].tolist()) != sorted(config.load_universe()):
        raise ValueError('Audit belongs to a different stock sample')
    if raw_manifest.get('universe_asof') != settings['universe_asof']:
        raise ValueError('Raw identity anchor does not match the Audible configuration')
    if manifest['source_sha256'] != sha256(processed/'stock_daily.csv'):
        raise ValueError('Audit source has changed')
    files = ['quote_sensitivity.csv','coverage_by_security.csv','quality_summary.json']
    for name in files:
        if sha256(audit/name) != manifest['outputs'][name]['sha256']:
            raise ValueError(f'Audit output changed: {name}')
    summary = json.loads((audit/'quality_summary.json').read_text(encoding='utf-8'))
    if summary['rows'] != len(daily) or summary['securities'] != len(pilot):
        raise ValueError('Summary counts do not match the verified source')
    destination = root/'dashboard_handoffs'/fresh_name('summaries')
    destination.mkdir(parents=True,exist_ok=False)
    hashes = {}
    for name in files:
        shutil.copyfile(audit/name,destination/name)
        hashes[name] = sha256(destination/name)
    # coverage.csv is a saved build aggregate. Verify it against unchanged daily flags.
    import pandas as pd
    coverage = pd.read_csv(processed/'coverage.csv')
    for row in coverage.itertuples(index=False):
        part = daily[daily['permno'].eq(row.permno)]
        member_count = int(part['in_sp500'].fillna(False).sum())
        if len(part) != row.rows or member_count != row.in_sp500_rows:
            raise ValueError('Saved coverage summary no longer matches source rows')
    if sorted(coverage['pilot_ticker'].tolist()) != sorted(config.load_universe()):
        raise ValueError('Coverage summary belongs to another stock sample')
    shutil.copyfile(processed/'coverage.csv',destination/'coverage.csv')
    hashes['coverage.csv'] = sha256(destination/'coverage.csv')
    handoff = dict(status='complete',data_kind='real_source_derived_summaries',
                   created_at_utc=datetime.now(timezone.utc).isoformat(),window=[start,end],
                   universe_asof=settings['universe_asof'],tickers=config.load_universe(),
                   quality_status=summary['quality_status'],source_sha256=manifest['source_sha256'],
                   audit_manifest_sha256=sha256(audit/'audit_manifest.json'),files=hashes,
                   row_level_prices_included=False,
                   use='Review permitted coursework use before transferring this summary bundle')
    (destination/'handoff_manifest.json').write_text(json.dumps(handoff,indent=2),encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['plan','identity','bundle'])
    parser.add_argument('--audit-dir')
    args = parser.parse_args()
    if args.action == 'plan':
        print(json.dumps(dict(settings=load_settings(),tickers=config.load_universe(),
                             data_root=str(independent_data_root()),
                             connection_opened=False,semiconductor_results='not bundled'),indent=2))
    elif args.action == 'identity':
        if not config.WRDS_USERNAME:
            config.WRDS_USERNAME = input('WRDS username (not password): ').strip()
        folder, resolved = identity_check()
        print(folder)
        print(resolved.to_string(index=False))
    else:
        if not args.audit_dir:
            parser.error('bundle requires --audit-dir')
        print(summary_bundle(args.audit_dir))


if __name__ == '__main__':
    main()
