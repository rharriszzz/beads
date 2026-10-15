"""Chromium checks for native review, whole-loop navigation and offline debugger."""
import functools
import http.server
import threading
from playwright.sync_api import sync_playwright
from .common import *


def main():
    out=BASE/'results/pilot'
    if not out.exists():out=BASE/'results/ui-smoke'
    errors=[]
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(out)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1100})
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(f'http://127.0.0.1:{server.server_port}/review/')
            page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
            links=page.locator('a').evaluate_all('(aa)=>aa.map(a=>a.href)')
            for link in links:assert page.request.get(link).ok,link
            page.goto(f'http://127.0.0.1:{server.server_port}/review/debug.html')
            page.wait_for_function('document.querySelector("#status").textContent.startsWith("Native location")')
            assert page.locator('#sections tbody tr').count()==32
            for j in range(32):
                page.locator('#sections button').nth(j).click()
                assert 'section '+str(j) in page.locator('#location').inner_text()
            page.locator('#whole').click(position={'x':150,'y':150})
            assert page.locator('#failures tbody tr').count()==25
            page.locator('#failures button').first.click();assert 'measurement' in page.locator('#evidence').inner_text()
            choices=page.locator('#candidate option').evaluate_all('(oo)=>oo.map(o=>o.value)')
            for value in choices:page.locator('#candidate').select_option(value)
            page.locator('#candidate').select_option(choices[0]);page.locator('#support').check()
            page.locator('#width').fill('160');page.locator('#width').dispatch_event('input')
            page.locator('#mechanism').select_option('uncertain-correspondence');assert page.locator('#failures tbody tr').count()>0
            if page.locator('#mechanism option[value="R295-regression"]').count():page.locator('#mechanism').select_option('R295-regression')
            page.locator('#failures button').first.click();page.locator('#local').click()
            assert 'R295' in page.locator('#before-label').inner_text()
            page.screenshot(path=str(BASE/'results/debugger-desktop.png'),full_page=True)
            page.locator('#contacts').click();assert 'lower separation bound' in page.locator('#evidence').inner_text()
            page.locator('#seam').click();assert 'topology' in page.locator('#evidence').inner_text()
            links2=page.locator('a').evaluate_all('(aa)=>aa.map(a=>a.href)')
            for link in links2:assert page.request.get(link).ok,link
            page.set_viewport_size({'width':520,'height':900});page.wait_for_timeout(100)
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(BASE/'results/debugger-narrow.png'))
            # Embedded data and local images also work with no web server.
            page.goto((out/'review/debug.html').as_uri())
            page.wait_for_function('document.querySelector("#status").textContent.startsWith("Native location")')
            browser.close()
    finally:server.shutdown();server.server_close();thread.join()
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(sections=32,candidate_views=len(choices),links=len(links)+len(links2),errors=errors,
        checks=['all section navigation','arbitrary location','nearby observations','all candidate families','support overlay','native crop zoom','available uncertainty/regression filters','contact evidence','seam','all links','desktop','narrow no overflow','offline file URL'],feedback_written=False))
    print('Chromium full-circuit debugger passed')

if __name__=='__main__':main()
