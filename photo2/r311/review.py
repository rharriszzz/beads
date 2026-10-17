"""Offline photographic/geographic review; raw and annotation canvases separate."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image
from photo2.r297.common import ROOT,read,save

def build(out,models,metrics):
    out=Path(out);dest=ROOT/'photo2/review/r311';dest.mkdir(parents=True,exist_ok=True)
    package=[]
    for m in models:
        raster=np.load(out/'exports'/f"{m['name']}-raster.npz")
        enc=raster['address'].astype(np.int32)+32768
        rgb=np.zeros((*enc.shape,3),np.uint8);rgb[:,:,0]=enc%256;rgb[:,:,1]=enc//256
        Image.fromarray(rgb).save(dest/f"{m['name']}-owners.png")
        record=dict(name=m['name'],family=m['family'],baseline=m['baseline'],parameters=m['parameters'],
                            positions=m['positions'],first_errors=m['first_errors'],metrics=metrics[m['name']]['overall'],
                            fixed=metrics[m['name']]['fixed']['overall'],physical={k:v for k,v in m['physical'].items() if k!='witnesses'},
                            reflections=[r for r in metrics[m['name']]['detail']['development']['reflections']+metrics[m['name']]['detail']['comparison']['reflections']],
                            all_observations=m['all_observations'])
        (dest/f"{m['name']}.js").write_text('window.R311LoadedModel='+json.dumps(record,separators=(',',':'))+';\n')
        package.append(dict(name=m['name'],family=m['family'],baseline=m['baseline']))
    # Data as a local script supports file:// review without fetch/CORS exceptions.
    (dest/'data.js').write_text('window.R311='+json.dumps(dict(models=package,D=read(out/'D.json')['D_px']),separators=(',',':'))+';\n')
    src=ROOT/'photo2/r311/viewer.html';shutil.copyfile(src,dest/'index.html')
    links=[]
    for a,b in __import__('photo2.r311.model',fromlist=['PAIRS']).PAIRS:links.append(f'response-{a}-{b}.png')
    links+=['multivariate.png','basin-multivariate.png','local-global-tradeoff.png','predicted-measured.png','whole-circuit-reflections.png','regional-outcomes.png']
    audit=out.parent/'audit'
    for p in audit.glob('*.png'):shutil.copyfile(p,dest/p.name);links.append(p.name)
    html='<html><meta name="viewport" content="width=device-width"><title>R311 sampled response maps</title><style>body{font:16px sans-serif;margin:20px}img{max-width:100%;height:auto}</style><h1>R311 sampled response maps</h1><p>Blank cells are unevaluated. Red crosses witness penetration; orange question marks are unresolved separation; grey diamonds are numerical/bounds rejections. Colored score cells are complete certified feasible necklaces. Projected ranges do not imply uniform joint coverage.</p><p><a href="index.html">Photographic review</a> · <a href="../../R311_REPORT.md">Report</a></p>'
    for name in links:html+=f'<h2>{name}</h2><a href="{name}"><img src="{name}" alt="{name}"></a>'
    (dest/'maps.html').write_text(html+'</html>')
    (dest/'serve.py').write_text('''#!/usr/bin/env python3
from pathlib import Path
import argparse,http.server,os
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8311);a=p.parse_args()
os.chdir(Path(__file__).resolve().parents[3])
server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),http.server.SimpleHTTPRequestHandler)
print(f'R311 review: http://127.0.0.1:{server.server_port}/photo2/review/r311/index.html',flush=True)
server.serve_forever()
''')
    (dest/'launch.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
R311_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$R311_ROOT"
exec .venv/bin/python photo2/review/r311/serve.py "$@"
''')
    (dest/'launch.sh').chmod(0o755)
    save(out/'review-links.json',dict(images=links,raw='photo.png',viewer='index.html',maps='maps.html'))
