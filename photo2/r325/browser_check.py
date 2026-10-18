"""Native-crop interactions, canvas rendering, desktop/narrow/offline checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path(__file__).parent/'results'
def main():
    errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((OUT/'index.html').resolve().as_uri());page.wait_for_function('window.REVIEW_READY && REVIEW_READY()')
        assert page.locator('h1').inner_text().startswith('R325');assert page.locator('canvas').count()==3
        for i in range(19):
            page.locator('#location').select_option(str(i));assert 'Window' in page.locator('#transition').inner_text()
            assert page.locator('#right').evaluate('(c)=>c.getContext("2d").getImageData(200,150,1,1).data[3]')==255
        page.locator('#location').select_option('1600,280');page.locator('.pair').screenshot(path=str(OUT/'native-upper.png'))
        page.locator('#location').select_option('1620,1480');page.locator('.pair').screenshot(path=str(OUT/'native-inward.png'))
        page.locator('#location').select_option('1400,2990');page.locator('#view').select_option('colored');page.locator('.pair').screenshot(path=str(OUT/'native-colored.png'))
        page.locator('#view').select_option('compare');page.screenshot(path=str(OUT/'browser-desktop.png'),full_page=True)
        page.locator('#raw').click();a=page.locator('#right').evaluate('(c)=>c.toDataURL()');page.locator('#raw').click();b=page.locator('#right').evaluate('(c)=>c.toDataURL()');assert a!=b
        page.locator('#whole').click(position={'x':400,'y':100});assert 'ab' in page.locator('#readout').inner_text()
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(OUT/'browser-narrow.png'),full_page=True)
        page.context.set_offline(True);page.reload();page.wait_for_function('window.REVIEW_READY && REVIEW_READY()')
        missing=[]
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if not(OUT/href).exists():missing.append(href)
        browser.close()
    assert not errors,errors
    receipt=dict(passed=not missing,canvas_checks=True,transitions=19,desktop=True,narrow=True,offline=True,missing_links=missing,errors=errors)
    (OUT/'browser-check.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
if __name__=='__main__':main()
