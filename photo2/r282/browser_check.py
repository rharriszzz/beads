"""Rendered phase/example navigation with complete static images."""
from playwright.sync_api import sync_playwright
from .common import ROOT,OUT,save


def main():
    errors=[];checks=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1400,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((ROOT/'photo2/review/r282/index.html').as_uri())
        for phase in ('Phase 1','Phase 2','Phase 3'):
            page.select_option('#phase',phase)
            values=page.locator('#example option').evaluate_all('(xs)=>xs.map(x=>x.value)')
            for value in values:
                page.select_option('#example',value)
                page.wait_for_function("document.querySelector('#picture').complete && document.querySelector('#picture').naturalWidth>0")
                assert page.locator('#note').inner_text();assert page.locator('#full').get_attribute('href')==page.locator('#picture').get_attribute('src')
                checks.append(dict(phase=phase,file=page.locator('#picture').get_attribute('src')))
        page.select_option('#phase','Phase 1');page.select_option('#example','2');page.wait_for_timeout(100)
        page.screenshot(path=str(OUT/'browser-review.png'));browser.close()
    assert not errors;save(OUT/'browser-check.json',dict(cases=checks,errors=errors));print(len(checks),'browser cases passed')


if __name__=='__main__':main()
