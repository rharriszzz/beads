"""All models/panels, layer invariance, pixel coordinates and actual launcher."""
import subprocess
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from photo2.r297.common import save
from .model import ROOT,BASE,REVIEW
from .serve import open_browser

def main():
    proc=subprocess.Popen([str(REVIEW/'launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,text=True)
    line=proc.stdout.readline().strip();assert line.startswith('R304 review: ');url=line.split('review: ')[1];errors=[];checked=[]
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1540,'height':1120});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);page.locator('#status').filter(has_text='Ready').wait_for()
            for name in ['primary','hand-minus','calibrated']:
                page.locator('#model').select_option(name)
                for panel in range(10):
                    page.locator('#panel').select_option(str(panel));assert f'Panel {panel+1}/10' in page.locator('#location').inner_text();assert page.locator('#raw').evaluate('(c)=>c.width>0 && c.height>0');checked.append([name,panel])
                # Every layer toggle must leave the raw photograph unchanged.
                page.locator('#panel').select_option('0');raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                for ident in ['observed','weak','peaks','centroids','vectors','boundaries','centers','labels','missing','centerline','contact','envelope']:
                    page.locator('#'+ident).click();assert raw==page.locator('#raw').evaluate('(c)=>c.toDataURL()');page.locator('#'+ident).click()
                # Raw canvas is exactly the corresponding nearest-scaled photo crop.
                assert page.evaluate("""()=>{const a=document.querySelector('#raw'),b=document.createElement('canvas');b.width=a.width;b.height=a.height;const c=b.getContext('2d'),z=Number(document.querySelector('#zoom').value);c.imageSmoothingEnabled=false;c.scale(z,z);c.translate(-crop[0],-crop[1]);c.drawImage(photo,0,0);return a.toDataURL()===b.toDataURL()}""")
                page.locator('#observationsList button').first.click();assert 'alternatives' in page.locator('#observationDetail').inner_text();page.locator('#nextBead').click();assert 'Index -19' in page.locator('#selectedLabel').inner_text()
                for href in page.locator('#downloads a').evaluate_all('(a)=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
            page.locator('#model').select_option('primary');page.locator('#panel').select_option('4');page.screenshot(path=str(BASE/'results/browser-desktop.png'),full_page=True)
            page.locator('#combined').screenshot(path=str(BASE/'results/browser-native-panel.png'))
            for href in page.locator('header a').evaluate_all('(a)=>a.map(x=>x.href)'):assert page.request.get(href).ok,href
            for ident in ['indexPlot','arcPlot']:assert page.locator('#'+ident).evaluate('(i)=>i.complete&&i.naturalWidth>0')
            page.set_viewport_size({'width':430,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'),full_page=True)
            page.goto((REVIEW/'index.html').as_uri());page.locator('#status').filter(has_text='Ready').wait_for();page.locator('#panel').select_option('9');assert 'Panel 10/10' in page.locator('#location').inner_text();browser.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(models_panels=checked,errors=errors,raw_invariant_all_layers=True,raw_exact_crop=True,desktop=True,narrow=True,offline=True,download_links=True,actual_launcher=True,windows_dispatch_mocked=True,windows_browser_actually_opened=False))
    print('R304 browser checks passed:',len(checked),'model/panels')

if __name__=='__main__':main()
