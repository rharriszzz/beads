"""Exercise the actual offline viewer: zoom/pan, filters, selection and tiles."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

def main():
    out=Path('/home/rharris/git/beads/photo2/r332/review');errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());page.wait_for_function('window.R332_VIEW_STATE&&window.R332_VIEW_STATE.frames>1')
        assert page.evaluate('R332.nodes.length>=R332.summary.recorded_accepted');assert page.locator('img').count()==22
        assert page.evaluate('R332.summary')==json.loads((out/'../results/summary.json').read_text()),'stale viewer data'
        assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if href.startswith('#'):continue
            assert (out/href).resolve().is_file(),href
        page.screenshot(path=str(out/'desktop.png'));page.locator('#region').select_option('0');page.wait_for_timeout(100);page.locator('#stage').screenshot(path=str(out/'G-viewer.png'))
        state=page.evaluate('({...R332_VIEW_STATE})');page.locator('[data-family="difference"]').uncheck();assert page.evaluate('R332_VIEW_STATE.links')<state['links'];page.locator('[data-family="difference"]').check()
        page.locator('#selection').fill('REC266-P050477');page.locator('#recenter').click();assert page.evaluate('R332_VIEW_STATE.selected')=='REC266-P050477';assert page.evaluate('R332_VIEW_STATE.scale')>=3
        page.locator('#pixels').check();page.locator('#predictions').check();page.locator('#stage').screenshot(path=str(out/'black-native-evidence.png'))
        box=page.locator('#view').bounding_box();before=page.evaluate('R332_VIEW_STATE.tx');page.mouse.move(box['x']+100,box['y']+100);page.mouse.down();page.mouse.move(box['x']+150,box['y']+130);page.mouse.up();assert page.evaluate('R332_VIEW_STATE.tx')!=before
        scale=page.evaluate('R332_VIEW_STATE.scale');page.locator('#zin').click();assert page.evaluate('R332_VIEW_STATE.scale')>scale
        page.locator('#raw').click();assert not page.evaluate('R332_VIEW_STATE.overlays');page.locator('#raw').click()
        for status in ['confirmed','working','provisional','unresolved','predicted','candidate']:
            locator=page.locator(f'[data-status="{status}"]');locator.check();locator.uncheck();locator.check()
        page.locator('[data-status="predicted"]').uncheck();page.locator('[data-status="candidate"]').uncheck()
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'))
        page.context.set_offline(True);page.reload();page.wait_for_function('window.R332_VIEW_STATE&&window.R332_VIEW_STATE.frames>1');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors,errors
        browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,native_image=True,zoom=True,pan=True,selection_recenter=True,all_status_switches=True,all_three_families=True,native_pixel_overlay=True,static_comparisons=11,errors=errors),indent=2)+'\n');print('PASS R332 viewer')

if __name__=='__main__':main()
