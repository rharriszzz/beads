#!/usr/bin/env python3
from pathlib import Path
import argparse,http.server,os
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8311);a=p.parse_args()
os.chdir(Path(__file__).resolve().parents[3])
server=http.server.ThreadingHTTPServer(('127.0.0.1',a.port),http.server.SimpleHTTPRequestHandler)
print(f'R311 review: http://127.0.0.1:{server.server_port}/photo2/review/r311/index.html',flush=True)
server.serve_forever()
