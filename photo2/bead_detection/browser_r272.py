"""Minimal viewer navigation checks in Chromium, including direct file opening."""
import json
from playwright.sync_api import sync_playwright
from .experiment_r272 import ROOT,OUT,save

def main():
    data=json.load(open(OUT/'inventory.json'));beads=data['beads'];checks=[]
    def check(ok,msg):assert ok,msg;checks.append(msg);print('PASS',msg,flush=True)
    asc=sorted(beads,key=lambda b:(b['region']['pixel_count'],b['id']));desc=sorted(beads,key=lambda b:(-b['region']['pixel_count'],b['id']))
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport=dict(width=1450,height=950),device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((ROOT/'photo2/trusted_inventory_r272/index.html').as_uri());page.wait_for_function('window.beadViewer?.state.ready');check(page.locator('#message').inner_text()=='','Direct-file viewer loads original photo and inventory')
        page.screenshot(path=str(OUT/'viewer-whole.png'))
        check(page.evaluate('beadViewer.data.beads.length')==len(beads),'Complete inventory loaded')
        check(page.evaluate('beadViewer.ordered().map(b=>b.id)')==[b['id'] for b in asc],'Ascending exact mask size, ID tie-break')
        page.click('#largest');check(page.evaluate('beadViewer.state.selected')==desc[0]['id'],'Largest region selected');check(page.evaluate('beadViewer.ordered().map(b=>b.id)')==[b['id'] for b in desc],'Descending exact mask size, same ID tie-break')
        page.screenshot(path=str(OUT/'viewer-largest.png'));check(page.locator('#previous').is_disabled(),'Previous disabled at first rank')
        page.click('#next');check(page.evaluate('beadViewer.state.selected')==desc[1]['id'],'Next uses selected descending ordering');page.click('#previous');check(page.evaluate('beadViewer.state.selected')==desc[0]['id'],'Previous reverses one descending step')
        page.click('#smallest');check(page.evaluate('beadViewer.state.selected')==asc[0]['id'],'Smallest region selected');page.screenshot(path=str(OUT/'viewer-smallest.png'))
        n=(len(beads)+1)//2;page.fill('#nth',str(n));page.click('#nthSmallest');check(page.evaluate('beadViewer.state.selected')==asc[n-1]['id'],'Nth smallest uses one-based rank');page.screenshot(path=str(OUT/'viewer-median.png'))
        page.click('#nthLargest');check(page.evaluate('beadViewer.state.selected')==desc[n-1]['id'],'Nth largest uses one-based rank');page.click('#next');check(page.evaluate('beadViewer.state.selected')==desc[n]['id'],'Next follows Nth largest ordering')
        for v in ('0','1.5',str(len(beads)+1)):
            before=page.evaluate('beadViewer.state.selected');page.fill('#nth',v);page.click('#nthSmallest');check(page.evaluate('beadViewer.state.selected')==before and 'Enter N' in page.locator('#message').inner_text(),'Invalid N '+v+' rejected without selection change')
        target=asc[len(beads)//3];page.fill('#jump',target['id']);page.locator('#jump').press('Enter');check(page.evaluate('beadViewer.state.selected')==target['id'],'ID jump selects correct stable ID')
        text=page.locator('#details').inner_text();check(all(str(v) in text for v in (target['id'],target['color'],target['region']['pixel_count'],target['bright_patch']['pixel_count'])),'Details show ID, color and exact region/patch counts');check('Relative luminance' in text and 'centroid' in text,'Brightness and both centroids displayed')
        box=target['region']['bbox'];s=page.evaluate('beadViewer.state');check(abs((box[0]+box[2])/2*s['scale']+s['tx']-s['width']/2)<1e-6 and abs((box[1]+box[3])/2*s['scale']+s['ty']-s['height']/2)<1e-6,'Selection centers the region');check(s['scale']>1,'Selection zooms in')
        page.fill('#jump','not-a-bead');page.locator('#jump').press('Enter');check(page.evaluate('beadViewer.state.selected')==target['id'] and 'No accepted' in page.locator('#message').inner_text(),'Unknown ID is harmless')
        page.click('#fit');check(page.evaluate('beadViewer.state.scale')<1,'Fit photo works');page.click('#zoomIn');before=page.evaluate('beadViewer.state.scale');page.click('#zoomOut');check(page.evaluate('beadViewer.state.scale')<before,'Zoom buttons work')
        stage=page.locator('#photo').bounding_box();page.mouse.move(stage['x']+200,stage['y']+200);before=page.evaluate('beadViewer.state.scale');page.mouse.wheel(0,-150);page.wait_for_timeout(150);check(page.evaluate('beadViewer.state.scale')>before,'Wheel zoom works')
        before=page.evaluate('[beadViewer.state.tx,beadViewer.state.ty]');page.mouse.move(stage['x']+200,stage['y']+200);page.mouse.down();page.mouse.move(stage['x']+240,stage['y']+220);page.mouse.up();after=page.evaluate('[beadViewer.state.tx,beadViewer.state.ty]');check(abs(after[0]-before[0]-40)<1 and abs(after[1]-before[1]-20)<1,'Drag pans without selecting')
        check(page.evaluate('beadViewer.data.beads.every(b=>beadViewer.hit(b.brightest.x+.5,b.brightest.y+.5)?.id===b.id)'),'Every brightest pixel hits its exact native mask')
        # Actual pointer click on a rendered native-mask pixel.
        page.evaluate('(id)=>beadViewer.select(id)',target['id']);s=page.evaluate('beadViewer.state');px=stage['x']+(target['brightest']['x']+.5)*s['scale']+s['tx'];py=stage['y']+(target['brightest']['y']+.5)*s['scale']+s['ty'];page.evaluate('(id)=>{beadViewer.state.selected=id}',asc[0]['id'] if asc[0]['id']!=target['id'] else asc[-1]['id']);page.mouse.click(px,py);check(page.evaluate('beadViewer.state.selected')==target['id'],'Canvas click selects region')
        page.locator('#overlays').uncheck();check(not page.locator('#overlays').is_checked(),'Original photo can be viewed without overlays');page.screenshot(path=str(OUT/'viewer-photo-only.png'));page.locator('#overlays').check()
        page.fill('#nth',str(len(beads)));page.click('#nthSmallest');check(page.locator('#next').is_disabled(),'Next disabled at final rank')
        check(page.locator('button').count()==10 and page.locator('select').count()==0,'Only the requested navigation and zoom controls')
        page.set_viewport_size(dict(width=650,height=850));page.wait_for_timeout(100);check(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'Narrow viewer has no horizontal page overflow')
        check(not errors,'No JavaScript errors');browser.close()
    save('browser-checks.json',dict(count=len(checks),checks=checks))
if __name__=='__main__':main()
