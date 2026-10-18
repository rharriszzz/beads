"""Static native-photo review checks: desktop, narrow and offline."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path(__file__).parent/'results'
def main():
    errors=[];missing=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((OUT/'index.html').resolve().as_uri());page.wait_for_load_state('load')
        assert page.locator('h1').inner_text().startswith('R326');assert page.locator('article').count()==4;assert page.locator('svg').count()==12
        for src in page.locator('svg image').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):assert (OUT/src).exists()
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if not (OUT/href).exists():missing.append(href)
        page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True)
        page.context.set_offline(True);page.reload();page.wait_for_load_state('load');assert page.locator('svg image').count()==12;browser.close()
    assert not errors and not missing,(errors,missing)
    result=dict(passed=True,desktop=True,narrow=True,offline=True,native_crop_panels=12,errors=errors,missing_links=missing);(OUT/'browser-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
