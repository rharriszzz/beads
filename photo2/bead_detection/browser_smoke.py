"""Real Chromium tests. Read-only viewer; no production review writes."""
import argparse
import json
import threading
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
from .server import make_server
from .detect import ROOT


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'photo2/output/detection-r259/browser');a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    work=ROOT/'photo2/output/detection-r259';server=make_server(work,port=0)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();checks=[]
    def check(ok,message):
        assert ok,message
        checks.append(message);print('PASS',message,flush=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1480,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            url=f'http://127.0.0.1:{server.server_port}'
            page.goto(url);page.wait_for_function('window.regionTest?.state.ready')
            state=lambda:page.evaluate('({...window.regionTest.state,visible:window.regionTest.state.visible.map(r=>({id:r.id,pixel_count:r.pixel_count}))})')
            data=json.loads((work/'regions.json').read_text());ordered=sorted(data['regions'],key=lambda r:(-r['pixel_count'],r['id']))
            check(len(state()['visible'])==len(ordered),'All retained regions loaded')
            check(page.locator('select').count()==0,'No model, lighting, index or pattern selectors')
            check(not any(page.is_checked('#'+k) for k in ['maxima','growth','rejected']),'Optional evidence starts hidden')
            page.screenshot(path=str(a.output/'whole.png'))
            for button,index in [('largest',0),('smallest',-1),('median',len(ordered)//2)]:
                page.click('#'+button);check(state()['selected']==ordered[index]['id'],button+' area selection')
            page.click('#next');check(state()['selected']==ordered[len(ordered)//2+1]['id'],'Next smaller region')
            page.click('#previous');check(state()['selected']==ordered[len(ordered)//2]['id'],'Previous larger region')
            r=ordered[len(ordered)//3];page.fill('#jump',str(int(r['id'][1:])));page.locator('#jump').press('Enter')
            check(state()['selected']==r['id'],'Jump by numeric ID')
            check(str(r['pixel_count']) in page.inner_text('#details') and 'Hue mean' in page.inner_text('#details'),'Details include area and circular HSV statistics')
            old=state();page.fill('#jump','R99999');page.locator('#jump').press('Enter');check(state()['selected']==old['selected'] and 'not found' in page.inner_text('#message'),'Invalid ID is explained without changing selection')
            rect=page.locator('#photo').bounding_box();pivot={'x':300,'y':350};before=page.evaluate('(p)=>window.regionTest.toSource(p)',pivot)
            page.mouse.move(rect['x']+pivot['x'],rect['y']+pivot['y']);page.mouse.wheel(0,-230);page.wait_for_timeout(100)
            after=page.evaluate('(p)=>window.regionTest.toSource(p)',pivot);check(np.linalg.norm([after[k]-before[k] for k in ['x','y']])<1e-8,'Wheel zoom preserves native pointer coordinate')
            old=state()['view'];page.mouse.move(rect['x']+400,rect['y']+300);page.mouse.down();page.mouse.move(rect['x']+451,rect['y']+337,steps=5);page.mouse.up();new=state()['view']
            check(abs(new['x']-old['x']-51)<1e-8 and abs(new['y']-old['y']-37)<1e-8,'Drag pan follows exact pixel delta')
            # Select a different candidate with an actual click on a saved support pixel.
            target=ordered[len(ordered)//2];page.evaluate('(id)=>window.regionTest.select(id)',target['id']);row,x1,x2=target['pixel_runs'][len(target['pixel_runs'])//2]
            screen=page.evaluate('(p)=>window.regionTest.toScreen(p)',{'x':(x1+x2)/2,'y':row});page.evaluate('window.regionTest.state.selected=null');page.mouse.click(rect['x']+screen['x'],rect['y']+screen['y']);check(state()['selected']==target['id'],'Photographic region click uses saved pixel support')
            old=state()['view'];page.locator('summary').click()
            for box in ['maxima','growth','rejected']:page.check('#'+box)
            check(state()['view']==old,'Evidence toggles preserve viewport')
            page.screenshot(path=str(a.output/'detail.png'))
            page.locator('#histogram rect').nth(8).click();visible=state()['visible'];bounds=state()['filter']
            check(all(bounds[0]<=r['pixel_count']<bounds[1] for r in visible),'Histogram click filters exact pixel-count bin')
            if visible:check(state()['selected']==visible[0]['id'],'Histogram bin immediately selects a member')
            page.click('#clear');check(len(state()['visible'])==len(ordered),'Clear histogram filter restores all regions')
            page.locator('#histogram rect').nth(2).focus();page.keyboard.press('Enter');check(state()['filter'] is not None,'Histogram bins support keyboard inspection')
            page.click('#clear');rejected=data['rejected'][0];page.fill('#jump',rejected['id']);page.locator('#jump').press('Enter');check(state()['selected']==rejected['id'] and 'rejected' in page.inner_text('#details'),'Rejected candidate ID can be inspected')
            for endpoint in ['/regions.json','/photo.png','/rank-size.csv','/size-distribution.png']:check(page.request.get(url+endpoint).status==200,'Serves '+endpoint)
            check(page.request.get(url+'/../REQUEST_LOG.md').status==404,'Server exposes only viewer artifacts')
            # Verify browser decoding matches source; no implicit ICC transform.
            expected=list(Image.open(work/'photo.png').getpixel((100,100)))
            actual=page.evaluate('''async()=>{let i=new Image();i.src='/photo.png';await i.decode();let c=document.createElement('canvas');c.width=i.width;c.height=i.height;let g=c.getContext('2d');g.drawImage(i,0,0);return Array.from(g.getImageData(100,100,1,1).data).slice(0,3)}''')
            check(actual==expected,'Browser preserves native decoded RGB')
            page.set_viewport_size({'width':430,'height':900});page.click('#fit');check(page.locator('#photo').bounding_box()['width']<=430,'Narrow-screen layout fits viewport')
            page.screenshot(path=str(a.output/'mobile.png'));check(not errors,'No JavaScript runtime errors')
            browser.close()
    finally:server.shutdown();server.server_close();thread.join()
    (a.output/'checks.json').write_text(json.dumps(dict(checks=checks,count=len(checks),errors=errors),indent=2)+'\n')


if __name__=='__main__':main()
