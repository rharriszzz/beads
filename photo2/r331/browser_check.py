"""Local offline review, presentation PDF and clipping checks."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    out=Path('/home/rharris/git/beads/photo2/r331/review');errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1360,'height':950});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((out/'index.html').as_uri());page.wait_for_load_state('load')
        for href in page.locator('a').evaluate_all('(as)=>as.map(a=>a.getAttribute("href"))'):
            if href.endswith('.pdf'):continue
            assert (out/href).resolve().is_file(),href
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
        page.screenshot(path=str(out/'desktop.png'));page.locator('#toggle').click();assert page.locator('.overlay').first.evaluate('x=>x.style.display==="none"');page.locator('#toggle').click()
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'))
        page.set_viewport_size({'width':1360,'height':950});page.goto((out/'presentation.html').as_uri());assert page.locator('.slide').count()==10
        page.locator('.slide').nth(1).screenshot(path=str(out/'g-slide.png'));page.locator('.slide').nth(3).screenshot(path=str(out/'black-slide.png'));page.locator('.slide').nth(5).screenshot(path=str(out/'inward-slide.png'));page.locator('.slide').nth(7).screenshot(path=str(out/'material-slide.png'))
        page.emulate_media(media='print');clipped=page.locator('.slide').evaluate_all('(xs)=>xs.map((x,i)=>({slide:i+1,clipped:x.scrollHeight>x.clientHeight+2,height:x.scrollHeight,available:x.clientHeight})).filter(x=>x.clipped)')
        assert not clipped,clipped
        page.pdf(path=str(out/'presentation.pdf'),prefer_css_page_size=True,print_background=True)
        page.emulate_media(media='screen');page.context.set_offline(True);page.reload();assert page.locator('svg image').count()>0
        assert page.locator('svg image').evaluate_all('(xs)=>xs.every(x=>x.getAttribute("href").startsWith("assets/"))')
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');assert not errors
        browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,overlays=True,presentation_slides=10,pdf_no_clipping=True,errors=errors),indent=2)+'\n');print('PASS R331 browser/PDF')

if __name__=='__main__':main()
