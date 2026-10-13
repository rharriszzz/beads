"""Exercise real read-only HTTP handlers against archives with no local R266 work."""
import gzip,io,json,tempfile
from pathlib import Path
from unittest.mock import patch
from . import server
from .experiment_r266 import ROOT,OUT,WORK,save


def main():
    checks=[]
    with tempfile.TemporaryDirectory(prefix='r266-archive-') as temp:
        root=Path(temp);(root/'photo2/review').mkdir(parents=True);(root/'photo2/review/r266').symlink_to(OUT,target_is_directory=True)
        with patch.object(server,'ROOT',root),patch.object(server,'ThreadingHTTPServer',lambda address,handler:handler):
            Handler=server.make_server(ROOT/'photo2/output/r265-first-dark/joint')
            def get(path):
                obj=Handler.__new__(Handler);obj.path=path;obj.wfile=io.BytesIO();codes=[]
                obj.send_response=lambda code:codes.append(code);obj.send_header=lambda *args:None;obj.end_headers=lambda:None;obj.send_error=lambda code:codes.append(code)
                obj.do_GET();assert codes==[200],(path,codes);checks.append(path);return obj.wfile.getvalue()
            names=json.loads(get('/r266-runs.json'));assert len(names)==25
            for name in ('straight-0','annular-3','straight-0-joint6','annular-0-selected12','straight-0-selected6','annular-0-selected3'):
                data=json.loads(get(f'/r266-data/{name}/regions.json'))
                assert data['generation_id']==json.loads((WORK/name/'regions.json').read_text())['generation_id']
                for group in ('regions','suppressed','deferred'):
                    if not data.get(group):continue
                    r=data[group][0];body=get(f'/r266-data/{name}/traces/{r["id"]}.json')
                    assert body==gzip.decompress((WORK/name/r['trace_file']).read_bytes())
                assert get(f'/r266-data/{name}/coordinates.csv')==(WORK/name/'coordinates.csv').read_bytes()
    save(OUT/'archive-handler-checks.json',dict(status='passed',checks=checks,count=len(checks),note='Real handler called without sockets; temporary root excludes every ignored R266 output. Payloads equal local files.'))
    print('PASS',len(checks),'archive handler requests')
if __name__=='__main__':main()
