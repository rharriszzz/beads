"""Rendered review smoke test; no network dependencies or external writes."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from .common import OUT,ROOT,save

def main():
 errors=[];checks=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True)
  page=browser.new_page(viewport={'width':1400,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto((ROOT/'photo2/r280/index.html').as_uri());page.wait_for_function("document.querySelector('#raw').width===320")
  count=page.locator('#scene option').count();assert count>=24
  for i in range(count):
   page.select_option('#scene',str(i));page.wait_for_function('bitmap!==null')
   assert page.locator('#details').inner_text().startswith('{')
   for name in ('phase1','prediction','evidence','uncertainty','neighbors'):
    page.locator('#'+name).uncheck();page.locator('#'+name).check()
   checks.append(dict(case=i,predictions=page.locator('#bead option').count()))
  page.select_option('#scene','12');page.wait_for_function('bitmap!==null')
  raw=page.locator('#raw').screenshot();layer_checks=[]
  for name in ('phase1','prediction','evidence','uncertainty','neighbors'):
   page.locator('#'+name).check();before=page.locator('#overlay').screenshot()
   page.locator('#'+name).uncheck();after=page.locator('#overlay').screenshot()
   assert before!=after,name
   assert page.locator('#raw').screenshot()==raw,name+' modified original pixels'
   layer_checks.append(name);page.locator('#'+name).check()
  page.screenshot(path=str(OUT/'browser-review.png'),full_page=False)
  assert not errors,errors;browser.close()
 save(OUT/'browser-check.json',dict(cases=checks,errors=errors,visually_verified_layers=layer_checks,original_canvas_unchanged=True,checks='All cases load; every layer toggles; model rows and evidence details render; actual-photo screenshot saved.'))
 print('browser cases',count,'errors',errors)
if __name__=='__main__':main()
