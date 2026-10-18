"""Read-only offline review, screenshots and static target checks."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

def main():
 out=Path('/home/rharris/git/beads/photo2/r329/results')
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());page.wait_for_load_state('load')
  assert page.locator('h1').inner_text()=='Trace the disagreement backward';assert page.locator('svg image').count()==11
  assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)')
  for href in page.locator('a').evaluate_all('(as)=>as.map(a=>a.getAttribute("href"))'):
   assert (out/href).resolve().is_file(),href
  page.screenshot(path=str(out/'browser-desktop.png'),full_page=True);page.locator('.panels').first.screenshot(path=str(out/'closest-comparison.png'))
  page.locator('#toggle').click();assert page.locator('.overlay').first.evaluate('e=>e.style.display==="none"');page.locator('#toggle').click()
  page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'browser-narrow.png'));page.context.set_offline(True);page.reload();assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)');assert not errors;browser.close()
 (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,overlay_toggle=True,local_links=True,images_loaded=True,errors=errors),indent=2)+'\n');print('PASS R329 browser desktop/narrow/offline/overlays/local links')
if __name__=='__main__':main()
