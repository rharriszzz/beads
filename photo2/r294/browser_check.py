"""Actual Chromium review of the static artifact, desktop and narrow."""
import http.server,threading,functools
from playwright.sync_api import sync_playwright
from .common import *

def main():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    httpd=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
    thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            url=f'http://127.0.0.1:{httpd.server_port}/photo2/review/r294/'
            page.goto(url);page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
            images=page.locator('img').count();links=page.locator('a').evaluate_all('(aa)=>aa.map(a=>a.href)')
            for link in links:assert page.request.get(link).ok,link
            assert images==len(read(REVIEW/'manifest.json')['crops'])+5
            page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
            page.set_viewport_size({'width':520,'height':900});page.wait_for_timeout(100)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);browser.close()
    finally:httpd.shutdown();httpd.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(images_loaded=images,links_checked=len(links),errors=errors,
        checks=['native whole-image links','bead 0 photo','raw/initial/revised crops','desktop1400','narrow520 no overflow'],
        feedback_written=False))
    print('Chromium:',images,'images;',len(links),'links; desktop/narrow passed')
if __name__=='__main__':main()
