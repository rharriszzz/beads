"""Actual Chromium integration test; requires optional playwright test dependency.

PLAYWRIGHT_BROWSERS_PATH=/tmp/beads-debugger-browsers .venv/bin/python -m photo2.bead_debugger.browser_smoke
Creates temporary reviews, never writes the user's review directory.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, tempfile, threading, time, urllib.request, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from .generate import ROOT
from .server import App,make_server


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/debugger/smoke');a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    checks=[]
    def check(condition,name):
        assert condition,name;checks.append(name);print('PASS',name,flush=True)
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        for name in ['generated','models']:(work/name).symlink_to(ROOT/'photo2/output/debugger'/name,target_is_directory=True)
        app=App(work);srv=make_server(app,port=0);thread=threading.Thread(target=srv.serve_forever,daemon=True);thread.start();url=f'http://127.0.0.1:{srv.server_port}'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);context=browser.new_context(viewport={'width':1500,'height':1000},device_scale_factor=1,accept_downloads=True);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url);page.wait_for_function('window.debuggerTest?.state.ready',timeout=120000)
                state=lambda:page.evaluate('window.debuggerTest.state')
                check(state()['k']==0,'Initial index 0 and real model loaded')
                check(page.evaluate('document.querySelector("#rawCrop").getContext("2d").getImageData(0,0,340,280).data.some(x=>x>100)'),'Raw evidence crop contains real image pixels')
                page.screenshot(path=str(a.output/'whole.png'))
                page.click('#zero');page.locator('#photoCanvas').focus()
                for k in [1,2,3]:page.keyboard.press('ArrowRight');check(state()['k']==k,f'Keyboard sequential index {k}')
                for key,expected in [('e',9),('q',3),('d',10),('a',3)]:page.keyboard.press(key);check(state()['k']==expected,f'Diagonal key {key}')
                page.keyboard.press('Home');page.keyboard.press('ArrowLeft');check(state()['k']==2695,'Negative index wraparound')
                page.keyboard.press('ArrowRight');check(state()['k']==0,'Positive index wraparound')
                hidden=page.evaluate('window.debuggerTest.models.get(window.debuggerTest.state.model).beads.find(b=>!b.area_px2).generator_index')
                page.evaluate('(i)=>window.debuggerTest.selectGI(i)',hidden);check('occluded' in page.locator('#selectionBadge').inner_text(),'Hidden bead remains navigable and explained')
                page.click('#zero')
                # Native source mapping under actual wheel and drag, with canvas CSS offset.
                rect=page.locator('#photoCanvas').bounding_box();pivot={'x':rect['width']*.42,'y':rect['height']*.46}
                before_view=state()['view']
                page.evaluate('document.querySelector("#photoCanvas").addEventListener("wheel",e=>{let r=e.currentTarget.getBoundingClientRect();window.lastWheelPivot={x:e.clientX-r.left,y:e.clientY-r.top}},{once:true})')
                page.mouse.move(rect['x']+pivot['x'],rect['y']+pivot['y']);page.mouse.wheel(0,-310);page.wait_for_timeout(150)
                actual_pivot=page.evaluate('window.lastWheelPivot')
                before={axis:(actual_pivot[axis]-before_view[axis])/before_view['scale'] for axis in ['x','y']}
                after=page.evaluate('(p)=>window.debuggerTest.toSource(p)',actual_pivot)
                check(np.linalg.norm([before['x']-after['x'],before['y']-after['y']])<1e-8,'Wheel zoom preserves exact pointer source coordinate')
                old=state()['view'];page.mouse.move(rect['x']+400,rect['y']+300);page.mouse.down();page.mouse.move(rect['x']+463,rect['y']+347,steps=6);page.mouse.up();new=state()['view']
                check(abs(new['x']-old['x']-63)<1e-8 and abs(new['y']-old['y']-47)<1e-8,'Drag pan maps exact CSS pixel delta')
                page.click('[data-tab="layers"]');page.click('#photoOnly');page.wait_for_timeout(100)
                point={'x':1346,'y':273};screen=page.evaluate('(p)=>window.debuggerTest.toScreen(p)',point)
                actual=page.evaluate('(p)=>Array.from(document.querySelector("#photoCanvas").getContext("2d").getImageData(Math.floor(p.x),Math.floor(p.y),1,1).data).slice(0,3)',screen)
                check(actual==list(app.photo.getpixel((1346,273))),'Canvas preserves native original RGB at known pixel center')
                page.click('#defaultLayers')
                obs=next(r for r in app.inventory['observations'] if r['evidence_class']=='interior')
                page.fill('#search',obs['id']);page.locator('#search').press('Enter');page.wait_for_timeout(100);check(state()['oid']==obs['id'],'Search selects fresh stable observation ID')
                pt=page.evaluate('(p)=>window.debuggerTest.toScreen(p)',{'x':obs['x'],'y':obs['y']});page.mouse.click(rect['x']+pt['x'],rect['y']+pt['y']);check(state()['oid']==obs['id'],'Actual canvas click selects observation marker')
                # Toggle all non-photo layers, exercising actual data and lazy-load endpoints.
                old=state();
                for box in page.locator('#layerList input').all():box.check()
                page.wait_for_function('document.querySelector("#fftDetails").textContent.includes("R250")',timeout=60000);page.wait_for_timeout(100)
                check(state()['view']==old['view'] and state()['gi']==old['gi'],'All overlay toggles preserve zoom/pan and selection')
                check(page.locator('#fftDetails').inner_text().find('wavelength')>=0,'FFT diagnostic layer has real candidates')
                perf=page.evaluate('()=>{let t=[];for(let i=0;i<30;i++){window.debuggerTest.draw();t.push(window.debuggerTest.state.stats.ms)}return t.sort((a,b)=>a-b)}')
                check(perf[15]<100,'All-layer draw median below 100 ms')
                check(state()['stats']['labels']<500,'Dense labels collision-culled below 500 in zoomed viewport')
                page.screenshot(path=str(a.output/'all-layers.png'))
                saved_view=state()['view'];selected_xy=page.evaluate('window.debuggerTest.selectedPoint()')
                page.select_option('#model','N2681_h-1_f0');page.wait_for_function('window.debuggerTest.state.model==="N2681_h-1_f0"');check(state()['h']==-1 and state()['view']==saved_view,'Opposing helicity switch preserves viewport')
                check(page.evaluate('window.debuggerTest.selectedPoint()')==selected_xy,'Model switch preserves selected photographic observation')
                page.select_option('#model','N2674_h+1_f0');page.wait_for_function('window.debuggerTest.state.model==="N2674_h+1_f0"');check(state()['n']==2674,'Alternative count model available')
                page.select_option('#model','N2696_h+1_f0');page.wait_for_function('window.debuggerTest.state.model==="N2696_h+1_f0"')
                model_bytes_before={mid:hashlib.sha256((work/'models'/f'{mid}.json').read_bytes()).hexdigest() for mid in app.cache}
                generated_before={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (work/'generated').iterdir() if f.is_file()}
                page.click('[data-tab="review"]');page.click('#confirmOrigin');page.wait_for_function('window.debuggerTest.state.k===0');check(state()['oid']==obs['id'],'Explicit fresh observation origin without legacy identity import')
                page.select_option('#action','index-neighbor-incorrect');page.fill('#note','Smoke test: neighboring index is incorrect.');page.fill('#alternative','k+6')
                page.keyboard.down('Shift');page.mouse.click(rect['x']+500,rect['y']+350);page.keyboard.up('Shift');check('Correction position:' in page.locator('#clicked').inner_text(),'Shift-click records native correction position')
                with page.expect_response('**/api/review'):page.click('#saveReview')
                page.wait_for_function('document.querySelector("#progress").textContent.startsWith("1 / ")');check(len(app.reviews.read()['reviews'])==1,'Review saves independently with count')
                r=app.reviews.read()['reviews'][0];check(r['clicked_position'] is not None and r['model_version']==state()['version'],'Review binds model version, observation and coordinates')
                check(all(hashlib.sha256((work/'models'/f'{mid}.json').read_bytes()).hexdigest()==h for mid,h in model_bytes_before.items()) and all(hashlib.sha256((work/'generated'/name).read_bytes()).hexdigest()==h for name,h in generated_before.items()),'Review leaves model predictions and independent generation byte-identical')
                with page.expect_download() as info:page.click('#export')
                export=info.value.path()
                with zipfile.ZipFile(export) as z:
                    doc=json.loads(z.read('debug-record.json'));crop=Image.open(io.BytesIO(z.read('original-crop.png')))
                    check(doc['note']==r['note'] and doc['observation']['id']==obs['id'],'Debug ZIP retains note and detector provenance')
                    check(np.array_equal(np.asarray(crop),np.asarray(app.photo.crop(doc['crop_box']))),'Debug ZIP crop is pixel-exact original')
                with page.expect_download() as info:page.locator('a[href="/api/backup"]').click()
                backup=Path(info.value.path());doc=json.loads(backup.read_text());check(doc['reviews'][0]['id']==r['id'],'Downloadable backup includes saved review')
                page.locator('#import').set_input_files(str(backup));page.wait_for_timeout(500);check(len(app.reviews.read()['reviews'])==1,'Backup import deduplicates records')
                page.click('#unchecked');check(state()['k']==1,'Next unchecked advances sequential review')
                page.fill('#note','Unsaved finding draft survives reload');page.evaluate('window.debuggerTest.flush()');expected=state();page.reload();page.wait_for_function('window.debuggerTest?.state.ready');check(state()['gi']==expected['gi'] and state()['view']==expected['view'],'Page restart restores index and viewport')
                page.click('[data-tab="review"]');check(page.input_value('#note')=='Unsaved finding draft survives reload','Draft restores across page restart')
                from .store import ReviewStore
                restored=ReviewStore(work/'reviews',app.manifest['image_sha256']);check(len(restored.read()['reviews'])==1 and restored.read()['session']['gi']==expected['gi'],'Server store restart restores findings and place')
                page.click('[data-tab="layers"]');page.click('#defaultLayers');page.click('[data-tab="review"]');page.screenshot(path=str(a.output/'review.png'))
                # Read every diagnostic reference to catch broken links.
                page.click('[data-tab="diagnostics"]')
                for href in page.locator('#diagnostics a').evaluate_all('(a)=>a.map(x=>x.getAttribute("href"))'):
                    response=context.request.get(url+href);check(response.ok,'Diagnostic link '+href)
                check(not errors,'No browser JavaScript errors')
                summary=dict(checks=checks,draw_median_ms=perf[15],draw_p95_ms=perf[28],browser_errors=errors,photo_size=list(app.photo.size),models=list(app.cache),review_revisions=len(list((work/'reviews').glob('revision-*.json'))))
                (a.output/'verification.json').write_text(json.dumps(summary,indent=2)+'\n');browser.close()
        finally:srv.shutdown();srv.server_close();thread.join()
if __name__=='__main__':main()
