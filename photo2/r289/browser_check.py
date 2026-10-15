"""Existing persistent Chromium launcher; review only, no deployment."""
from playwright.sync_api import sync_playwright
from .common import *

def main():
    errors=[];images=[];links=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1360,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((REVIEW/'index.html').as_uri());page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
        for im in page.locator('img').all():
            im.scroll_into_view_if_needed();page.wait_for_function('(src)=>{const x=[...document.images].find(i=>i.getAttribute("src")==src);return x.complete&&x.naturalWidth>0}',arg=im.get_attribute('src'));images.append(im.get_attribute('src'))
        for a in page.locator('a[href]').all():
            href=a.get_attribute('href')
            if href.startswith('http'):continue
            if href.startswith('#'):assert page.locator(href).count()==1,href
            else:assert (REVIEW/href).resolve().exists(),href
            links.append(href)
        for name in ('red-multiple','yellow-worst','P2','Q14'):
            page.locator('#'+name).evaluate('(x)=>x.scrollIntoView({block:"start"})');page.screenshot(path=str(OUT/('browser-'+name+'.png')))
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=false)');page.evaluate('scrollTo(0,0)');page.screenshot(path=str(OUT/'browser-desktop.png'))
        page.set_viewport_size({'width':560,'height':900});page.screenshot(path=str(OUT/'browser-narrow.png'));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'horizontal overflow'
        tables=page.locator('table').count();details=page.locator('details').count();assert len(images)>=24 and tables>=6
        browser.close()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(images=len(images),tables=tables,details=details,local_links=len(links),errors=errors,narrow_width=560,desktop_width=1360))
    print(len(images),'images',tables,'tables',details,'expandable comparisons;',len(links),'local links pass')
if __name__=='__main__':main()
