"""Real Chromium checks of variable-count whole-circuit navigation and raw pixels."""
import argparse,subprocess
import numpy as np
from PIL import Image,ImageOps
from pathlib import Path
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save
from photo2.r299.serve import open_browser

def check(out,launcher=False):
    out=Path(out).resolve();review=out/'review';errors=[];checked=[]
    if launcher:
        proc=subprocess.Popen([str(ROOT/'photo2/review/r307/launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,text=True)
        line=proc.stdout.readline().strip();assert line.startswith('R307 review: ');url=line.split('review: ')[1]
    else:
        from photo2.r299.serve import make_server
        import threading
        server=make_server(0);threading.Thread(target=server.serve_forever,daemon=True).start();proc=None
        url=f'http://127.0.0.1:{server.server_port}/'+str(review.relative_to(ROOT))+'/'
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1000});page.on('pageerror',lambda e:(errors.append(str(e)),print('Browser error:',e,flush=True)))
            response=page.goto(url)
            assert response and response.ok,(url,response.status if response else None)
            try:page.locator('#status').filter(has_text='Ready').wait_for(timeout=60000)
            except Exception:
                save(out/'browser-failure.json',dict(status=page.locator('#status').inner_text(),errors=errors,url=url))
                raise
            page.set_viewport_size({'width':430,'height':900})
            overflow=page.evaluate("""()=>[...document.querySelectorAll('body *')].map(e=>({tag:e.tagName,id:e.id,width:e.getBoundingClientRect().width,right:e.getBoundingClientRect().right})).filter(e=>e.right>innerWidth+1).slice(0,30)""")
            if page.evaluate('document.documentElement.scrollWidth>innerWidth'):
                save(out/'browser-layout-failure.json',dict(overflow=overflow));page.screenshot(path=str(out/'browser-layout-failure.png'),full_page=True)
                raise AssertionError(overflow)
            page.set_viewport_size({'width':1500,'height':1000})
            names=page.evaluate('DATA.models.map(x=>x.name)')
            for name in names:
                page.locator('#model').select_option(name);limits=page.evaluate('[model.positions[0].index,model.positions.at(-1).index]')
                for k in [limits[0],limits[0]+1,-101,-1,0,1,103,760,limits[1]-1,limits[1]]:
                    if not limits[0]<=k<=limits[1]:continue
                    page.locator('#index').fill(str(k));page.locator('#index').press('Tab');assert page.evaluate('selected')==k
                    assert page.evaluate('JSON.stringify(viewCenter)===JSON.stringify(bead(selected).projected_center)');checked.append([name,k])
                page.evaluate('selectBead(0,true)');raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                for ident in ['overlap','vectors','photoReference','centerline','material','centers','labels','observed','predicted']:
                    page.locator('#'+ident).click();assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()');page.locator('#'+ident).click()
                for mode in ['selected','all','neighbors','none']:
                    page.locator('#boundaries').select_option(mode);assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                assert page.evaluate("""()=>{const a=$('raw'),b=document.createElement('canvas');b.width=a.width;b.height=a.height;const c=b.getContext('2d');c.imageSmoothingEnabled=false;c.fillStyle='#303030';c.fillRect(0,0,b.width,b.height);c.translate(b.width/2,b.height/2);c.scale(zoom,zoom);c.translate(-viewCenter[0],-viewCenter[1]);c.drawImage(photo,0,0);return a.toDataURL()===b.toDataURL()}""")
                page.locator('#nextBead').click();assert page.evaluate('selected')==1
                page.locator('[data-step="50"]').click();assert page.evaluate('selected')==51
                page.locator('#slider').focus();page.locator('#slider').press('ArrowRight');assert page.evaluate('selected')==52
                page.locator('#follow').uncheck();old=page.evaluate('[...viewCenter]');page.locator('#nextBead').click();assert page.evaluate('[...viewCenter]')==old;page.locator('#follow').check()
                point=page.evaluate('model.positions.find(b=>b.reflection).reflection.peak');target=page.evaluate('model.positions.find(b=>b.reflection).index')
                assert page.evaluate('p=>pick(p)',point)==target
                assert page.evaluate('pick([0,0])') is None
                node=page.locator('#plot [data-index]').last;idx=int(node.get_attribute('data-index'));node.hover();node.click();assert page.evaluate('selected')==idx
                for ident in ['signed','median','rms','segmented']:page.locator('#'+ident).check();page.locator('#'+ident).uncheck()
                for href in page.locator('#downloads a').evaluate_all('(a)=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
            page.locator('#model').select_option('primary');page.evaluate('selectBead(-101,true)')
            point=page.evaluate('[...viewCenter]')
            for name in names:
                page.locator('#model').select_option(name);assert page.evaluate('[...viewCenter]')==point
            page.locator('#model').select_option('primary');page.evaluate('selectBead(-101,true)')
            page.locator('#overlap').uncheck();raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()');combined=page.locator('#combined').evaluate('(c)=>c.toDataURL()')
            page.locator('#overlap').check();assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()');assert combined!=page.locator('#combined').evaluate('(c)=>c.toDataURL()')
            assert 'C-1116-0328' in page.locator('#overlapDetail').inner_text();assert page.locator('#overlapDetail button').count()>2
            page.locator('#overlapDetail button').first.click();assert page.evaluate('selected') is not None
            page.locator('#model').select_option('primary');page.evaluate('selectBead(0,true)');page.locator('#presetC').click();page.locator('#photoReference').check();page.locator('#centerline').check()
            page.locator('#gallery').scroll_into_view_if_needed()
            page.locator('#gallery img').evaluate_all('(images)=>images.forEach(i=>i.loading="eager")')
            page.wait_for_function('[...document.querySelectorAll("#gallery img")].every(i=>i.complete&&i.naturalWidth>0)')
            source=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB')
            gallery=page.evaluate('GALLERY')
            for g in gallery:
                lo=np.maximum([0,0],np.floor(np.array(g['point'])-110)).astype(int);hi=np.minimum(source.size,lo+220).astype(int)
                raw=Image.open(review/g['raw']);expected=source.crop((*lo,*hi))
                assert np.array_equal(np.asarray(raw),np.asarray(expected))
                annotated=Image.open(review/g['image'])
                assert np.array_equal(np.asarray(annotated.crop((0,32,raw.width,32+raw.height))),np.asarray(raw))
            for href in page.locator('header a,#gallery a').evaluate_all('(a)=>a.map(x=>x.href)'):
                assert page.request.get(href.split('#')[0]).ok,href
            page.evaluate('window.scrollTo(0,0)')
            page.screenshot(path=str(out/'browser-desktop.png'),full_page=True)
            page.set_viewport_size({'width':430,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(out/'browser-narrow.png'),full_page=True)
            page.goto((review/'index.html').as_uri());page.locator('#status').filter(has_text='Ready').wait_for(timeout=120000);page.evaluate('selectBead(model.positions.at(-1).index,true)');assert page.evaluate('selected===model.positions.at(-1).index')
            browser.close()
    finally:
        if proc:proc.terminate();proc.wait(timeout=10)
        else:server.shutdown();server.server_close()
    assert not errors,errors
    result=dict(passed=True,models=names,locations=checked,errors=errors,raw_native_and_layer_invariant=True,original_and_geometric_axes=True,
        native_owner_pick=True,variable_count_navigation=True,step_slider_follow=True,plot_click=True,desktop=True,narrow=True,offline=True,
        geographic_model_switch=True,observed_interior_overlay_visible=True,competing_owner_buttons=True,actual_launcher=launcher,windows_dispatch_mocked=True,windows_browser_opened=False,
        gallery_images=len(gallery),gallery_native_crops_exact=True,gallery_images_loaded=True,header_and_gallery_links=True)
    save(out/'browser-check.json',result);print('R307 browser checks passed',len(checked),'locations',flush=True)

if __name__=='__main__':
    import sys
    default=ROOT/'photo2/r307/results/campaign'
    if not (default/'review/index.html').exists():default=ROOT/'photo2/r307/results/qualification'
    ap=argparse.ArgumentParser();ap.add_argument('output',type=Path,nargs='?',default=default);ap.add_argument('--launcher',action='store_true')
    argv=sys.argv[1:]
    if argv==['photo2.r307.browser_check']:argv=[]  # trusted wrapper retains its module argument
    a=ap.parse_args(argv);check(a.output,a.launcher or a.output.name=='campaign')
