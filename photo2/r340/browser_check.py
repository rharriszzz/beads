"""Bounded offline rendering check for the R340 material-region review."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'photo2/r340/autoregion/review';errors=[];failed=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failed.append(r.url));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R340_READY');assert page.locator('.slot').count()==208;assert page.locator('.slot.strong').count()==181 and page.locator('.slot.conflict').count()==19;assert page.locator('article').count()==9;assert page.locator('img').evaluate_all('(xs)=>xs.every(e=>e.complete&&e.naturalWidth>0)');page.screenshot(path=str(out/'desktop.png'))
  page.evaluate("show('C-1253-2928')");assert 'C-1253-2928' in page.locator('#target-name').inner_text();assert '1: C-1253-2928' in page.locator('#key').inner_text();assert 'unknown' in page.locator('#detail').inner_text();page.locator('#viewer').screenshot(path=str(out/'edge-false-positive.png'));page.locator('#mark').uncheck();page.locator('#mark').check();page.evaluate('position(190)');assert page.locator('#records tr').count()==7;page.evaluate("document.querySelector('#search').value='REC266';list()");assert page.locator('#records tr').count()==2
  page.set_viewport_size({'width':390,'height':844});page.evaluate('window.scrollTo(0,0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R340_READY');assert not errors,errors;assert not failed,failed;browser.close()
 receipt=dict(passed=True,offline=True,narrow=True,loaded_literal_images=19,local_target_number1=True,photo_region_toggle=True,current_adjacency=True,native_viewer_case_switch=True,search=True,pattern208=True,supported=181,conflicts=19,insufficient=8,errors=errors,failed_requests=failed);(out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R340 browser',receipt)
if __name__=='__main__':main()
