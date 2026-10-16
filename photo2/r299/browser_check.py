"""Actual launch script, preserved geometry tab, full ledgers and raw invariance."""
import subprocess
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from .common import *
from .serve import open_browser

def main():
    proc=subprocess.Popen([str(REVIEW/'launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);first=proc.stdout.readline().strip();assert first.startswith('R299 review: '),first;url=first.split('review: ',1)[1];errors=[]
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            b=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1450,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url);page.wait_for_function('document.querySelector("#status").textContent.startsWith("Ready")')
            count=page.locator('#model option').count();observations=page.locator('#observation option').count();assert observations==52
            for name in page.locator('#model option').evaluate_all('(a)=>a.map(x=>x.value)'):
                page.locator('#model').select_option(name);assert page.locator('#ledger tbody tr').count()==52
            page.locator('#model').select_option(page.evaluate('DATA.default'))
            for i in range(observations):page.locator('#observation').select_option(str(i));assert 'Native location' in page.locator('#location').inner_text()
            page.locator('#observation').select_option('0');raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()');overlay=page.locator('#overlay').evaluate('(c)=>c.toDataURL()');page.locator('#rawonly').click();assert page.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw;assert page.locator('#overlay').evaluate('(c)=>c.toDataURL()')==raw;assert overlay!=raw
            page.locator('#restore').click();page.locator('#competitors').check();page.locator('#reference').check();page.locator('#kind').select_option('centroid');assert page.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw
            page.locator('#stationplot').click(position={'x':250,'y':100});page.locator('#angleplot').click(position={'x':220,'y':100});page.locator('#observation').select_option('0');page.screenshot(path=str(BASE/'results/browser-desktop.png'),full_page=True)
            links=page.locator('a').evaluate_all('(a)=>a.map(x=>x.href)')
            for link in links:assert page.request.get(link).ok,link
            page.locator('#geometrytab').click();frame=page.frame_locator('#geometryframe');frame.locator('#status').filter(has_text='Ready').wait_for();assert frame.locator('#model option').count()==4
            page.locator('#reflectiontab').click();page.set_viewport_size({'width':520,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'),full_page=True)
            page.goto((REVIEW/'index.html').as_uri());page.wait_for_function('document.querySelector("#status").textContent.startsWith("Ready")');assert page.locator('#model option').count()==count;page.locator('#geometrytab').click();page.frame_locator('#geometryframe').locator('#status').filter(has_text='Ready').wait_for();b.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(errors=errors,models=count,observations=observations,links=len(links),desktop=True,narrow=True,offline=True,raw_invariant=True,raw_only_equal=True,preserved_R298_tab=True,actual_shell_launcher=True,launcher_other_directory=True,windows_dispatch_mocked=True,windows_browser_actually_opened=False));print('R299 Chromium checks passed')
if __name__=='__main__':main()
