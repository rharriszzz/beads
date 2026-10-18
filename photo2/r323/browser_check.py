"""Static original-photo review checks, desktop/narrow/offline."""
import json
from pathlib import Path
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'photo2/r323/results'
def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((OUT/'index.html').as_uri());page.wait_for_load_state('load')
        assert page.locator('h1').inner_text().startswith('R323');assert page.locator('img').count()==6
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
        for link in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):assert (OUT/link).exists(),link
        page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
        page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True)
        page.context.set_offline(True);page.reload();page.wait_for_load_state('load')
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');browser.close()
    assert not errors
    (OUT/'browser-check.json').write_text(json.dumps(dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),checks=['six original-RGB figures','all local links','desktop','narrow without overflow','offline reload'],errors=errors),indent=2)+'\n');print('PASS desktop/narrow/offline static review')
if __name__=='__main__':main()
