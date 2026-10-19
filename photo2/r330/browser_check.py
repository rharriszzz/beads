"""Offline desktop/narrow review and inspectable screenshot artifacts."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

def main():
    out=Path('/home/rharris/git/beads/photo2/r330/review')
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());page.wait_for_load_state('load')
        assert 'repeating motif' in page.locator('h1').inner_text();assert page.locator('svg image').count()==18
        assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)')
        for href in page.locator('a').evaluate_all('(as)=>as.map(a=>a.getAttribute("href"))'):assert (out/href).resolve().is_file(),href
        page.screenshot(path=str(out/'desktop.png'));page.locator('.pair').nth(6).screenshot(path=str(out/'g-comparison.png'));page.locator('.pair').nth(7).screenshot(path=str(out/'h-comparison.png'));page.locator('.pair').nth(8).screenshot(path=str(out/'f-comparison.png'))
        page.locator('summary').first.click();page.locator('.pair').first.screenshot(path=str(out/'color-example.png'));page.locator('#toggle').click();assert page.locator('.overlay').first.evaluate('e=>e.style.display==="none"');page.locator('#toggle').click()
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();assert page.locator('img').evaluate_all('(imgs)=>imgs.every(i=>i.complete&&i.naturalWidth>0)');assert not errors;browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,overlays=True,local_links=True,errors=errors),indent=2)+'\n');print('PASS R330 browser')

if __name__=='__main__':main()
