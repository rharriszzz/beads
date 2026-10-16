"""One-command localhost review, including WSL's Windows browser opener."""
import argparse
import functools
import http.server
import shutil
import subprocess
import threading
import webbrowser
from photo2.r297.common import ROOT

def open_browser(url):
    if shutil.which('powershell.exe'):
        subprocess.Popen(['powershell.exe','-NoProfile','-NonInteractive','-Command',f"Start-Process '{url}'"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    elif shutil.which('wslview'):
        subprocess.Popen(['wslview',url],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    else:webbrowser.open(url,new=2)

def make_server(port):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    return http.server.ThreadingHTTPServer(('127.0.0.1',port),functools.partial(Handler,directory=str(ROOT)))
def main():
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8298);p.add_argument('--no-browser',action='store_true');a=p.parse_args()
    try:server=make_server(a.port)
    except OSError:server=make_server(0)
    url=f'http://127.0.0.1:{server.server_port}/photo2/review/r298/'
    print('R298 review: '+url,flush=True);print('Ctrl+C stops this review server.',flush=True)
    if not a.no_browser:threading.Timer(.4,open_browser,args=[url]).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
