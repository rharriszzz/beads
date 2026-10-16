"""Read-only full-circuit review, including WSL browser dispatch."""
import argparse,threading
from photo2.r299.serve import make_server,open_browser

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--port',type=int,default=8306);ap.add_argument('--no-browser',action='store_true');a=ap.parse_args()
    try:s=make_server(a.port)
    except OSError:s=make_server(0)
    url=f'http://127.0.0.1:{s.server_port}/photo2/r306/results/campaign/review/'
    print('R306 review: '+url,flush=True)
    if not a.no_browser:threading.Timer(.4,open_browser,args=[url]).start()
    try:s.serve_forever()
    except KeyboardInterrupt:pass
    finally:s.server_close()

if __name__=='__main__':main()
