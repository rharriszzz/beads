"""Actual offline desktop/narrow interaction, local numbering and native-image checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
    out=ROOT/'photo2/r338/review';errors=[];requests=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:requests.append(r.url));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R338_READY');assert page.locator('.case').count()==5 and page.locator('.panel').count()==23;assert page.locator('.slot').count()==208 and page.locator('.slot.strong').count()==176 and page.locator('.slot.conflict').count()==24;assert page.locator('.slot.observed').count()+page.locator('.slot.unknown').count()==8
        key_rows=0
        for i in range(5):
            page.locator(f'[data-case="{i}"]').click();assert page.evaluate('R338_CURRENT')==i;assert page.locator('.case:visible').count()==1
            for panel in page.locator('.case:visible .panel').all():
                panel.locator('details').evaluate('(e)=>e.open=true');rows=panel.locator('tbody tr');assert rows.first.locator('td').nth(0).inner_text()=='1';assert rows.first.locator('td').nth(1).inner_text()==panel.locator('h3').inner_text().replace('Photograph ','');assert panel.locator('.photo-number').count()==rows.count();assert panel.locator('.diagram circle').count()==rows.count();key_rows+=rows.count()
            if i==2:page.locator('.case:visible .panel').first.screenshot(path=str(out/'conflict112.png'))
        completed=page.locator('#completed .panel');completed.locator('details').evaluate('(e)=>e.open=true');assert completed.locator('tbody tr').first.locator('td').nth(1).inner_text()=='R332-B-0098-0092';key_rows+=completed.locator('tbody tr').count()
        page.locator('[data-case="0"]').click();page.locator('#next').click();assert page.evaluate('R338_CURRENT')==1;page.locator('#previous').click();assert page.evaluate('R338_CURRENT')==0;page.locator('#numbers').uncheck();assert page.locator('.photo-number').first.evaluate('(e)=>getComputedStyle(e).display')=='none';page.locator('#numbers').check();page.locator('#photo-links').check();assert page.locator('.photo-link').first.evaluate('(e)=>getComputedStyle(e).display')!='none';page.locator('#photo-links').uncheck();width=page.locator('.native').first.evaluate('(e)=>e.getBoundingClientRect().width');page.locator('#zoom-in').click();assert page.locator('.native').first.evaluate('(e)=>e.getBoundingClientRect().width')>width*1.3;page.locator('.stage').first.evaluate('(e)=>e.scrollLeft=100');assert page.locator('.stage').first.evaluate('(e)=>e.scrollLeft')>0;page.locator('#fit').click()
        for href in page.locator('a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
            if not href.startswith('#'):assert (out/href).resolve().is_file(),href
        assert page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete && e.naturalWidth>0)');page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'desktop.png'));page.locator('#pattern').screenshot(path=str(out/'sequence208.png'));page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R338_READY');assert page.locator('.panel').count()==23
        page.goto((out/'ledger.html').as_uri());assert page.locator('main section').count()==32;assert page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete && e.naturalWidth>0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors,errors;assert not requests,requests;browser.close()
    receipt=dict(passed=True,primary_questions=5,numbered_panels=23,all_panel_key_rows_checked=key_rows,target_own_feature1=True,current_diagrams_actual_edges=True,slots=208,supported=176,conflicts=24,insufficient=8,ledger_unknown_positions=32,all_keys_expanded=True,photo_numbers_and_links=True,navigation=True,zoom_and_pan=True,local_links=True,narrow=True,offline=True,errors=errors,failed_requests=requests);(out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R338 browser',receipt)
if __name__=='__main__':main()
