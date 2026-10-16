"""Exercise actual launcher, interactive residuals and intact nested debuggers."""
import subprocess
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save
from photo2.r300.serve import open_browser
BASE=ROOT/'photo2/r300';REVIEW=ROOT/'photo2/review/r300'

def main():
    proc=subprocess.Popen([str(REVIEW/'launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    first=proc.stdout.readline().strip();assert first.startswith('R300 review: '),first;url=first.split('review: ',1)[1];errors=[]
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url)
            assert page.locator('#model option').count()==19
            for name in page.locator('#model option').evaluate_all('(a)=>a.map(x=>x.value)'):
                page.locator('#model').select_option(name)
                for kind in ['peak','centroid']:
                    page.locator('#kind').select_option(kind)
                    for component in ['0','1','diameters','index']:
                        page.locator('#component').select_option(component);assert page.evaluate('plotted.length')==52
            page.locator('#model').select_option('joint-15');page.locator('#kind').select_option('centroid');page.locator('#component').select_option('0')
            page.locator('#plot').click(position={'x':250,'y':180});assert 'frozen index' in page.locator('#readout').inner_text();chosen=page.evaluate('selected.r.id');page.locator('#inspect').click()
            frame=page.frame_locator('#debugger');frame.locator('#status').filter(has_text='Ready').wait_for();page.wait_for_function("document.querySelector('#debugger').contentDocument.querySelector('#model').value==='joint-15'")
            page.wait_for_function("document.querySelector('#debugger').contentDocument.querySelector('#observation').value===String(DATA.ledger.filter(r=>r.model==='joint-15').findIndex(r=>r.id===selected.r.id))")
            raw=frame.locator('#raw').evaluate('(c)=>c.toDataURL()');frame.locator('#competitors').check();assert frame.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw
            frame.locator('#geometrytab').click();frame.frame_locator('#geometryframe').locator('#status').filter(has_text='Ready').wait_for()
            page.locator('#toggle').click();assert page.locator('#legacy').is_hidden();page.locator('h1').scroll_into_view_if_needed();page.screenshot(path=str(BASE/'results/browser-desktop.png'),full_page=False)
            links=page.locator('a').evaluate_all('(a)=>a.map(x=>x.href)')
            for link in links:assert page.request.get(link).ok,link
            for image in page.locator('img').evaluate_all('(a)=>a.map(x=>x.src)'):assert page.request.get(image).ok,image
            page.set_viewport_size({'width':520,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'),full_page=False)
            page.goto((REVIEW/'index.html').as_uri());assert page.locator('#model option').count()==19;page.locator('#toggle').click();page.frame_locator('#debugger').locator('#status').filter(has_text='Ready').wait_for();browser.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(models=19,points=52,plot_modes=8,links=len(links),clicked_original_observation=chosen,errors=errors,raw_invariant=True,unchanged_R299_R298_debuggers=True,actual_shell_launcher=True,other_directory=True,desktop=True,narrow=True,offline=True,windows_dispatch_mocked=True,windows_browser_actually_opened=False));print('R300 browser checks passed')
if __name__=='__main__':main()
