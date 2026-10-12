"""Real browser audit of identical crops, native HSV and run-specific replay."""
import gzip
import json
import threading
from playwright.sync_api import sync_playwright
from .server import make_server
from .hue_r264 import ROOT, OUT, WORK, HUES
from .bounded_detect import save


def main():
    server=make_server(ROOT/'photo2/output/detection-r263-bounded',port=0)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    checks=[]
    def check(ok,text):
        assert ok,text
        checks.append(text)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1600,'height':1100})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            base=f'http://127.0.0.1:{server.server_port}'
            page.goto(base+'/hue-comparison');page.wait_for_function('window.hueTest')
            for asset in ['/r264-hsv.png','/r264-review.png','/r264-leaf.png']:
                check(page.request.get(base+asset).status==200,'Diagnostic image '+asset)
            data=json.loads((OUT/'comparison.json').read_text())
            for i,c in enumerate(data['cases']):
                page.select_option('#crop',str(i))
                check(page.locator('canvas').count()==7,'Seven original/six candidate panels: '+c['name'])
                dimensions=page.locator('canvas').evaluate_all('(cs)=>cs.map(c=>[c.width,c.height])')
                check(all(d==dimensions[0] for d in dimensions),'Identical crop scale: '+c['name'])
                check(page.evaluate('hueTest.box')==c['box'],'Exact native crop: '+c['name'])
            page.select_option('#crop','0')
            page.locator('canvas').first.hover()
            check('Native (' in page.inner_text('#readout') and 'H ' in page.inner_text('#readout'),'Native RGB / HSV hover')
            page.screenshot(path=str(OUT/'browser-comparison.png'),full_page=False)
            # Hit the same raw native pixel on an overlay and cycle overlapped IDs.
            page.select_option('#crop','2')
            canvas=page.locator('canvas').nth(3);b=canvas.bounding_box();box=data['cases'][2]['box']
            page.mouse.click(b['x']+(485-box[0]+.5)/(box[2]-box[0])*b['width'],b['y']+(669-box[1]+.5)/(box[3]-box[1])*b['height'])
            check(page.evaluate('hueTest.selected') in ('P032240','P032353'),'Support click selects overlapping pair')
            for hue in HUES:
                page.goto(base+f'/?hue={hue}&id=P032240')
                page.wait_for_function('window.regionTest?.state.replay!==null && window.regionTest?.state.ready')
                check(page.evaluate('regionTest.data.parameters.hue_stop_deg')==hue,f'Correct hue dataset {hue}')
                with gzip.open(WORK/str(hue)/'traces/P032240.json.gz','rt') as f:trace=json.load(f)
                check(page.evaluate('regionTest.state.replay')==trace,f'Exact archived trace {hue}')
                check(page.locator('#traceDownload').get_attribute('href')==f'/hue-data/{hue}/traces/P032240.json',f'Run-specific download {hue}')
                check(page.request.get(base+f'/hue-data/{hue}/coordinates.csv').status==200,f'Coordinate export {hue}')
            page.goto(base+'/hue-comparison');page.wait_for_function('window.hueTest')
            page.set_viewport_size({'width':430,'height':900})
            check(page.locator('canvas').first.bounding_box()['width']<=430,'Narrow screen comparison fits')
            check(page.request.get(base+'/hue-data/9/regions.json').status==404,'Unknown hue rejected')
            check(page.request.get(base+'/hue-data/8/traces/P999999.json').status==404,'Missing trace rejected')
            check(not errors,'No JavaScript errors')
            browser.close()
    finally:
        server.shutdown();server.server_close()
    save(OUT/'browser-checks.json',dict(count=len(checks),checks=checks))
    print(len(checks),'browser checks passed')


if __name__=='__main__':main()
