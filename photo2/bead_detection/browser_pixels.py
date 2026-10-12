"""Real Chromium checks for R261 pixel replay; never writes user review records."""
import argparse
import json
from pathlib import Path
import threading
import numpy as np
from playwright.sync_api import sync_playwright
from .pixel_detect import ROOT, save
from .server import make_server


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,default=ROOT/'photo2/output/detection-r261');ap.add_argument('--output',type=Path,default=ROOT/'photo2/review/r261');args=ap.parse_args()
    work=args.work;out=args.output;out.mkdir(parents=True,exist_ok=True);server=make_server(work,port=0)
    threading.Thread(target=server.serve_forever,daemon=True).start();checks=[]
    def check(ok,msg):
        assert ok,msg
        checks.append(msg);print('PASS',msg,flush=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1500,'height':1040});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            url=f'http://127.0.0.1:{server.server_port}';page.goto(url);page.wait_for_function('window.regionTest?.state.ready',timeout=60000)
            data=json.loads((work/'regions.json').read_text());ordered=sorted(data['regions'],key=lambda r:(-r['pixel_count'],r['id']))
            state=lambda:page.evaluate('({selected:regionTest.state.selected,view:regionTest.state.view,count:regionTest.state.count,stop:regionTest.state.stop,visible:regionTest.state.visible.length,replaying:regionTest.state.replaying})')
            check(state()['visible']==len(ordered),'All retained supports loaded')
            check(page.locator('input[type=checkbox]').count()==0,'Old optional layers removed')
            page.screenshot(path=str(out/'browser-whole.png'))
            for button,index in [('largest',0),('smallest',-1),('median',len(ordered)//2)]:
                page.click('#'+button);page.wait_for_function('regionTest.state.replay!==null');check(state()['selected']==ordered[index]['id'],button+' native-area selection')
            page.click('#next');check(state()['selected']==ordered[len(ordered)//2+1]['id'],'Next by size');page.click('#previous');check(state()['selected']==ordered[len(ordered)//2]['id'],'Previous by size')
            target=next(r for r in ordered if r['id']=='P128275')
            page.fill('#jump',target['id'][1:]);page.locator('#jump').press('Enter');page.wait_for_function('regionTest.state.replay!==null')
            check(state()['selected']==target['id'],'Numeric ID selects the R261 namespace')
            check('Area centroid' in page.inner_text('#details') and 'Bright-patch centroid' in page.inner_text('#details'),'Coordinates distinguished in details')
            trace=page.evaluate('regionTest.state.replay');page.click('#reset');check(state()['count']==0,'Reset begins before seed acceptance')
            for i in range(1,5):
                page.click('#step');check(state()['count']==i,'One pixel per step '+str(i))
                a=trace['accepted'][i-1];check(f'({a[0]}, {a[1]})' in page.inner_text('#pixelInfo') and str(a[3]) in page.inner_text('#pixelInfo'),'Exact accepted pixel and brightness '+str(i))
            page.locator('#frame').fill(str(len(trace['accepted'])));page.locator('#frame').dispatch_event('input');check(state()['count']==len(trace['accepted']),'Slider reaches every acceptance')
            page.click('#stopNext');check(state()['stop']==0,'First stop selectable')
            stop=trace['stops'][0];check(state()['count']==stop[8],'Stop navigation restores its exact growth time');check(f'({stop[0]}, {stop[1]})' in page.inner_text('#stopInfo') and stop[7] in page.inner_text('#stopInfo') and 'HSV' in page.inner_text('#stopInfo'),'Exact stopped pixel, reason, brightness and HSV')
            page.locator('#stopIndex').fill(str(len(trace['stops'])));page.locator('#stopIndex').dispatch_event('change');check(state()['stop']==len(trace['stops'])-1,'Last stopped path available without truncation')
            page.click('#stopPrevious');check(state()['stop']==len(trace['stops'])-2,'Previous stop event')
            page.click('#reset');page.click('#play');page.wait_for_function('regionTest.state.count>=3');page.click('#play');n=state()['count'];page.wait_for_timeout(180);check(state()['count']==n,'Animation pauses exactly')
            page.click('#final');check(not state()['replaying'],'Final support hides pre-retreat fill')
            page.click('#reset');page.click('#step');page.click('#stopNext');page.locator('#stopInfo').scroll_into_view_if_needed();page.screenshot(path=str(out/'browser-replay.png'))
            page.locator('#fit').scroll_into_view_if_needed();rect=page.locator('#photo').bounding_box();pivot={'x':300,'y':350};before=page.evaluate('(p)=>regionTest.toSource(p)',pivot)
            page.mouse.move(rect['x']+pivot['x'],rect['y']+pivot['y']);page.mouse.wheel(0,-230);page.wait_for_timeout(100);after=page.evaluate('(p)=>regionTest.toSource(p)',pivot)
            check(np.linalg.norm([after[k]-before[k] for k in ['x','y']])<1e-8,'Zoom preserves native pointer coordinate')
            before=state()['view'];page.mouse.move(rect['x']+400,rect['y']+300);page.mouse.down();page.mouse.move(rect['x']+451,rect['y']+337,steps=5);page.mouse.up();after=state()['view'];check(abs(after['x']-before['x']-51)<1e-8 and abs(after['y']-before['y']-37)<1e-8,'Pan follows pointer exactly')
            page.evaluate('(id)=>regionTest.select(id)',target['id']);screen=page.evaluate('(p)=>regionTest.toScreen(p)',dict(zip(['x','y'],target['location'])));page.evaluate('regionTest.state.selected=null');page.mouse.click(rect['x']+screen['x'],rect['y']+screen['y']);check(state()['selected']==target['id'],'Click uses exact retained pixel membership')
            page.locator('#histogram rect').nth(2).click();check(page.evaluate('regionTest.state.visible.every(r=>r.pixel_count>=regionTest.state.filter[0]&&r.pixel_count<regionTest.state.filter[1])'),'Histogram filters exact native size')
            page.click('#clear');check(state()['visible']==len(ordered),'Clear restores complete retained inventory')
            page.fill('#jump','P999999');page.locator('#jump').press('Enter');check('not found' in page.inner_text('#message'),'Invalid ID explained')
            rejected=data['rejected'][0];page.fill('#jump',rejected['id']);page.locator('#jump').press('Enter');page.wait_for_function('regionTest.state.replay!==null');check('rejected' in page.inner_text('#details'),'Rejected grown support and trace inspectable')
            for endpoint in ['/regions.json','/photo.png','/size-distribution.png','/coordinates.csv',f'/traces/{target["id"]}.json']:
                check(page.request.get(url+endpoint).status==200,'Serves '+endpoint)
            check(page.request.get(url+'/traces/../../REQUEST_LOG.md').status==404,'Trace endpoint cannot traverse workspace')
            page.set_viewport_size({'width':430,'height':900});page.click('#fit');check(page.locator('#photo').bounding_box()['width']<=430,'Narrow viewport fits')
            if data['version'].startswith('r265-'):
                page.fill('#jump',target['id']);page.locator('#jump').press('Enter');page.wait_for_function('regionTest.state.replay!==null')
                trace=page.evaluate('regionTest.state.replay')
                page.click('#step');check('Straight path:' in page.inner_text('#pixelInfo'),'Straight native path is explained during replay')
                from .repaired_detect import straight_pixels
                seed=tuple(trace['accepted'][0][:2])
                check(all([trace['accepted'][j][:2] for j in ids]==[list(xy) for xy in straight_pixels(seed,tuple(trace['accepted'][i][:2]))] for i,ids in enumerate(trace['straight_path_indices'])),'Every displayed path is a straight native segment')
                index=next(i for i,d in enumerate(trace['stop_details']) if d and d.get('blocker'))
                page.locator('#stopIndex').fill(str(index+1));page.locator('#stopIndex').dispatch_event('change')
                check('Straight path blocked at' in page.inner_text('#stopInfo'),'Exact straight-path blocker is explained')
                page.screenshot(path=str(out/'browser-straight.png'))
            check(not errors,'No JavaScript runtime errors');browser.close()
    finally:server.shutdown();server.server_close()
    save(out/'browser-checks.json',dict(checks=checks,count=len(checks)))

if __name__=='__main__':main()
