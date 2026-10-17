"""Actual launcher, offline review, raw invariance, recenter and all atlas assets."""
import subprocess
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save
from .analysis import OUT

def main():
    proc=subprocess.Popen([str(ROOT/'photo2/review/r310/launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,text=True);line=proc.stdout.readline().strip();assert line.startswith('R310 review: ');url=line.split('review: ')[1];errors=[];checks=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':950});page.on('pageerror',lambda e:errors.append(str(e)));assert page.goto(url).ok;page.wait_for_function('window.getReviewState && photo.complete && photo.naturalWidth>0',timeout=60000)
            for name in page.evaluate('DATA.models.map(m=>m.name)'):
                old=page.evaluate('getReviewState()');page.locator('#model').select_option(name);assert page.evaluate('getReviewState().center')==old['center'];page.locator('#home').click()
                anchor=page.evaluate('model.anchor')
                for k in [anchor,anchor-320,anchor-160,anchor-40,anchor-7,anchor+1,anchor+7,anchor+40,anchor+160,anchor+320]:
                    page.locator('#index').fill(str(k));page.locator('#index').press('Enter');state=page.evaluate('getReviewState()');assert state['index']==k;assert state['center']==page.evaluate('model.positions.find(b=>b.index===selected).projected_center');checks.append([name,k])
                page.locator('#home').click();raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                for key in ['boundaries','interiors','vectors','neighbors','axes']:
                    page.locator('#'+key).click();assert page.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw;page.locator('#'+key).click()
                assert page.evaluate("""()=>{const c=document.createElement('canvas');c.width=raw.width;c.height=raw.height;let x=c.getContext('2d'),z=+$('zoom').value;x.setTransform(z,0,0,z,c.width/2-center[0]*z,c.height/2-center[1]*z);x.imageSmoothingEnabled=false;x.drawImage(photo,0,0);return c.toDataURL()===raw.toDataURL()}""")
                page.locator('[data-step="6"]').click();assert page.evaluate('selected')==anchor+6
                old=page.evaluate('getReviewState().center');page.locator('#view').click(position={'x':130,'y':120});assert page.evaluate('getReviewState().center')!=old
                page.locator('#home').click();assert 'C-1497-0271' in page.locator('#near').inner_text();page.locator('#near button').first.click()
            for href in page.locator('a').evaluate_all('(a)=>a.map(a=>a.href)'):assert page.request.get(href).ok,href
            page.locator('img').evaluate_all('(a)=>a.forEach(x=>x.loading="eager")');page.wait_for_function('[...document.images].every(x=>x.complete && x.naturalWidth>0)',timeout=60000)
            for button in page.locator('#atlas button').all():button.click();assert page.evaluate('Number.isFinite(getReviewState().center[0])')
            page.locator('#home').click();page.evaluate('window.scrollTo(0,0)');page.screenshot(path=str(OUT/'browser-desktop.png'))
            page.set_viewport_size({'width':430,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'browser-narrow.png'))
            page.goto((ROOT/'photo2/review/r310/index.html').as_uri());page.wait_for_function('window.getReviewState && photo.complete && photo.naturalWidth>0',timeout=60000);page.locator('[data-step="7"]').click();assert page.evaluate('selected')==page.evaluate('model.anchor+7');browser.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    result=dict(passed=True,locations=checks,errors=errors,actual_launcher=True,offline=True,narrow=True,raw_native_exact=True,layer_invariance=True,click_recenter=True,model_switch_preserves_photo=True,competing_owner_buttons=True,atlas_buttons=True,all_images_loaded=True,links=True);save(OUT/'browser-check.json',result);print('R310 browser passed',len(checks),'locations')
if __name__=='__main__':main()
