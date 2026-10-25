"""Isolation and handoff behavior, using fictional rows only."""
import json
import pandas as pd
import pytest
import run_audible as app
from src.common import config
from src.stocks.pull import TABLES, data_root
from src.stocks.history_audit import run
from tests.stocks.test_history_audit import fixture_data, EvidenceDB, START, END

class IdentityDB:
    def __init__(self, ambiguous=False):
        self.closed=False
        self.ambiguous=ambiguous
    def raw_sql(self, query):
        if 'limit 0' in query.lower():
            table=next(k for k in TABLES if 'crsp.'+k in query.lower())
            return pd.DataFrame(columns=TABLES[table])
        rows=[dict(permno=100+i,ticker=t,namedt='2000-01-01',nameenddt=None,shrcd=11)
              for i,t in enumerate(config.load_universe())]
        if self.ambiguous:
            rows.append({**rows[0],'permno':9999})
        return pd.DataFrame(rows)
    def close(self):
        self.closed=True

def test_old_group_environment_cannot_redirect_defaults(monkeypatch,tmp_path):
    monkeypatch.setenv('STOCKS_DATA_ROOT',str(tmp_path/'original-group'))
    monkeypatch.delenv('AUDIBLE_DATA_ROOT',raising=False)
    assert data_root()==app.independent_data_root()
    assert len(app.load_settings())>0
    assert len(config.load_universe())==10

def test_identity_checks_all_ten_and_closes_connection(monkeypatch,tmp_path):
    monkeypatch.setattr(app,'independent_data_root',lambda:tmp_path)
    db=IdentityDB()
    folder,resolved=app.identity_check(lambda:db)
    assert db.closed
    assert set(resolved.pilot_ticker)==set(config.load_universe())
    assert json.loads((folder/'manifest.json').read_text())['universe_asof']=='2024-12-31'
    assert len(list(tmp_path.glob('identity_checks/*/resolved.csv')))==1

def test_identity_ambiguity_keeps_failure_and_no_success(monkeypatch,tmp_path):
    monkeypatch.setattr(app,'independent_data_root',lambda:tmp_path)
    db=IdentityDB(ambiguous=True)
    with pytest.raises(ValueError,match='Human review required'):
        app.identity_check(lambda:db)
    assert db.closed
    assert len(list(tmp_path.glob('identity_checks/*/failure.json')))==1
    assert not list(tmp_path.glob('identity_checks/*/manifest.json'))

def prepare_bundle(monkeypatch,tmp_path):
    processed=fixture_data(tmp_path)
    audit,_=run(tmp_path,START,END,'fictional',connect_factory=EvidenceDB)
    monkeypatch.setattr(app,'independent_data_root',lambda:tmp_path)
    monkeypatch.setattr(app,'load_settings',lambda:dict(start=START,end=END,
        sample_start=START,sample_end=END,universe_asof=END))
    return processed,audit

def test_summary_rejects_different_stock_sample(monkeypatch,tmp_path):
    _,audit=prepare_bundle(monkeypatch,tmp_path)
    with pytest.raises(ValueError,match='different stock sample'):
        app.summary_bundle(audit)
    assert not (tmp_path/'dashboard_handoffs').exists()

def test_verified_summary_handoff_excludes_raw_and_rejects_tamper(monkeypatch,tmp_path):
    _,audit=prepare_bundle(monkeypatch,tmp_path)
    monkeypatch.setattr(config,'load_universe',lambda:['TEST'])
    folder=app.summary_bundle(audit)
    assert {p.name for p in folder.iterdir()}=={
        'quote_sensitivity.csv','coverage_by_security.csv','coverage.csv',
        'quality_summary.json','handoff_manifest.json'}
    assert json.loads((folder/'handoff_manifest.json').read_text())['row_level_prices_included'] is False
    with (audit/'quote_sensitivity.csv').open('a') as f:
        f.write('\nTAMPERED\n')
    with pytest.raises(ValueError,match='Audit output changed'):
        app.summary_bundle(audit)

def test_summary_cannot_read_external_group_root(tmp_path):
    with pytest.raises(ValueError,match='independent Audible data root'):
        app.summary_bundle(tmp_path/'original-group')
