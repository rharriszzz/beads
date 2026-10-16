"""Real Chromium tests of navigation, native owner picking, plots and offline review."""
import subprocess,json
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from photo2.r297.common import save
from .model import ROOT,BASE,REVIEW
from .serve import open_browser

def main():
    proc=subprocess.Popen([str(REVIEW/'launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,text=True)
    line=proc.stdout.readline().strip();assert line.startswith('R305 review: '),line;url=line.split('review: ')[1];errors=[];checked=[]
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1540,'height':1120});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);page.locator('#status').filter(has_text='Ready').wait_for(timeout=60000)
            for name in ['primary','hand-minus','calibrated']:
                page.locator('#model').select_option(name)
                for k in [-40,-20,0,48,103,190,329,330,580,760,830,1000]:
                    page.locator('#index').fill(str(k));page.locator('#index').press('Tab');assert page.evaluate('selected')==k;assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(selected).projected_center)');checked.append([name,k])
                page.evaluate('selectBead(100,true)')
                for step in [10,50,-10,-50,-1]:
                    prior=page.evaluate('selected');page.locator(f'[data-step="{step}"]').click();assert page.evaluate('selected')==prior+step;assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(selected).projected_center)')
                page.locator('#slider').focus();page.locator('#slider').press('ArrowRight');assert page.evaluate('selected')==100
                for column in range(2,8):
                    buttons=page.locator(f'#groups tr td:nth-child({column+1}) button:not([disabled])')
                    if buttons.count():buttons.first.click();assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(selected).projected_center)')
                page.evaluate('selectBead(0,true)');old=page.evaluate('[...viewCenter]');z=page.evaluate('zoom');page.locator('#nextBead').click();assert page.evaluate('selected')==1;assert page.evaluate('zoom')==z;assert old!=page.evaluate('[...viewCenter]');assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(1).projected_center)')
                page.locator('#follow').uncheck();old=page.evaluate('[...viewCenter]');page.locator('#nextBead').click();assert page.evaluate('selected')==2 and page.evaluate('[...viewCenter]')==old
                c=page.locator('#combined').bounding_box();page.mouse.move(c['x']+100,c['y']+100);page.mouse.down();page.mouse.move(c['x']+130,c['y']+120);page.mouse.up();assert page.evaluate('[...viewCenter]')!=old;page.locator('#follow').check()
                page.evaluate('selectBead(0,true)');page.locator('#presetA').click();assert page.evaluate("checked('vectors')&&$('boundaries').value==='none'&&!checked('centers')&&!checked('labels')&&!checked('predicted')")
                raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                for ident in ['vectors','observed','predicted','centers','labels','contact','centerline','material','silhouette','strong','weak','ambiguous']:
                    page.locator('#'+ident).click();assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()');page.locator('#'+ident).click()
                for mode in ['all','selected','neighbors','none']:page.locator('#boundaries').select_option(mode);assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                assert page.evaluate("""()=>{const a=$('raw'),b=document.createElement('canvas');b.width=a.width;b.height=a.height;const c=b.getContext('2d');c.imageSmoothingEnabled=false;c.fillStyle='#303030';c.fillRect(0,0,b.width,b.height);c.translate(b.width/2,b.height/2);c.scale(zoom,zoom);c.translate(-viewCenter[0],-viewCenter[1]);c.drawImage(photo,0,0);return a.toDataURL()===b.toDataURL()}""")
                # Pick actual owned native pixels for widely separated addresses.
                for k in [-40,0,103,330,580,830,1000]:
                    hit=page.evaluate("""k=>{const im=ownerImages[model.name],p=ownerPixels[model.name];for(let i=0;i<p.length;i+=4)if(p[i]+256*p[i+1]-32768===k)return [i/4%im.width+model.bounds[0],Math.floor(i/4/im.width)+model.bounds[1]];return null;}""",k)
                    if hit:
                        assert page.evaluate('p=>pick(p)',hit)==k;assert page.evaluate('selected')==k
                old=page.evaluate('selected');assert page.evaluate('pick([0,0])') is None;assert page.evaluate('selected')==old
                # Actual canvas click transforms back to same native owned point.
                page.evaluate('selectBead(0,true)');hit=page.evaluate("()=>bead(0).reflection.peak");point=page.evaluate("p=>{const c=$('combined'),r=c.getBoundingClientRect();return [r.left+c.width/2+(p[0]-viewCenter[0])*zoom,r.top+c.height/2+(p[1]-viewCenter[1])*zoom]}",hit);page.mouse.click(*point);assert page.evaluate('selected')==0
                node=page.locator('#plot [data-index]').last;target=int(node.get_attribute('data-index'));node.hover();assert 'observed (' in page.locator('#tooltip').inner_text();node.click();assert page.evaluate('selected')==target;assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(selected).projected_center)')
                for ident in ['median','rms','segmented','signed']:page.locator('#'+ident).check()
                assert page.locator('#plot circle').count()>0
                for ident in ['median','rms','segmented','signed']:page.locator('#'+ident).uncheck()
                for href in page.locator('#downloads a').evaluate_all('(a)=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
            page.locator('#model').select_option('primary');page.evaluate('selectBead(0,true)');page.locator('#presetC').click();page.locator('#boundaries').select_option('selected');page.screenshot(path=str(BASE/'results/browser-desktop.png'),full_page=True);page.locator('#combined').screenshot(path=str(BASE/'results/browser-start.png'))
            for g in page.evaluate('GALLERY'):
                assert page.request.get(url+g['image']).ok;assert page.request.get(url+g['raw']).ok
            page.locator('#gallery button').last.click();assert page.evaluate('selected')==274
            page.set_viewport_size({'width':430,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'),full_page=True)
            page.goto((REVIEW/'index.html').as_uri());page.locator('#status').filter(has_text='Ready').wait_for(timeout=60000);page.evaluate('selectBead(1000,true)');assert page.evaluate('selected')==1000;browser.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(model_locations=checked,errors=errors,recentering_and_zoom=True,follow_off_panning=True,native_owner_picking=True,distant_click_rejected=True,actual_canvas_click=True,plot_hover_click=True,all_step_sizes_and_slider=True,category_navigation=True,raw_exact_and_invariant=True,presets=True,boundary_modes=True,desktop=True,narrow=True,offline=True,download_and_gallery_links=True,actual_launcher=True,windows_dispatch_mocked=True,windows_browser_actually_opened=False))
    print('R305 browser checks passed:',len(checked),'model locations')
if __name__=='__main__':main()
