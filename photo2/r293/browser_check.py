"""Actual browser checks for the coverage overview and new short review."""
import tempfile,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import *
from .serve import server

def main():
    manifest=read(REVIEW/'manifest.json');errors=[];loaded=[]
    with tempfile.TemporaryDirectory(prefix='r293-browser-') as folder:
        httpd=server(0,Path(folder));thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{httpd.server_port}/'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url)
                def ready(cid):page.wait_for_function('(id)=>document.body.dataset.loaded===id',arg=cid)
                def saved(n):page.wait_for_function('(n)=>document.querySelector("#message").textContent.startsWith("Saved revision "+n+".")',arg=n)
                first=manifest['start_here'][0];ready(first);page.wait_for_function('document.body.dataset.coverageReady==="true"');assert page.locator('#stationSelect option').count()==385;assert page.locator('#caseSelect option').count()==8;assert httpd.store.state()['cases']=={}
                assert 'not establish every bead' in page.locator('#coverageSummary').inner_text();page.locator('#stationSelect').select_option('S083');assert 'feature evidence present' in page.locator('#stationInfo').inner_text();assert page.locator('#stationRaw').evaluate('(i)=>i.complete&&i.naturalWidth>0');before=page.locator('#mapCanvas').evaluate('(c)=>c.toDataURL()');page.locator('#mapHide').click();assert before!=page.locator('#mapCanvas').evaluate('(c)=>c.toDataURL()');page.locator('#mapHide').click();page.locator('#mapMode').select_option('material');page.locator('#mapMode').select_option('priority');box=page.locator('#mapCanvas').bounding_box();page.mouse.move(box['x']+180,box['y']+160);page.mouse.wheel(0,-350);page.mouse.down();page.mouse.move(box['x']+210,box['y']+180);page.mouse.up();page.locator('#mapFit').click();page.locator('#nextGap').click();assert 'does not prove complete bead coverage' in page.locator('#featureInfo').inner_text()
                page.locator('[data-answer="A"]').click();saved(1);page.locator('[data-answer="partial"]').click();saved(2);page.locator('#diagnostics input[value="neighbor"]').check();saved(3);page.locator('#undo').click();saved(4);page.reload();ready(first);assert page.locator('[data-answer="partial"]').get_attribute('aria-pressed')=='true'
                page.locator('#playlist').select_option('all')
                for c in manifest['cases']:
                    page.locator('#caseSelect').select_option(c['case_id']);ready(c['case_id']);assert page.locator('#evidence details').count()==8;assert page.locator('#raw').evaluate('(i)=>i.complete&&i.naturalWidth>0');assert page.locator('#error').inner_text()=='';loaded.append(c['case_id'])
                    if c['historical_review']:assert page.locator('[data-answer="A"]').is_disabled();assert 'no repeat answer' in page.locator('#previousReview').inner_text()
                page.locator('#caseSelect').select_option('red-worst');ready('red-worst');assert 'all displayed marks' in page.locator('#knownEvidence').inner_text();assert 'threshold sensitivity' in page.locator('#positionInfo').inner_text();page.locator('#unreviewed').check();assert page.locator('#caseSelect option').count()==sum(not c['historical_review'] for c in manifest['cases'])-1;page.locator('#unreviewed').uncheck()
                page.locator('#playlist').select_option('start');page.locator('#caseSelect').select_option(first);ready(first);page.locator('#seamsOnly').check();page.locator('#seamsOnly').uncheck();old=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#zoomIn').click();assert old!=page.locator('#canvas').evaluate('(c)=>c.toDataURL()');page.locator('#reset').click();page.locator('#hide').click();page.locator('#hide').click()
                page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True);page.set_viewport_size({'width':520,'height':900});page.wait_for_timeout(100);assert page.locator('#mapCanvas').evaluate('(c)=>{const a=c.getContext("2d").getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<a.length;i+=4)if(a[i]>60)n++;return n/(c.width*c.height)>.2;}'),'Native photo must remain visible after narrow-screen refit';page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                with page.expect_download() as dl:page.locator('#export').click()
                dl.value.save_as(str(Path(folder)/'export.json'));d=read(Path(folder)/'export.json');assert d['schema']=='R293-feedback-export-v1';assert len(d['events'])==4;assert d['events'][0]['position_measurements']['physical_center'] is None
                for path in ('report.md','reproduce.md','coverage.html'):assert page.request.get(url+path).ok
                browser.close()
            reopened=server(0,Path(folder));assert reopened.store.state()==httpd.store.state();reopened.server_close()
        finally:httpd.shutdown();httpd.server_close();thread.join()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(cases_loaded=len(loaded),start_here=8,stations=385,errors=errors,checks=['native whole-photo map','priority/material modes','map zoom/pan/hide','station native crop and no false gap','125 native candidate crops/all T1–T8','24 historical reviews read-only and skipped by unreviewed navigation','8 new central questions','independent/candidate/physical positions distinguished','partial/diagnostic/undo/reopen/export','desktop1400/narrow520'],feedback_destination='Temporary directory only; no historical or actual R293 answers created.'));print('Chromium:',len(loaded),'cases,385 windows,8 new questions passed')
if __name__=='__main__':main()
