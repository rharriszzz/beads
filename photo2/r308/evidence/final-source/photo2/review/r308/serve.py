#!/usr/bin/env python3
import sys,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from photo2.r299.serve import make_server,open_browser
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8308);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
try:server=make_server(a.port)
except OSError:server=make_server(0)
url=f'http://127.0.0.1:{server.server_port}/photo2/r308/results/campaign/review/'
print('R308 review: '+url,flush=True)
if not a.no_browser:open_browser(url)
try:server.serve_forever()
except KeyboardInterrupt:pass
finally:server.server_close()
