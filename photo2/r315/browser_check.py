"""Static, offline desktop/narrow browser validation."""
from playwright.sync_api import sync_playwright
from photo2.r297.common import save,utc
from .diagnose import OUT

def main():
 errors=[];checks=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((OUT/'index.html').as_uri());page.wait_for_load_state('load');assert page.locator('h1').inner_text().startswith('R315');assert page.locator('table tr').count()==25;assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');checks.append('24 ledger rows and desktop images');page.screenshot(path=str(OUT/'review/browser-desktop.png'));page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(OUT/'review/browser-narrow.png'));checks.append('narrow layout renders');page.context.set_offline(True);page.reload();page.wait_for_load_state('load');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');checks.append('offline images');browser.close()
 assert not errors;save(OUT/'browser-check.json',dict(passed=True,utc=utc(),checks=checks,errors=errors))
if __name__=='__main__':main()
