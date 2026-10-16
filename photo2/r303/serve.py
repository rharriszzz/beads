"""Reuse the read-only R301/R299 localhost launcher."""
import argparse
import threading
from photo2.r299.serve import make_server,open_browser

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8303);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
    try:s=make_server(a.port)
    except OSError:s=make_server(0)
    url=f'http://127.0.0.1:{s.server_port}/photo2/review/r303/'
    print('R303 review: '+url,flush=True)
    if not a.no_browser:threading.Timer(.4,open_browser,args=[url]).start()
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()

if __name__=='__main__':main()
