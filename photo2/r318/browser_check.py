from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save,utc
OUT=ROOT/'photo2/r318/results'

def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((OUT/'index.html').as_uri());page.wait_for_load_state('load');assert page.locator('h1').inner_text().startswith('R318')
        assert page.locator('img').count()==4
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
        page.screenshot(path=str(OUT/'browser-desktop.png'))
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
        page.screenshot(path=str(OUT/'browser-narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_load_state('load')
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');browser.close()
    assert not errors
    save(OUT/'browser-check.json',dict(passed=True,utc=utc(),checks=['both epoch vector/error figures loaded','desktop','narrow without horizontal overflow','offline'],errors=errors))

if __name__=='__main__':main()
