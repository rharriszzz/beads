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
        page.goto((out/'index.html').as_uri());page.wait_for_function('window.R344_READY && window.R344_PAPER_READY')
        assert page.locator('#graph-paper .paper-bead').count()==1968
        assert page.locator('#graph-paper .paper-bead[data-member="true"][data-kind="strict"]').count()==208
        assert page.locator('#graph-paper .paper-bead[data-member="true"][data-kind="provisional"]').count()==208
        assert page.evaluate("Array.from(document.querySelectorAll('#graph-paper .paper-bead')).every(el=>el.querySelector('ellipse').getAttribute('fill')===palette[P.entries[+el.dataset.position][el.dataset.kind+'_color']])")
        assert page.evaluate("(()=>{const xy=k=>{const e=document.querySelector('#graph-paper .paper-bead[data-kind=\"strict\"][data-copy=\"0\"][data-k=\"'+k+'\"] ellipse');return [+e.getAttribute('cx'),+e.getAttribute('cy')]},p=xy(0);return [[1,48,0],[6,-24,-32],[7,24,-32]].every(([k,x,y])=>xy(k)[0]-p[0]===x&&xy(k)[1]-p[1]===y)})()")
        assert page.locator('#paper-seam').is_checked()
        assert page.locator('#graph-paper .strip-side').count()==4
        assert page.locator('#graph-paper .repeat-cut').count()==4
        assert page.evaluate("[...document.querySelectorAll('#graph-paper .strip-side, #graph-paper .repeat-cut')].every(e=>e.getAttribute('vector-effect')==='non-scaling-stroke'&&!e.hasAttribute('stroke-dasharray'))")
        assert page.evaluate("(()=>{for(const kind of ['strict','provisional'])for(let y=-8;y<=39;y++){const es=[...document.querySelectorAll('#graph-paper .paper-bead')].filter(e=>e.dataset.kind===kind&&+e.dataset.row===y).sort((a,b)=>+a.dataset.cx-+b.dataset.cx);const b=es.filter(e=>e.dataset.side==='basic');if(es.filter(e=>e.dataset.side==='left').length!==7||es.filter(e=>e.dataset.side==='right').length!==7||es.length!==b.length+14)return false;for(let j=1;j<es.length;j++)if(+es[j].dataset.k-+es[j-1].dataset.k!==1||+es[j].dataset.cx-+es[j-1].dataset.cx!==48)return false}return true})()")
        target=page.locator('#graph-paper .paper-bead[data-member="true"][data-position="83"][data-kind="strict"] ellipse')
        target.click();assert 'Position 83' in page.locator('#position-detail').inner_text();assert page.locator('.bead.chosen[data-position="83"]').count()==2
        page.locator('#strict .bead[data-position="127"]').click();assert page.locator('#graph-paper .paper-selected[data-position="127"]').count()>=2
        width=page.evaluate('paperBox[2]');page.get_by_role('button',name='Zoom +',exact=True).click();assert page.evaluate('paperBox[2]')<width
        page.get_by_role('button',name='Fit',exact=True).click();assert page.evaluate('paperBox[2]')==width
        page.locator('#graph-paper').scroll_into_view_if_needed();box=page.locator('#graph-paper').bounding_box();start=page.evaluate('paperBox[0]');page.mouse.move(box['x']+box['width']-8,box['y']+box['height']-8);page.mouse.down();page.mouse.move(box['x']+box['width']-48,box['y']+box['height']-28);page.mouse.up();assert page.evaluate('paperBox[0]')!=start;page.get_by_role('button',name='Fit',exact=True).click()
        page.locator('#paper-labels').select_option('position');assert page.locator('#graph-paper .paper-bead text').count()==1968;page.locator('#paper-labels').select_option('ab');assert page.locator('#graph-paper .paper-bead[data-copy="0"][data-k="0"][data-kind="strict"] text').text_content()=='(0,0)';page.locator('#paper-labels').select_option('k');page.locator('#paper-labels').select_option('none')
        page.locator('#paper-guides').check();page.locator('#paper-guides').uncheck();page.locator('#paper-seam').check()
        assert page.locator('#graph-paper .paper-bead').count()==1968 and page.locator('#graph-paper .paper-bead[data-member="true"]').count()==416
        assert page.evaluate("(()=>{const xy=s=>{const e=document.querySelector('#graph-paper .paper-bead[data-kind=\"strict\"][data-copy=\"'+s+'\"][data-k=\"6\"] ellipse');return [+e.getAttribute('cx'),+e.getAttribute('cy')]},a=xy(0),b=xy(1);return b[0]-a[0]===312&&b[1]-a[1]===32})()")
        assert page.evaluate("(()=>{const xy=s=>{const e=document.querySelector('#graph-paper .paper-bead[data-kind=\"strict\"][data-copy=\"'+s+'\"][data-k=\"19\"] ellipse');return [+e.getAttribute('cx'),+e.getAttribute('cy')]},a=xy(0),b=xy(2);return b[0]-a[0]===624&&b[1]-a[1]===64})()")
        assert page.evaluate("(()=>{const colors=new Map();for(const el of document.querySelectorAll('#graph-paper .paper-bead')){const key=el.dataset.kind+':'+el.dataset.k,fill=el.querySelector('ellipse').getAttribute('fill');if(colors.has(key)&&colors.get(key)!==fill)return false;colors.set(key,fill)}return true})()")
        page.locator('#graph-paper').screenshot(path=str(out/'graph-paper-seams.png'));page.locator('#paper-seam').uncheck();assert page.locator('#graph-paper .paper-bead').count()==624;assert page.locator('#graph-paper .strip-side').count()==4;page.locator('#graph-paper').screenshot(path=str(out/'graph-paper-basic.png'));page.locator('#paper-seam').check()
        page.locator('#paper-kind').select_option('strict');assert page.locator('#graph-paper .paper-bead').count()==984;page.locator('#paper-kind').select_option('both')
        page.locator('#graph-paper').screenshot(path=str(out/'graph-paper.png'))
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
        page.context.set_offline(True);page.reload();page.wait_for_function('window.R344_READY && window.R344_PAPER_READY');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');assert not errors and not failed,(errors,failed);browser.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,offline=True,narrow=True,strict_positions=208,provisional_tentative=9,repeat_addresses=2704,photographed_addresses=1041,real_matrix_to_native_click=True,stable_local_keys=True,source_colors_preserved=True,before_after_toggle=True,graph_to_string_click=True,string_to_graph_click=True,graph_chosen_members_per_view=208,graph_canonical_points_per_view=312,same_k_seam_copy_colors=True,rendered_positive_1_6_7_directions=True,rendered_seam_right_down=True,zoom_and_drag_pan=True,optional_indices_coordinates_guides_and_sides=True,seven_left_and_seven_right_every_row=True,display_points_per_view=984,rendered_second_seam=True,solid_sides_and_start_end_cuts=True,errors=errors,failed_requests=failed),indent=2)+'\n')
    print('PASS R344 browser')


if __name__=='__main__':
    main()
