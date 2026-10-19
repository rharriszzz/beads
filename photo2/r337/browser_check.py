"""Actual local offline review, controls, native identity and narrow-layout check."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
    out=ROOT/'photo2/r337/review';errors=[];requests=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:requests.append(r.url));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R337_READY');assert page.locator('#lattice .bead').count()==1039;assert page.locator('#lattice .core').count()==710
        assert page.locator('.comparison').count()==3;assert page.locator('.motif').count()==6;assert page.locator('#motif-0 .strong').count()==176;assert page.locator('#motif-0 .slot').count()==208
        page.locator('#interior').check();assert page.locator('#lattice .bead:visible').count()==710;page.locator('#interior').uncheck();page.locator('#link-toggle').uncheck();assert page.locator('#links').evaluate('(e)=>getComputedStyle(e).display')=='none';page.locator('#link-toggle').check()
        page.locator('#traces').select_option('BR');assert page.locator('.trace.BY:visible').count()==0;assert page.locator('.trace.BR:visible').count()>0;page.locator('#traces').select_option('all');page.locator('#cohort').select_option('interior');assert page.locator('#tile-interior').is_visible();page.locator('#cohort').select_option('active')
        page.locator('#zoom-in').click();assert page.locator('#lattice').evaluate('(e)=>e.getBoundingClientRect().width')>4400;page.locator('#zoom-out').click();page.locator('#paper').evaluate('(e)=>e.scrollLeft=0');node=page.locator('#lattice [data-id="C-1302-0316"]');node.click();assert page.evaluate('R337_SELECTED')=='C-1302-0316';assert page.locator('#selected').inner_text().startswith('C-1302-0316');assert page.locator('#native image').get_attribute('width')=='2540';assert page.locator('#native image').get_attribute('height')=='3182'
        for case in page.locator('.comparison').all():case.locator('details').evaluate('(e)=>e.open=true');assert case.locator('table tr').count()>10
        page.locator('#overlays').click();assert page.locator('.overlay').first.evaluate('(e)=>e.style.visibility')=='hidden';page.locator('#overlays').click()
        for href in page.locator('a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
            if not href.startswith('#'):assert (out/href).resolve().is_file(),href
        page.locator('#design').screenshot(path=str(out/'design.png'));page.locator('#motif-0').screenshot(path=str(out/'sequence208.png'));page.locator('.comparison').nth(1).screenshot(path=str(out/'continuation.png'));page.screenshot(path=str(out/'desktop.png'))
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R337_READY');assert not errors,errors;assert not requests,requests;browser.close()
    receipt=dict(passed=True,measured_nodes=1039,frozen_core=710,sequence_slots=208,strict_colors=176,unknown_positions=32,comparison_panels=3,sequence_displays=6,all_keys_expanded=True,native_dimensions=[2540,3182],layers_and_zoom=True,local_links=True,narrow=True,offline=True,errors=errors,failed_requests=requests)
    (out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R337 browser')
if __name__=='__main__':main()
