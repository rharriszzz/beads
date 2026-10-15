"""R291 short review, all photographic cases and separate durable test feedback."""
import tempfile
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import *
from .serve import server

def main():
    errors=[];manifest=read(REVIEW/'manifest.json');first=manifest['start_here'][0];loaded=[];links=[]
    with tempfile.TemporaryDirectory(prefix='r291-browser-') as folder:
        httpd=server(0,Path(folder));thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{httpd.server_port}/'
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1050},device_scale_factor=1)
                page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url)
                def ready(name):page.wait_for_function('(id)=>document.body.dataset.loaded===id',arg=name)
                def saved(revision):page.wait_for_function('(n)=>document.querySelector("#message").textContent.startsWith("Saved revision "+n+".")',arg=revision)
                ready(first);assert page.locator('#caseSelect option').count()==14;assert not page.locator('#ownershipView').is_checked();assert page.locator('#ownership').is_hidden();assert page.locator('[data-answer]').count()==6
                page.locator('[data-answer="partial"]').click();saved(1);assert httpd.store.state()['cases'][first]['payload']['diagnostics']==[]
                page.locator('#diagnostics input[value="neighbor"]').check();saved(2)
                page.locator('[data-answer="wrong-clear"]').click();saved(3);page.locator('#undo').click();saved(4)
                assert page.locator('[data-answer="partial"]').get_attribute('aria-pressed')=='true'
                page.reload();ready(first);page.wait_for_function('document.querySelector("[data-answer=partial]").getAttribute("aria-pressed")==="true"')
                page.locator('#nextOpen').click();ready(manifest['start_here'][1]);assert page.locator('#playlist').input_value()=='start'
                page.locator('#playlist').select_option('all');page.wait_for_function('document.querySelector("#caseSelect").options.length===68')
                for c in manifest['cases']:
                    page.locator('#caseSelect').select_option(c['case_id']);ready(c['case_id']);assert page.locator('#evidence details').count()==8;assert page.locator('#raw').evaluate('(x)=>x.complete&&x.naturalWidth>0');assert page.locator('#error').inner_text()=='';loaded.append(c['case_id'])
                # Target, marks toggle, actual zoom/pan and alternative differences.
                page.locator('#caseSelect').select_option('P2');ready('P2');original=page.locator('#canvas').evaluate('(c)=>c.toDataURL()')
                page.locator('#hide').click();unmarked=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');assert original!=unmarked
                page.locator('#hide').click();assert original==page.locator('#canvas').evaluate('(c)=>c.toDataURL()')
                page.locator('#zoomIn').click();assert original!=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#reset').click()
                rect=page.locator('#viewport').bounding_box();page.mouse.move(rect['x']+100,rect['y']+100);page.mouse.down();page.mouse.move(rect['x']+140,rect['y']+130);page.mouse.up();assert original!=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#reset').click()
                alternative=next(c for c in manifest['cases'] if c['alternative']);page.locator('#caseSelect').select_option(alternative['case_id']);ready(alternative['case_id']);page.locator('#proposal').select_option('B');page.locator('#differences').check();assert page.locator('#status').inner_text().startswith('B')
                rev=httpd.store.state()['cases'].get(alternative['case_id'],{}).get('revision',0);page.locator('[data-answer="B"]').click();saved(rev+1)
                # Reversed ownership pair is answered once and reused elsewhere.
                page.locator('#caseSelect').select_option('red-multiple-1');ready('red-multiple-1');page.locator('#ownershipView').check();select=page.locator('[aria-label="Ownership H-0656-0525"]');select.select_option('same');saved(1)
                page.locator('#caseSelect').select_option('red-multiple-2');ready('red-multiple-2');page.locator('#ownershipView').check();assert page.locator('[aria-label="Ownership H-0656-0515"]').input_value()=='same'
                page.locator('#caseSelect').select_option('red-worst');ready('red-worst');assert 'all displayed marks' in page.locator('#knownEvidence').inner_text()
                page.locator('#playlist').select_option('start');page.wait_for_function('document.querySelector("#caseSelect").options.length===14');page.locator('#caseSelect').select_option(first);ready(first)
                page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
                page.set_viewport_size({'width':520,'height':900});page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Narrow overflow'
                with page.expect_download() as download:page.locator('#export').click()
                download.value.save_as(str(Path(folder)/'export.json'));export=read(Path(folder)/'export.json');assert export['schema']=='R291-feedback-export-v1' and len(export['events'])>=6
                for a in page.locator('a[href]').all():
                    href=a.get_attribute('href')
                    if href.startswith(('http','#')):continue
                    response=page.request.get(url+href);assert response.ok,href;links.append(href)
                page.goto(url+'coverage.html');assert page.locator('tr').count()>=19
                browser.close()
            reopened=server(0,Path(folder));assert reopened.store.state()==httpd.store.state();reopened.server_close()
        finally:httpd.shutdown();httpd.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(real_photo_cases_loaded=len(loaded),start_here=14,answer_choices=6,evidence_tests_per_candidate=8,desktop_width=1400,narrow_width=520,errors=errors,links=links,checks=['optional diagnostics','one-click partial','wrong despite clear photo','undo/reload','Start Here navigation','target hide/restore','actual zoom/pan','alternative differences','ownership pair reuse','preserved user evidence','export','reopened disk store'],feedback_destination='Temporary directory only; R290 and real R291 feedback not changed.'))
    print('Chromium:',len(loaded),'photo cases; 14 Start Here; six answers; optional diagnostics/pair reuse; responsive and durable feedback pass')

if __name__=='__main__':main()
