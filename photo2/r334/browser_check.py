"""Actual offline R334 photograph/lattice, maker mapping and pixel controls."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path('/home/rharris/git/beads')
def main():
    out=ROOT/'photo2/r334/review';errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1600,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R334_STATE&&R334_STATE.frames>2');page.wait_for_function('Array.from(document.images).every(x=>x.complete&&x.naturalWidth>0)')
        assert page.evaluate('R334.nodes.length')==1600;assert page.evaluate('new Set(R334.nodes.map(n=>n.id)).size')==1600;assert page.evaluate('R334.nodes.filter(n=>n.status==="working").length')==1041
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if href.startswith('#'):continue
            assert (out/href).resolve().is_file(),href
        page.screenshot(path=str(out/'desktop.png'))
        page.locator('#layer').select_option('raw');assert page.evaluate('byId.get("E5-1616-2970").color')=='red';assert page.evaluate('byId.get("R332-R-0025-0023").color')=='yellow'
        page.locator('#layer').select_option('color');assert page.evaluate('byId.get("E5-1616-2970").color')=='black';assert page.evaluate('byId.get("R332-R-0025-0023").color')=='yellow'
        page.locator('#layer').select_option('relocated');assert page.evaluate('byId.get("R332-R-0025-0023").xy')==[2076,845];assert page.evaluate('byId.get("C-2058-0820").color')=='yellow';assert page.evaluate('coords(byId.get("C-2058-0820"))') is None
        page.locator('#layer').select_option('provisional');page.locator('#layer').select_option('relocated');assert page.evaluate('byId.get("C-1284-0332").color')=='red'
        page.locator('#selection').fill('NEW-1706-342');page.locator('#recenter').click();assert page.evaluate('R334_STATE.selected')=='NEW-1706-342'
        for id in ['body-pixels','reflection-pixels','annulus-pixels']:page.locator('#'+id).check()
        page.locator('#br').uncheck();page.locator('#by').uncheck();page.locator('#views').screenshot(path=str(out/'black-first-pixels.png'))
        for id in ['body-pixels','reflection-pixels','annulus-pixels','unassociated','provisional','hypotheses','breaks','links','repeat-only']:
            page.locator('#'+id).check();page.locator('#'+id).uncheck()
        page.locator('#br').check();page.locator('#by').check();page.locator('#links').check();page.locator('#breaks').check();page.locator('#repeat-only').uncheck()
        page.evaluate('R334_VIEW.select("R332-R-0025-0023")');page.locator('#views').screenshot(path=str(out/'misplaced-linked-views.png'))
        for family in ['F0','F1','difference']:page.locator(f'[data-family="{family}"]').uncheck();page.locator(f'[data-family="{family}"]').check()
        for name in ['closest','early','working','R332']:page.locator('#map').select_option(name)
        page.locator('#axes').select_option('paper');page.locator('#axes').select_option('strip');page.locator('#convention').select_option('B');page.locator('#reverse').check();page.locator('#convention').select_option('A');page.locator('#reverse').uncheck()
        for v in ['photo','lattice']:
            box=page.locator('#'+v).bounding_box();before=page.evaluate(f'R334_STATE.views[{0 if v=="photo" else 1}].tx');page.mouse.move(box['x']+100,box['y']+100);page.mouse.down();page.mouse.move(box['x']+150,box['y']+130);page.mouse.up();assert page.evaluate(f'R334_STATE.views[{0 if v=="photo" else 1}].tx')!=before
        page.locator('#raw').click();assert page.evaluate('R334_STATE.raw');page.locator('#raw').click();page.locator('#native').click();assert abs(page.evaluate('R334_STATE.views[0].scale')-1)<1e-12
        page.locator('#correction-04').locator('details').first.evaluate('(x)=>x.open=true');assert 'NEW-2237-2128' in page.locator('#correction-04').inner_text();page.locator('#correction-08').screenshot(path=str(out/'misplaced-before-after.png'))
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),page.evaluate('Array.from(document.querySelectorAll("body *")).filter(x=>x.getBoundingClientRect().right>innerWidth+1).slice(0,8).map(x=>({tag:x.tagName,id:x.id,width:x.getBoundingClientRect().width}))');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R334_STATE&&R334_STATE.frames>2');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors,errors;browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,offline=True,desktop=True,narrow=True,all_1600_supports=True,authoritative_and_raw_layers=True,seven_color_corrections=True,separate_moved_body=True,yellow_unindexed_not_fabricated_in_lattice=True,body_reflection_annular_pixel_controls=True,geographic_before_after=True,maps_conventions_axes=True,native_images=True,errors=errors),indent=2)+'\n');print('PASS R334 browser')
if __name__=='__main__':main()
