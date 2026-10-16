"""Smoke-test reused debugger, raw-pixel invariance and actual launcher."""
import subprocess
from unittest.mock import patch
from playwright.sync_api import sync_playwright
from .core import ROOT,BASE,save
from .serve import open_browser

def main():
    review=ROOT/'photo2/review/r302'
    proc=subprocess.Popen([str(review/'launch.sh'),'--port','0','--no-browser'],cwd='/tmp',stdout=subprocess.PIPE,text=True)
    line=proc.stdout.readline().strip();assert line.startswith('R302 review: ');url=line.split('review: ')[1];errors=[];checked=[]
    try:
        with patch('photo2.r299.serve.shutil.which',side_effect=lambda k:'powershell.exe' if k=='powershell.exe' else None),patch('photo2.r299.serve.subprocess.Popen') as spawn:
            open_browser(url);assert url in spawn.call_args.args[0][-1]
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1450,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto(url);page.locator('#status').filter(has_text='Ready').wait_for()
            for name in page.locator('#model option').evaluate_all('(x)=>x.map(o=>o.value)'):
                page.locator('#model').select_option(name);assert 'Ready' in page.locator('#status').inner_text()
                raw=page.locator('#raw').evaluate('(c)=>c.toDataURL()')
                page.locator('#alternatives').check();page.locator('#centers').check();page.locator('#surfaces').uncheck();page.locator('#next').click()
                assert page.locator('#raw').evaluate('(c)=>c.toDataURL()')==raw
                assert 'alternatives' in page.locator('#details').inner_text();checked.append(name)
            page.locator('#model').select_option(index=0);page.locator('#surfaces').check();page.screenshot(path=str(BASE/'results/browser-desktop.png'))
            for a in page.locator('a').evaluate_all('(x)=>x.map(a=>a.href)'):assert page.request.get(a).ok,a
            page.set_viewport_size({'width':520,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(BASE/'results/browser-narrow.png'))
            page.goto((review/'index.html').as_uri());page.locator('#status').filter(has_text='Ready').wait_for();browser.close()
    finally:proc.terminate();proc.wait(timeout=10)
    assert not errors,errors
    save(BASE/'results/browser-check.json',dict(models=checked,errors=errors,raw_invariant=True,desktop=True,narrow=True,offline=True,actual_launcher=True,windows_dispatch_mocked=True,windows_browser_actually_opened=False))
    print('R302 reused debugger checks passed:',len(checked),'models')

if __name__=='__main__':main()
