"""Inspect actual R335 input keys, then test current R336 and completed evidence."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path('/home/rharris/git/beads')
def main():
    out=ROOT/'photo2/r336/review';errors=[];inputs=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1550,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((ROOT/'photo2/r335/review/index.html').as_uri());page.wait_for_function('window.R335_STATE?.ready')
        for i in range(10):
            page.evaluate('(i)=>R335_VIEW.select(R335.cases[i].id)',i);page.locator('#evidence .keys').evaluate('(x)=>x.open=true');key=page.evaluate('(i)=>R335.panels[R335.cases[i].panel].key',i);text=page.locator('#evidence .keys').inner_text();assert all(r['id'] in text for r in key);inputs.append(dict(target=page.evaluate('(i)=>R335.cases[i].id',i),key=key))
            if i in [4,5]:page.locator('#evidence').screenshot(path=str(out/f'input-R335-{i+1}.png'))
        (out/'input-review-inspection.json').write_text(json.dumps(dict(actual_page='photo2/r335/review/index.html',all_ten_keys_expanded=True,panels=inputs),indent=2)+'\n')
        page.goto((out/'index.html').as_uri());page.wait_for_function('window.R336_STATE?.ready');assert page.evaluate('R336.cases.length')==2;assert page.locator('h1').inner_text()=='Remaining row-continuation questions';page.screenshot(path=str(out/'desktop.png'))
        excluded={'E5-1499-3037','E7-2235-1306','E5-0948-2669','E5-0986-2754','R332-B-0196-0183','R332-B-0138-0130','R332-B-0098-0092','C-1979-2669','REC266-P146299','NEW-1927-2829'}
        for i in range(2):
            page.evaluate('(i)=>R336_VIEW.select(R336.cases[i].id)',i);key=page.evaluate('(i)=>R336.panels[R336.cases[i].panel].key',i);assert not {r['id'] for r in key}&excluded;page.locator('#evidence .keys').evaluate('(x)=>x.open=true');assert page.locator('#evidence .key-wrap tbody tr').count()==len(key);page.locator('#problem').screenshot(path=str(out/f'problem-{i+1}.png'))
        page.locator('#previous').click();assert page.evaluate('R336_STATE.current')=='C-1423-3004';page.locator('#next').click();assert page.evaluate('R336_STATE.current')=='C-0481-1576'
        page.locator('#zoom-in').click();assert page.locator('.stage').first.evaluate('(x)=>x.scrollWidth>x.clientWidth');stage=page.locator('.stage').first;box=stage.bounding_box();page.mouse.move(box['x']+170,box['y']+80);page.mouse.down();page.mouse.move(box['x']+50,box['y']+80);page.mouse.up();assert stage.evaluate('(x)=>x.scrollLeft')>0;page.locator('#reset').click()
        for toggle in ['annotations','links','alternatives']:page.locator('#'+toggle).uncheck();page.locator('#'+toggle).check()
        for href in page.locator('a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))'):
            if not href.startswith('#'):assert (out/href).resolve().is_file(),href
        page.goto((out/'evidence.html').as_uri());assert page.locator('input[type=checkbox]').count()==8;page.locator('input').first.check();assert page.locator('#sample-0-0').evaluate('(x)=>x.style.display')=='inline';page.locator('input').first.uncheck();page.screenshot(path=str(out/'evidence-diagnostic.png'),full_page=True)
        page.goto((out/'repairs.html').as_uri());assert page.locator('section.panel').count()==5
        page.goto((out/'index.html').as_uri());page.wait_for_function('window.R336_STATE?.ready');page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.screenshot(path=str(out/'narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_function('window.R336_STATE?.ready');assert not errors,errors;browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,actual_R335_ten_keys_inspected=True,current_primary_questions=2,excluded_or_solved_targets_absent=True,current_numbered_diagrams=True,exact_pixel_controls=True,completed_repair_panels=5,native_links=True,zoom_pan=True,next_previous=True,desktop=True,narrow=True,offline=True,errors=errors),indent=2)+'\n');print('PASS R336 browser')
if __name__=='__main__':main()
