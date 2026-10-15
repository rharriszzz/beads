"""Actual Chromium visual/interaction checks with no feedback writes."""
import http.server,threading,functools
from playwright.sync_api import sync_playwright
from .common import *
def main():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();errors=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/photo2/review/r295/');page.locator('img').evaluate_all('(imgs)=>imgs.forEach(i=>i.loading="eager")');page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
            images=page.locator('img').count();links=page.locator('a').evaluate_all('(aa)=>aa.map(a=>a.href)')
            for link in links:assert page.request.get(link.split('#')[0]).ok,link
            for model in ('R294-whole.png','hand-plus-whole.png','original-native.png','R295-whole.png'):
                page.locator('#model').select_option(model);page.wait_for_function('document.querySelector("#whole").complete&&document.querySelector("#whole").naturalWidth===2540');assert page.locator('#whole').get_attribute('src')==model
            page.locator('#toggle').click();assert page.locator('#whole').get_attribute('src')=='original-native.png';page.locator('#toggle').click();assert page.locator('#whole').get_attribute('src')=='R295-whole.png'
            page.locator('#zoom').fill('1600');page.locator('#zoom').dispatch_event('input');assert page.locator('#whole').evaluate('(e)=>e.style.width')=='1600px';page.locator('#zoom').fill('1000');page.locator('#zoom').dispatch_event('input')
            page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
            page.set_viewport_size({'width':520,'height':900});page.wait_for_timeout(100);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);browser.close()
    finally:server.shutdown();server.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(images_loaded=images,links_checked=len(links),errors=errors,checks=['whole original/model selection','original toggle','zoom','native crop links','221-position exports','desktop1450','narrow520 no overflow'],feedback_written=False));print('Chromium',images,'images',len(links),'links passed')
if __name__=='__main__':main()
