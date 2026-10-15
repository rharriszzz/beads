"""Real-photo batch UI, durable feedback and responsive checks in Chromium.

All simulated user actions write into /tmp, never the user's feedback directory.
"""
import tempfile
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import *
from .serve import server

def main():
    errors=[];images=[];links=[]
    with tempfile.TemporaryDirectory(prefix='r290-browser-') as folder:
        httpd=server(0,Path(folder));thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{httpd.server_port}/'
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1050},device_scale_factor=1)
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url);page.wait_for_function('document.body.dataset.loaded==="P1"');page.wait_for_function('document.querySelector("#raw").complete && document.querySelector("#raw").naturalWidth>0')
                assert page.locator('[data-answer="A"]').is_enabled()
                page.locator('[data-answer="neither"]').click();page.wait_for_function('document.querySelector("#message").textContent.startsWith("Saved revision 1")')
                page.locator('[data-answer="not-sure"]').click();page.wait_for_function('document.querySelector("#message").textContent.startsWith("Saved revision 2")')
                page.locator('#undo').click();page.wait_for_function('document.querySelector("#message").textContent.startsWith("Saved revision 3")')
                assert page.locator('[data-answer="neither"]').get_attribute('aria-pressed')=='true'
                page.reload();page.wait_for_function('document.querySelector("[data-answer=neither]").getAttribute("aria-pressed")==="true"')
                # Every packaged photographic crop and case loads through the UI.
                manifest=read(REVIEW/'manifest.json')
                for e in manifest['cases']:
                    page.locator('#caseSelect').select_option(e['case_id']);page.wait_for_function('(id)=>document.body.dataset.loaded===id',arg=e['case_id'])
                    page.wait_for_function('(id)=>document.querySelector("#raw").src.endsWith(id+".png") && document.querySelector("#raw").complete && document.querySelector("#raw").naturalWidth>0',arg=e['case_id'])
                    assert page.locator('#evidence details').count()==8;images.append(e['case_id'])
                    assert page.locator('#error').inner_text()=='',e['case_id']
                alternative=next(e for e in manifest['cases'] if e['alternative'] and e['case_id']!='P1')
                page.locator('#caseSelect').select_option(alternative['case_id']);page.wait_for_function('(id)=>document.body.dataset.loaded===id',arg=alternative['case_id'])
                page.locator('#proposal').select_option('B');assert page.locator('#status').inner_text().startswith('B:')
                page.locator('[data-answer="B"]').click();page.wait_for_function('document.querySelector("#message").textContent.startsWith("Saved revision")')
                ownership=page.locator('#ownership select')
                if ownership.count():
                    ownership.first.select_option('same');page.wait_for_function('document.querySelector("#message").textContent.startsWith("Saved revision 2")')
                page.locator('#zoomIn').click();page.locator('#overlay').uncheck();page.locator('#overlay').check();page.locator('#features').uncheck();page.locator('#features').check();page.locator('#reset').click()
                page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
                page.set_viewport_size({'width':520,'height':900});page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True)
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Narrow overflow'
                with page.expect_download() as download:page.locator('#export').click()
                download.value.save_as(str(Path(folder)/'export.json'));export=read(Path(folder)/'export.json');assert len(export['events'])>=4
                for a in page.locator('a[href]').all():
                    href=a.get_attribute('href')
                    if href.startswith(('http','#')):continue
                    response=page.request.get(url+href);assert response.ok,href;links.append(href)
                page.goto(url+'coverage.html');assert page.locator('tr').count()==19
                page.locator('a[href="index.html"]').click();page.wait_for_function('document.body.dataset.loaded==="P1"')
                page.locator('#split').select_option('reserved');page.wait_for_function('document.querySelector("#identity").textContent.includes("reserved")');assert page.locator('#caseSelect option').count()==17
                page.locator('#category').select_option('multiple-highlights');assert page.locator('#caseSelect option').count()>0
                browser.close()
            # Reopen the authoritative disk store through a fresh server instance.
            reopened=server(0,Path(folder));assert reopened.store.state()==httpd.store.state();reopened.server_close()
        finally:httpd.shutdown();httpd.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(cases_loaded=len(images),evidence_tests_per_case=8,links=links,errors=errors,desktop_width=1400,narrow_width=520,feedback_tests=['answer','revision','undo','reload','ownership','alternative-B','download-export','reopen-server'],feedback_destination='Temporary directory only; no user answers created.'))
    print('Chromium:',len(images),'real-photo cases; durable revisions/undo/export/reopen; desktop/narrow pass')

if __name__=='__main__':main()
