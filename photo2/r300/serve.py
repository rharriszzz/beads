"""R300 entry with the intact R299/R298 debugger available locally and offline."""
import argparse
import threading
from photo2.r299.serve import make_server,open_browser

def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8300);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
    try:server=make_server(a.port)
    except OSError:server=make_server(0)
    url=f'http://127.0.0.1:{server.server_port}/photo2/review/r300/'
    print('R300 review: '+url,flush=True)
    if not a.no_browser:threading.Timer(.4,open_browser,args=[url]).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
