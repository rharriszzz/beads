"""Actual localhost/offline/native-picking/raw-layer review contracts."""
import subprocess
import numpy as np
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,read,save

OUT=ROOT/'photo2/r311/results/campaign'

def main():
    server=subprocess.Popen([str(ROOT/'photo2/review/r311/launch.sh'),'--port','0'],cwd='/tmp',stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    line=server.stdout.readline().strip();assert line.startswith('R311 review: '),line
    url=line.split('review: ',1)[1];errors=[];checks=[];picked=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
            assert page.goto(url).ok
            page.wait_for_function('window.R311View && image.complete && image.naturalWidth>0 && ownerReady',timeout=120000)
            names=page.evaluate('R311.models.map(m=>m.name)')
            for name in names:
                before=page.evaluate('R311View.viewport');page.locator('#model').select_option(name)
                page.wait_for_function('ownerReady && owners.complete')
                assert page.evaluate('R311View.viewport')==before
                for location in ['0','1','2','5','required','boundary','worst','whole']:
                    page.locator('#location').select_option(location)
                    assert page.evaluate('R311View.viewport.every(Number.isFinite)')
                    raw=page.locator('#photo').evaluate('c=>c.toDataURL()')
                    for toggle in ['boundaries','centers','interiors','reflections','raw']:
                        page.locator('#'+toggle).click();assert page.locator('#photo').evaluate('c=>c.toDataURL()')==raw
                        page.locator('#'+toggle).click()
                    checks.append([name,location])
                page.locator('#location').select_option('0')
                # Pick a known native pixel in the original support, independently
                # read from the saved owner raster rather than nearest-center code.
                raster=np.load(OUT/'exports'/f'{name}-raster.npz')
                model=read(OUT/'exports'/f'{name}.json.gz');target=model['first_errors'][0];k=target['modal_index']
                xx,yy=np.where(raster['address'][220:310,1450:1550]==k)[1],np.where(raster['address'][220:310,1450:1550]==k)[0]
                assert len(xx);px,py=int(xx[len(xx)//2]+1450),int(yy[len(yy)//2]+220)
                v=page.evaluate('R311View.transform')
                page.locator('#overlay').click(position={'x':(px+.25)*v['scale']+v['offset'][0],'y':(py+.25)*v['scale']+v['offset'][1]})
                assert page.evaluate('selected')==k,(name,k,page.evaluate('selected'));picked.append([name,px,py,k])
                old=page.evaluate('selected');page.locator('[data-step="7"]').click();assert page.evaluate('selected')==old+7
                page.locator('#follow').check();page.locator('[data-step="1"]').click();b=page.evaluate('current.positions.find(b=>b.index===selected).projected_center');v=page.evaluate('R311View.viewport');assert abs(v[0]+v[2]/2-b[0])<1e-8
                page.locator('#follow').uncheck();page.locator('#location').select_option('0')
                for href in page.locator('a').evaluate_all('a=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
                page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)')
            page.screenshot(path=str(OUT/'browser-desktop.png'))
            page.set_viewport_size({'width':430,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(OUT/'browser-narrow.png'))
            assert page.goto(url.replace('index.html','maps.html')).ok
            page.wait_for_function('[...document.images].every(i=>i.complete && i.naturalWidth>0)',timeout=120000)
            for href in page.locator('a').evaluate_all('a=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
            page.goto((ROOT/'photo2/review/r311/index.html').as_uri())
            page.wait_for_function('window.R311View && image.complete && image.naturalWidth>0 && ownerReady',timeout=120000)
            page.locator('#location').select_option('5');page.locator('#raw').check();assert page.locator('#overlay').evaluate('c=>c.getContext("2d").getImageData(0,0,c.width,c.height).data.every(x=>x===0)')
            browser.close()
    finally:server.terminate();server.wait(timeout=10)
    assert not errors,errors
    save(OUT/'browser-check.json',dict(passed=True,actual_launcher=True,offline=True,narrow=True,raw_layer_invariance=True,native_owner_picking=picked,locations=checks,links_and_images=True,errors=errors))
    print('R311 browser passed',len(checks),'locations')
if __name__=='__main__':main()
