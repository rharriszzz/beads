"""Actual offline pattern-to-occurrence-to-native-pixel review interaction."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]


def main():
    out=ROOT/'photo2/r344/review';errors=[];failed=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:failed.append(r.url))
        page.goto((out/'index.html').as_uri());page.wait_for_function('window.R344_READY')
        assert page.locator('#strict .bead').count()==208 and page.locator('#provisional .tentative').count()==9
        assert page.locator('#matrix circle').count()==2704 and page.locator('#matrix circle[data-id]:not([data-id=""])').count()==1041
        page.screenshot(path=str(out/'desktop.png'))
        page.locator('#position-input').fill('83');page.locator('button',has_text='Open').click();assert page.locator('#occurrences tr').count()==8
        page.locator('#occurrences').get_by_role('button',name='R332-R-0037-0040',exact=True).click();assert 'R332-R-0037-0040' in page.locator('#photo-title').inner_text();assert page.locator('#key').inner_text().startswith('1: R332-R-0037-0040 (red)')
        page.locator('#inspector').screenshot(path=str(out/'remaining-mismatch.png'))
        page.evaluate('selectPosition(127)');assert 'strict yellow' in page.locator('#position-detail').inner_text();page.evaluate("inspect('R332-R-0125-0118',false)");assert 'Explicit R344 yellow' in page.locator('#source-detail').inner_text()
        page.locator('#old-color').check();page.locator('#old-color').uncheck();page.locator('#complete').uncheck();page.locator('#complete').check()
        page.locator('#matrix circle[data-position="29"][data-occurrence="5"]').evaluate('el=>el.dispatchEvent(new MouseEvent("click",{bubbles:true}))');assert 'NEW-1519-2976' in page.locator('#photo-title').inner_text()
        page.locator('#inspector').screenshot(path=str(out/'maker-yellow.png'))
        page.set_viewport_size({'width':390,'height':844});page.evaluate('window.scrollTo(0,0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'))
        page.context.set_offline(True);page.reload();page.wait_for_function('window.R344_READY');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors and not failed,(errors,failed);browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,offline=True,narrow=True,strict_positions=208,provisional_tentative=9,repeat_addresses=2704,photographed_addresses=1041,real_matrix_to_native_click=True,stable_local_keys=True,source_colors_preserved=True,before_after_toggle=True,errors=errors,failed_requests=failed),indent=2)+'\n')
    print('PASS R344 browser')


if __name__=='__main__':
    main()
