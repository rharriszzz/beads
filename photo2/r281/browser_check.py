"""Rendered review layer separation and original-pixel checks."""
from playwright.sync_api import sync_playwright
from .common import OUT,ROOT,save

def main():
 errors=[];checks=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1400,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((ROOT/'photo2/review/r281/index.html').as_uri());page.wait_for_function("document.querySelector('#raw').width===220")
  count=page.locator('#example option').count()
  for i in range(count):
   page.select_option('#example',str(i));page.wait_for_function('im.complete && im.naturalWidth>0');page.wait_for_timeout(50)
   assert 'H1' in page.locator('#scores').inner_text();raw=page.locator('#raw').screenshot()
   for name in ('phase1','prediction','null','support','positive','negative','uncertainty'):
    page.locator('#'+name).check();page.locator('#'+name).uncheck()
   assert raw==page.locator('#raw').screenshot();checks.append(i)
  page.select_option('#example','10');page.wait_for_timeout(100);layers=[];raw=page.locator('#raw').screenshot()
  for name in ('phase1','prediction','null','support','positive','negative','uncertainty'):
   page.locator('#'+name).check();a=page.locator('#overlay').screenshot();page.locator('#'+name).uncheck();b=page.locator('#overlay').screenshot();assert a!=b,name;assert raw==page.locator('#raw').screenshot();layers.append(name)
  page.locator('#prediction').check();page.locator('#support').check();page.locator('#phase1').check();page.screenshot(path=str(OUT/'browser-review.png'));browser.close()
 assert not errors,errors;save(OUT/'browser-check.json',dict(cases=len(checks),layers=layers,original_unchanged=True,errors=errors));print('browser',len(checks),'cases;',len(layers),'layers')
if __name__=='__main__':main()
