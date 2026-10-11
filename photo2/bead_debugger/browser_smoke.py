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
                # R257: new native calculation, global light switch, review action,
                # origin-preserving export and response race protection.
                page.evaluate('window.debuggerTest.selectGI(2164)')
                page.wait_for_function('window.debuggerTest.state.detailReady',timeout=60000)
                detail=page.evaluate('window.debuggerTest.detail')
                selected=next(b for b in detail['beads'] if b['generator_index']==2164)
                check(detail['ray_resolution_px']==1 and selected['legacy_k']==2,'Native selected/neighbor calculation preserves generator and legacy origins')
                check(selected['convergence']['1']['distance_to_adaptive_px']<.3,'Bead 2 native centroid agrees with boundary supersampling')
                check(len(detail['footprint'])>100 and 'peak_xyz' in next(b['highlight'] for b in detail['beads'] if b['highlight']),'Native ownership and 3D surface highlight calculations are nonempty')
                page.click('[data-tab="inspect"]');old=state()['view'];page.select_option('#lighting','rectangle-sharp')
                page.wait_for_function('window.debuggerTest.state.detailReady && window.debuggerTest.detail.lighting.id==="rectangle-sharp"',timeout=60000)
                check(state()['view']==old and state()['gi']==2164,'Global light switch preserves selected bead and viewport')
                check(page.locator('#surfaceDetails').inner_text().find('Reflection discrepancy')>=0,'Native coordinates, convergence and mismatch are visible in Inspect')
                page.click('#cleanFootprint')
                check([k for k,v in state()['layers'].items() if v]==['photo','nativeSurface'],'Clean footprint preset removes unrelated markers')
                page.screenshot(path=str(a.output/'r257-clean.png'))
                page.click('#comparePoints')
                check(state()['layers']['nativeCenter'] and state()['layers']['nativeCentroid'] and not state()['layers']['indices'],'Selected locations preset retains only explained physical points')
                page.click('[data-tab="layers"]')
                for name in ['nativeSurface','nativeOutward','nativeCentroid','highlightPoint','highlightRegion','observedReflection','shadowDiagnostic']:page.check('#layer-'+name)
                page.screenshot(path=str(a.output/'r257-native.png'))
                page.click('[data-tab="review"]');page.select_option('#action','lighting-mismatch');page.fill('#note','R257 test only: shared lighting mismatch')
                with page.expect_response('**/api/review'):page.click('#saveReview')
                saved=app.reviews.read()['reviews'];check(len(saved)==2 and saved[0]['id']==r['id'],'New finding action appends without rewriting R256 review history')
                with page.expect_download() as info:page.click('#export')
                with zipfile.ZipFile(info.value.path()) as z:
                    doc=json.loads(z.read('debug-record.json'));surface=doc['surface_diagnostics']
                    check(doc['lighting_id']=='rectangle-sharp' and surface['lighting']['id']=='rectangle-sharp','Debug ZIP preserves selected lighting and its calculated footprint')
                    check(doc['origin_id']!='legacy','Debug ZIP preserves explicitly changed review origin')
                    check(surface['selected_generator_index']==2164 and surface['beads'] and surface['observed_reflections'] is not None,'Debug ZIP contains 3D points, convergence, observations and uncertainties')
                page.evaluate('()=>{window.debuggerTest.selectGI(2163);window.debuggerTest.selectGI(2164);window.debuggerTest.selectGI(2165)}')
                page.wait_for_function('window.debuggerTest.state.detailReady && window.debuggerTest.detail.selected_generator_index===2165',timeout=60000)
                check(state()['gi']==2165,'Rapid navigation discards stale asynchronous surface results')
                # R258 additions run in this same temporary review workspace.
                before_reviews=app.reviews.read()['reviews'];old_versions={mid:app.model(mid)['version'] for mid in ['N2696_h+1_f0','N2674_h+1_f0','N2681_h-1_f0']}
                page.evaluate('async()=>{await window.debuggerTest.switchModel("N2696_h+1_f0");window.debuggerTest.jumpK(2)}')
                old_view=state()['view']
                page.evaluate('async()=>{await window.debuggerTest.switchModel("R258_origin_C")}')
                check(state()['view']==old_view and state()['k']==2,'R258 model switch preserves exact viewport and explicit review address')
                page.wait_for_function('window.debuggerTest.state.detailReady',timeout=90000)
                check(page.evaluate('window.debuggerTest.models.get("R258_origin_C").ownership_evidence.some(p=>p[4]===1)'),'R258 photographic ownership evidence available')
                page.click('[data-tab="layers"]');page.check('#layer-ownershipFailure');page.check('#layer-unsupported');page.check('#layer-registered')
                check(state()['layers']['registered'] and state()['layers']['ownershipFailure'],'R258 physical curve and ownership-failure layers operate')
                page.click('[data-tab="review"]');page.click('#regionDraw')
                points=[[1344,338],[1351,338],[1351,341],[1344,341]]
                rect=page.locator('#photoCanvas').bounding_box()
                for x,y in points:
                    p=page.evaluate('(p)=>window.debuggerTest.toScreen(p)',dict(x=x,y=y));page.mouse.click(rect['x']+p['x'],rect['y']+p['y'])
                page.click('#regionDraw');page.select_option('#regionColor','yellow');page.select_option('#action','location-incorrect');page.fill('#note','R258 browser test polygon, not maker evidence')
                with page.expect_response('**/api/review'):page.click('#saveReview')
                rec=app.reviews.read()['reviews'][-1]
                check(np.allclose(rec['region_polygon'],points,atol=.3),'Native-coordinate region polygon saved in review')
                check(rec['region_color']=='yellow' and rec['index_namespace']=='R258 conditional material address','Region color and index namespace preserved')
                check(app.reviews.read()['reviews'][:-1]==before_reviews,'R258 region save leaves all earlier reviews byte-equivalent')
                with page.expect_download() as info:page.click('#export')
                with zipfile.ZipFile(info.value.path()) as z:
                    exported=json.loads(z.read('debug-record.json'));check(exported['region_polygon']==rec['region_polygon'],'Debug ZIP contains the marked region')
                    check(exported['model_id']=='R258_origin_C' and exported['surface_diagnostics']['model_id']=='R258_origin_C','New model ZIP owns matching native surface diagnostics')
                page.evaluate('async()=>{await window.debuggerTest.flush()}');page.reload();page.wait_for_function('window.debuggerTest?.state.ready',timeout=90000)
                check(state()['model']=='R258_origin_C' and state()['k']==2,'R258 model and address survive reload')
                page.click('[data-tab="review"]');check(page.locator('#note').input_value()=='R258 browser test polygon, not maker evidence','Region review draft survives reload')
                check(all(app.model(mid)['version']==v for mid,v in old_versions.items()),'Historical model versions remain immutable')
                page.screenshot(path=str(a.output/'r258-region.png'))
                page.click('[data-tab="inspect"]');view_before=state()['view'];page.click('#bead2Compare')
                page.wait_for_function('window.debuggerTest.state.model==="R258_origin_C2" && window.debuggerTest.state.detailReady',timeout=120000)
                check(state()['view']==view_before and state()['k']==2,'One-click bead2 comparison selects compact C2 without moving the image')
                pixel=page.evaluate('window.debuggerTest.detail.footprint.find(p=>p[2]===window.debuggerTest.state.gi)');p=page.evaluate('(p)=>window.debuggerTest.toScreen(p)',dict(x=pixel[0],y=pixel[1]));rect=page.locator('#photoCanvas').bounding_box();page.mouse.move(rect['x']+p['x'],rect['y']+p['y'])
                check('native owner k2' in page.locator('#cursor').inner_text(),'Pointer reports the selected native pixel owner')
                page.click('#bead2Compare');page.wait_for_function('window.debuggerTest.state.model==="N2696_h+1_f0"',timeout=120000)
                check(state()['view']==view_before and state()['k']==2,'Comparison returns to old model without changing view or address')

                check(not errors,'No browser JavaScript errors')
                summary=dict(checks=checks,draw_median_ms=perf[15],draw_p95_ms=perf[28],browser_errors=errors,photo_size=list(app.photo.size),models=list(app.cache),review_revisions=len(list((work/'reviews').glob('revision-*.json'))))
                (a.output/'verification.json').write_text(json.dumps(summary,indent=2)+'\n');browser.close()
        finally:srv.shutdown();srv.server_close();thread.join()
if __name__=='__main__':main()
