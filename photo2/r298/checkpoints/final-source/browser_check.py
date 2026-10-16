"""Desktop/narrow/offline UI, actual shell launcher HTTP, mocked WSL opener."""
import json
import subprocess
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save
from .calibrate import BASE
from .serve import open_browser

def main():
    command=[str(ROOT/'photo2/review/r298/launch.sh'),'--port','0','--no-browser']
    proc=subprocess.Popen(command,cwd='/tmp',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    first=proc.stdout.readline().strip();assert first.startswith('R298 review: '),first
    url=first.split('review: ',1)[1];errors=[]
    try:
        with patch('photo2.r298.serve.shutil.which',side_effect=lambda k:'/mnt/c/Windows/powershell.exe' if k=='powershell.exe' else None),patch('photo2.r298.serve.subprocess.Popen') as spawn:
            open_browser(url);args=spawn.call_args.args[0];assert args[0]=='powershell.exe' and url in args[-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);page.wait_for_function('document.querySelector("#status").textContent.startsWith("Ready")')
            page.wait_for_function('Array.from(surfaces.values()).every(i=>i.complete&&i.naturalWidth>0)')
            for button in ['oldonly','newonly','both']:page.locator('#'+button).click()
            assert page.locator('#model option').count()==4
            for value in page.locator('#model option').evaluate_all('(a)=>a.map(x=>x.value)'):page.locator('#model').select_option(value)
            for i in range(page.locator('#region option').count()):
                page.locator('#region').select_option(str(i));assert 'Native location' in page.locator('#location').inner_text()
            page.locator('#region').select_option('0');page.locator('#model').select_option(str(page.evaluate('DATA.primary')))
            # Raw panel is unchanged when every overlay changes, and toggles affect
            # the comparison panel. This catches overlays accidentally drawn on raw.
            raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()');marked=page.locator('#overlay').evaluate('(c)=>c.toDataURL()')
            page.locator('#rawonly').click();assert page.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw
            assert page.locator('#overlay').evaluate('(c)=>c.toDataURL()')!=marked
            assert page.locator('#overlay').evaluate('(c)=>c.toDataURL()')==raw
            page.locator('#restore').click();page.locator('#neighbor').check();page.locator('#separators').check();page.locator('#uncertain').check();page.locator('#width').fill('140');page.locator('#width').dispatch_event('input');page.locator('#errors').click(position={'x':400,'y':100})
            page.locator('#region').select_option('0');page.screenshot(path=str(BASE/'results/browser-desktop.png'),full_page=True)
            links=page.locator('a').evaluate_all('(a)=>a.map(x=>x.href)')
            for link in links:assert page.request.get(link).ok,link
            page.set_viewport_size({'width':520,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'),full_page=True)
            page.goto((ROOT/'photo2/review/r298/index.html').as_uri());page.wait_for_function('document.querySelector("#status").textContent.startsWith("Ready")');assert page.locator('#model option').count()==4
            browser.close()
    finally:
        proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(errors=errors,links=len(links),candidate_families=4,regions=51,raw_panel_toggle_invariant=True,raw_only_canvas_equality=True,desktop=True,narrow=True,offline=True,actual_shell_launcher_http=True,launcher_from_other_directory=True,windows_opener_mocked=True,actual_windows_gui_opened=False))
    print('R298 graphical review and launcher checks passed')
if __name__=='__main__':main()
