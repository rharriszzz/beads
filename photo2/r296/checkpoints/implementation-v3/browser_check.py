"""Repository-approved Chromium review contract for the delivered pilot."""
import functools
import http.server
import threading
from playwright.sync_api import sync_playwright
from .common import *


def main():
    out=BASE/'results/pilot';review=out/'review';errors=[]
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(out)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/review/')
            page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
            images=page.locator('img').count();links=page.locator('a').evaluate_all('(aa)=>aa.map(a=>a.href)')
            for link in links:assert page.request.get(link).ok,link
            options=page.locator('#model option').evaluate_all('(oo)=>oo.map(o=>o.value)')
            for option in options:
                page.locator('#model').select_option(option)
                page.wait_for_function('document.querySelector("#whole").complete&&document.querySelector("#whole").naturalWidth>0')
                assert page.locator('#whole').get_attribute('src')==option
            page.locator('#toggle').click();assert page.locator('#whole').get_attribute('src')=='original.png'
            page.locator('#toggle').click();assert page.locator('#whole').get_attribute('src')==options[-1]
            page.locator('#zoom').fill('1600');page.locator('#zoom').dispatch_event('input');assert page.locator('#whole').evaluate('(e)=>e.style.width')=='1600px'
            page.locator('#zoom').fill('1100');page.locator('#zoom').dispatch_event('input')
            page.screenshot(path=str(BASE/'results/browser-desktop.png'))
            page.set_viewport_size({'width':520,'height':900});page.wait_for_timeout(100)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(BASE/'results/browser-narrow.png'));browser.close()
    finally:server.shutdown();server.server_close();thread.join()
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(images=images,links=len(links),models=len(options)-1,errors=errors,
        checks=['all images and download links','model selection','original toggle','native zoom','desktop1450','narrow520 no document overflow'],feedback_written=False))
    print('Chromium checks passed',images,'images',len(links),'links')

if __name__=='__main__':main()
