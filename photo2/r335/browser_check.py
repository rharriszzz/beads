"""Actual offline current-problem navigation, source images, keys and masks."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path('/home/rharris/git/beads')
def main():
    out=ROOT/'photo2/r335/review';errors=[];requests=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1600,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)));page.on('requestfailed',lambda r:requests.append(r.url))
        page.goto((out/'index.html').as_uri());page.wait_for_function('window.R335_STATE?.ready')
        assert page.locator('h1').inner_text()=='Current unresolved problems'
        assert page.evaluate('R335.cases.length')==10;assert page.evaluate('R335_STATE.current')=='K-1508-3038'
        assert not page.locator('#links').is_checked();assert not page.locator('#reflection').is_checked();assert not page.locator('#annulus').is_checked()
        page.screenshot(path=str(out/'desktop.png'),full_page=False)
        for i in range(10):
            page.evaluate('(i)=>R335_VIEW.select(R335.cases[i].id)',i)
            assert page.locator('#evidence .panel').count()==1
            count=page.evaluate('(i)=>R335.panels[R335.cases[i].panel].key.length',i)
            assert page.locator('#evidence .key-wrap tbody tr').count()==count
            assert page.locator('#evidence .photograph svg image').count()==1
            assert page.locator('#evidence .diagram svg').count()==1
            if i in [0,1,4,7,8,9]:page.locator('#problem').screenshot(path=str(out/f'problem-{i+1:02}.png'))
        assert page.locator('#examples .panel').count()==2
        page.evaluate('R335_VIEW.select("K-2225-1294")');key=page.evaluate('R335.panels[R335.cases[1].panel].key');assert next(x for x in key if x['id']=='E7-2235-1306')['color']=='black'
        for toggle in ['links','alternatives','traces','annulus','reflection','annotations']:
            page.locator('#'+toggle).check();page.locator('#'+toggle).uncheck()
        page.locator('#annotations').check();page.locator('#alternatives').check();page.locator('#annulus').check();page.locator('#reflection').check();page.locator('#evidence').screenshot(path=str(out/'native-pixel-diagnostic.png'))
        page.locator('#annulus').uncheck();page.locator('#reflection').uncheck()
        page.locator('#zoom-in').click();assert page.evaluate('R335_STATE.zoom')>1
        stage=page.locator('#evidence .stage');assert stage.evaluate('(x)=>x.scrollWidth>x.clientWidth')
        box=stage.bounding_box();page.mouse.move(box['x']+180,box['y']+100);page.mouse.down();page.mouse.move(box['x']+70,box['y']+100);page.mouse.up();assert stage.evaluate('(x)=>x.scrollLeft')>0
        page.locator('#reset').click();assert page.evaluate('R335_STATE.zoom')==1
        page.locator('#next').click();assert page.evaluate('R335_STATE.current')=='NEW-946-2684';page.locator('#previous').click();assert page.evaluate('R335_STATE.current')=='K-2225-1294'
        page.locator('#evidence .keys').evaluate('(x)=>x.open=true');page.locator('#evidence .pick').first.click();assert 'K-2225-1294' in page.locator('#selected-info').inner_text()
        page.locator('#additional').evaluate('(x)=>x.open=true');name=page.evaluate('R335.additional.find(x=>x.id==="R332-B-0017-0020").name');page.locator('#extra-select').select_option(name);assert page.evaluate('R335_STATE.current')=='R332-B-0017-0020';assert not page.locator('#question').is_visible()
        # All targets, comparison images and links are local files and readable.
        for image in page.evaluate('Object.values(R335.panels).flatMap(p=>[p.image,p.body_image])'):assert (out/image).is_file(),image
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if href.startswith('#'):continue
            assert (out/href).resolve().is_file(),href
        page.set_viewport_size({'width':390,'height':844});page.evaluate('R335_VIEW.select("K-1508-3038")');page.evaluate('scrollTo(0,0)');assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),page.evaluate('document.documentElement.scrollWidth');page.screenshot(path=str(out/'narrow.png'))
        page.locator('#zoom-in').click();assert page.locator('#evidence .stage').evaluate('(x)=>x.scrollWidth>x.clientWidth')
        page.context.set_offline(True);page.reload();page.wait_for_function('window.R335_STATE?.ready');assert not errors,errors;assert not requests,requests
        browser.close()
    receipt=dict(passed=True,default_current_layer=True,primary_problems=10,all_numbered_keys=True,local_native_images=True,corrected_black_blockers=True,comparisons_current=True,next_previous=True,zoom_pan=True,optional_reflection_and_intensity_pixels=True,no_forced_extra_questions=True,desktop=True,narrow=True,offline=True,errors=errors)
    (out/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS R335 browser')
if __name__=='__main__':main()
