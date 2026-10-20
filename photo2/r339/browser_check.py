"""Actual offline desktop/narrow review and local-key interaction checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'photo2/r339/review';errors=[];failed=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failed.append(r.url));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R339_READY');assert page.locator('.case').count()==5 and page.locator('.panel').count()==25;assert page.locator('.slot').count()==208 and page.locator('.slot.strong').count()==179 and page.locator('.slot.conflict').count()==21;keyrows=0
  for i in range(5):
   page.locator(f'[data-case="{i}"]').click();assert page.evaluate('R339_CURRENT')==i;assert page.locator('.case:visible').count()==1
   for panel in page.locator('.case:visible .panel').all():
    panel.locator('details').evaluate('(e)=>e.open=true');rows=panel.locator('table tr');assert rows.nth(1).locator('td').nth(0).inner_text()=='1';assert rows.nth(1).locator('td').nth(1).inner_text()==panel.locator('h3').inner_text().replace('Photograph ','');assert panel.locator('.number').count()==rows.count()-1;assert panel.locator('.diagram circle').count()==rows.count()-1;keyrows+=rows.count()-1
  for panel in page.locator('#solved .panel').all():panel.locator('details').evaluate('(e)=>e.open=true');keyrows+=panel.locator('table tr').count()-1
  assert keyrows==509;page.locator('[data-case="0"]').click();page.locator('#next').click();assert page.evaluate('R339_CURRENT')==1;page.locator('#previous').click();assert page.evaluate('R339_CURRENT')==0
  for id,cl in [('numbers','.number'),('links','.photolink'),('pixels','.pixels')]:
   page.locator('#'+id).check();assert page.locator(cl).first.evaluate('(e)=>getComputedStyle(e).display')!='none';page.locator('#'+id).uncheck();assert page.locator(cl).first.evaluate('(e)=>getComputedStyle(e).display')=='none'
  page.locator('#numbers').check();width=page.locator('.native').first.evaluate('(e)=>e.getBoundingClientRect().width');page.locator('#zoom-in').click();assert page.locator('.native').first.evaluate('(e)=>e.getBoundingClientRect().width')>width*1.3;page.locator('.stage').first.evaluate('(e)=>e.scrollLeft=100');assert page.locator('.stage').first.evaluate('(e)=>e.scrollLeft')>0;page.locator('#fit').click()
  for href in page.locator('a').evaluate_all('(es)=>es.map(e=>e.getAttribute("href"))'):
   if not href.startswith('#'):assert (out/href).resolve().is_file(),href
  assert page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)');page.locator('.case:visible .panel').first.screenshot(path=str(out/'question196.png'));page.locator('#pattern').screenshot(path=str(out/'sequence208.png'));page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'desktop.png'));page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R339_READY');page.goto((out/'ledger.html').as_uri());assert page.locator('main section').count()==29;assert page.locator('img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)');assert not errors,errors;assert not failed,failed;browser.close()
 receipt=dict(passed=True,questions=5,panels=25,own_panel_key_rows=509,each_target_own_feature1=True,actual_links_and_current_colors=True,all_keys_expanded=True,navigation=True,photo_number_link_sample_controls=True,zoom_pan=True,narrow=True,offline=True,supported=179,conflicts=21,insufficient=8,ledger_unknowns=29,errors=errors,failed_requests=failed);(out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R339 browser',receipt)
if __name__=='__main__':main()
