from pathlib import Path
import json
from playwright.sync_api import sync_playwright
OUT=Path(__file__).parent/'results'
def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1200,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((OUT/'index.html').resolve().as_uri());page.wait_for_load_state('load');assert page.locator('h1').inner_text().startswith('R327');assert page.locator('article').count()==5
        for src in page.locator('svg image').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):assert (OUT/src).exists()
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):assert (OUT/href).exists(),href
        page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.locator('details').first.locator('summary').click();assert page.locator('details').first.get_attribute('open') is not None;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True);page.context.set_offline(True);page.reload();page.wait_for_load_state('load');assert page.locator('svg image').count()>=12;browser.close()
    assert not errors;result=dict(passed=True,desktop=True,narrow=True,offline=True,details_open=True,errors=errors);(OUT/'browser-check.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
