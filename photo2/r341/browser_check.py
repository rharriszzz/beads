"""Real offline desktop/mobile and exact local-key/diagram review checks."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'photo2/r341/review';errors=[];failed=[];panels=json.load(open(out/'panels.json'));inventory=panels[-1]['panel']
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failed.append(r.url));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R341_READY');assert page.locator('.question').count()==4;assert page.locator('.panel').count()==21;assert page.locator('.slot.strong').count()==191 and page.locator('.slot.conflict').count()==9 and page.locator('.slot.observed').count()==8
  for r in panels:
   el=page.locator('#'+r['panel']);assert ('1: '+r['id']) in el.locator('.key').text_content(),r['id'];assert r['key'][0]==r['id']
  assert panels[0]['key'][1]=='C-1739-2960';assert panels[3]['key'][1]=='C-1677-1513';assert panels[-2]['key'][1]=='E5-0562-1620'
  page.screenshot(path=str(out/'desktop.png'));page.locator('#question-0').screenshot(path=str(out/'question169.png'));page.locator('#mark').uncheck();page.locator('#mark').check();page.evaluate('position(102)');assert page.locator('#records tr').count()==5;page.evaluate("inspect('NEW-1681-1498')");assert page.locator('#'+inventory+' .key').is_visible();assert '1: NEW-1681-1498' in page.locator('#'+inventory+' .key').inner_text()
  page.evaluate("selectedResidue=null;document.querySelector('#search').value='NEW-910-2406';list()");assert page.locator('#records tr').count()==2;page.locator('#records button').click();assert 'NEW-910-2406' in page.locator('#'+inventory+' h4').inner_text();assert 'overlay black' in page.locator('#'+inventory+' .detail').inner_text();page.set_viewport_size({'width':390,'height':844});page.evaluate('window.scrollTo(0,0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R341_READY');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors,errors;assert not failed,failed;browser.close()
 receipt=dict(passed=True,offline=True,narrow=True,questions=4,native_panels=21,all_own_photograph_keys=True,target_always1=True,question_companion2_keys=True,current_adjacency=True,region_toggle=True,search=True,live_inventory_key_visible=True,supported=191,conflicting=9,insufficient=8,errors=errors,failed_requests=failed);(out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R341 browser',receipt)
if __name__=='__main__':main()
