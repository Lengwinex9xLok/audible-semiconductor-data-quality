"""Replay gross-only CIZ results from immutable saved inputs; no network access."""
from pathlib import Path
import argparse,hashlib,json,runpy,sys
import pandas as pd
from ciz_aggregation import gross_only_evaluate
def main(root):
    root=Path(root).resolve()
    manifest=json.loads((root/'ciz_manifest.json').read_text())
    for rel,expected in manifest['input_hashes'].items():
        assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==expected,rel
    core=runpy.run_path(str(Path(__file__).parent/'benchmark_core_v02.py'))
    core={**core,'COST_CASES':{'gross_zero_cost':0.0}}
    d=pd.read_csv(root/'stock_daily.csv')
    cal=pd.read_csv(root/'raw/calendar.csv').trading_date
    tables=gross_only_evaluate(d,cal,core)
    for name,t in zip(manifest['outputs'],tables):
        saved=pd.read_csv(root/'gross_results'/name,dtype={'period':str})
        pd.testing.assert_frame_equal(t.reset_index(drop=True),saved.reset_index(drop=True),check_dtype=False,atol=1e-12,rtol=0)
    print(json.dumps({'status':'gross_replay_passed','network_queries':False,'files_written':False,'tables':len(tables)}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True)
    main(p.parse_args().run_root)
