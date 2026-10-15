"""Actual Chromium review checks; all test judgments live under /tmp."""
import tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import *
from .serve import server

def main():
    manifest=read(REVIEW/'manifest.json');errors=[];loaded=[]
    with tempfile.TemporaryDirectory(prefix='r292-browser-') as folder:
        httpd=server(0,Path(folder));thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{httpd.server_port}/'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url)
                def ready(cid):page.wait_for_function('(id)=>document.body.dataset.loaded===id',arg=cid)
                def saved(rev):page.wait_for_function('(rev)=>document.querySelector("#message").textContent.startsWith("Saved revision "+rev+".")',arg=rev)
                first=manifest['start_here'][0];ready(first);assert page.locator('#caseSelect option').count()==len(manifest['start_here']);assert page.locator('[data-answer]').count()==6;assert httpd.store.state()['cases']=={};assert page.locator('#playlist option[value="start"]').inner_text()==f'Start Here · {len(manifest["start_here"])} cases'
                page.locator('#seamsOnly').check();assert page.locator('#separatorInfo').inner_text().startswith(str(len(read(REVIEW/'data'/(first+'.json'))['separator_arcs'])));page.locator('#seamsOnly').uncheck()
                original=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#hide').click();assert original!=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#hide').click();page.locator('#zoomIn').click();box=page.locator('#canvas').bounding_box();page.mouse.move(box['x']+90,box['y']+90);page.mouse.down();page.mouse.move(box['x']+125,box['y']+115);page.mouse.up();assert original!=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#reset').click()
                page.locator('[data-answer="partial"]').click();saved(1);page.locator('#diagnostics input[value="neighbor"]').check();saved(2);page.locator('[data-answer="wrong-clear"]').click();saved(3);page.locator('#undo').click();saved(4);page.reload();ready(first);assert page.locator('[data-answer="partial"]').get_attribute('aria-pressed')=='true'
                page.locator('#playlist').select_option('all')
                for c in manifest['cases']:
                    page.locator('#caseSelect').select_option(c['case_id']);ready(c['case_id']);assert page.locator('#evidence details').count()==8;assert page.locator('#raw').evaluate('(i)=>i.complete&&i.naturalWidth>0');loaded.append(c['case_id'])
                for cid in ('Q14','red-worst'):
                    page.locator('#caseSelect').select_option(cid);ready(cid);assert 'no repeat judgment is needed' in page.locator('#previousReview').inner_text();assert not any(c.get('case_id')==cid for c in httpd.store.events())
                page.locator('#caseSelect').select_option('red-worst');ready('red-worst');assert 'all displayed marks' in page.locator('#knownEvidence').inner_text()
                page.locator('#caseSelect').select_option('red-multiple-1');ready('red-multiple-1');page.locator('#ownershipView').check();page.locator('[aria-label="Ownership H-0656-0525"]').select_option('same');saved(1);page.locator('#caseSelect').select_option('red-multiple-2');ready('red-multiple-2');page.locator('#ownershipView').check();assert page.locator('[aria-label="Ownership H-0656-0515"]').input_value()=='same'
                alternate=next(c for c in manifest['cases'] if c['alternative']);page.locator('#caseSelect').select_option(alternate['case_id']);ready(alternate['case_id']);page.locator('#proposal').select_option('B');page.locator('#differences').check();assert page.locator('#status').inner_text().startswith('B')
                page.locator('#playlist').select_option('start');page.locator('#caseSelect').select_option(first);ready(first);page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True);page.set_viewport_size({'width':520,'height':900});page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                with page.expect_download() as dl:page.locator('#export').click()
                dl.value.save_as(str(Path(folder)/'export.json'));export=read(Path(folder)/'export.json');assert export['schema']=='R292-feedback-export-v1';assert export['events'][0]['displayed_separator_arcs']
                for href in ('report.md','reproduce.md','coverage.html'):
                    assert page.request.get(url+href).ok,href
                browser.close()
            reopened=server(0,Path(folder));assert reopened.store.state()==httpd.store.state();reopened.server_close()
        finally:httpd.shutdown();httpd.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(cases_loaded=len(loaded),start_here=len(manifest['start_here']),answers=6,errors=errors,checks=['actual separators and separate-only view','raw photo','hide all','actual zoom/pan','six answers and optional diagnostics','revision undo reload reopen export','ownership pair reuse','historical red-worst evidence','unchanged accepted references not answered','all eight tests','desktop1400/narrow520'],feedback_destination='Temporary directory only; historical and actual R292 feedback unchanged.'));print('Chromium passed',len(loaded),'real-photo cases;',len(manifest['start_here']),'Start Here')
if __name__=='__main__':main()
