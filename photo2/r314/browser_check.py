"""Offline static review smoke test, native photo preservation checked separately."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save,utc

OUT=ROOT/'photo2/r314/results'
def main():
 errors=[];checks=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((OUT/'index.html').as_uri());page.wait_for_load_state('load')
  assert page.locator('h1').inner_text().startswith('R314');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');checks.append('all desktop images loaded')
  page.screenshot(path=str(OUT/'review/browser-desktop.png'),full_page=False);page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'review/browser-narrow.png'));assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');checks.append('narrow images loaded')
  page.context.set_offline(True);page.reload();page.wait_for_load_state('load');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');checks.append('offline local images loaded');browser.close()
 assert not errors
 save(OUT/'browser-check.json',dict(passed=True,utc=utc(),checks=checks,errors=errors,scope='Static offline page only. Native raw arrays and all local artifact paths independently checked.'))
if __name__=='__main__':main()
