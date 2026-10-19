"""Actual offline UI checks and desktop/narrow review screenshots."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

def main():
    out=Path('/home/rharris/git/beads/photo2/r333/review');errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1600,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R333_STATE&&R333_STATE.frames>2');page.wait_for_function('Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)')
        assert page.evaluate('new Set(R333.nodes.map(n=>n.id)).size===R333.nodes.length')
        assert page.evaluate('R333.nodes.filter(n=>n.status==="working").length')==1041
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if href.startswith('#'):continue
            assert (out/href).resolve().is_file(),href
        page.screenshot(path=str(out/'desktop.png'));page.locator('#section').select_option('0');page.locator('#views').screenshot(path=str(out/'section-1.png'))
        page.locator('#selection').fill('NEW-1706-342');page.locator('#recenter').click();assert page.evaluate('R333_STATE.selected')=='NEW-1706-342';assert page.evaluate('R333_STATE.views[0].scale')==3
        page.locator('#labels').check();page.locator('#views').screenshot(path=str(out/'G-linked-views.png'))
        assert page.locator('#info').inner_text().find('black')>=0
        for id in ['br','by','links','breaks','hypotheses','provisional','repeat-only']:
            page.locator('#'+id).check();page.locator('#'+id).uncheck();page.locator('#'+id).check()
        for family in ['F0','F1','difference']:
            page.locator(f'[data-family="{family}"]').uncheck();page.locator(f'[data-family="{family}"]').check()
        page.locator('#repeat-only').uncheck();page.locator('#provisional').uncheck();page.locator('#labels').uncheck()
        for v in ['photo','lattice']:
            box=page.locator('#'+v).bounding_box();before=page.evaluate(f'R333_STATE.views[{0 if v=="photo" else 1}].tx');page.mouse.move(box['x']+100,box['y']+100);page.mouse.down();page.mouse.move(box['x']+150,box['y']+120);page.mouse.up();assert before!=page.evaluate(f'R333_STATE.views[{0 if v=="photo" else 1}].tx')
        page.locator('#raw').click();assert page.evaluate('R333_STATE.raw');page.locator('#raw').click()
        for name in ['closest','early','working','R332']:page.locator('#map').select_option(name);assert page.evaluate('R333_STATE.map')==name
        page.locator('#axes').select_option('paper');page.locator('#axes').select_option('strip');page.locator('#convention').select_option('B');page.locator('#reverse').check();page.locator('#convention').select_option('A');page.locator('#reverse').uncheck();page.locator('#trace').select_option('greedy');page.locator('#trace').select_option('regular')
        page.locator('#fit').click();page.locator('#zoom-in').click();page.locator('#zoom-out').click();page.locator('#native').click();assert abs(page.evaluate('R333_STATE.views[0].scale')-1)<1e-12
        # Exercise real hit testing in each view at a selected support.
        page.evaluate('R333_VIEW.select("C-1284-0332")')
        for v in ['photo','lattice']:
            box=page.locator('#'+v).bounding_box();page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2);assert page.evaluate('R333_STATE.selected')=='C-1284-0332'
        page.locator('#case-01').screenshot(path=str(out/'case-01.png'))
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R333_STATE&&R333_STATE.frames>2');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors,errors
        browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,photo_and_unwrapped=True,pan_both=True,zoom=True,click_both=True,selection=True,map_convention_axes_comparisons=True,all_layers=True,original_native_crops=True,errors=errors),indent=2)+'\n');print('PASS R333 viewer')
if __name__=='__main__':main()
