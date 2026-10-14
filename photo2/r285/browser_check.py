"""Rendered local review; no external application, network or inference writes."""
from playwright.sync_api import sync_playwright
from photo2.r282.common import save
from .select import OUT
from .review import REVIEW

def main():
    errors=[];images=[];links=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1500,'height':1050});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((REVIEW/'index.html').as_uri());page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
        for img in page.locator('img').all():
            img.scroll_into_view_if_needed();page.wait_for_function('(src)=>{const x=[...document.images].find(i=>i.getAttribute("src")==src);return x.complete&&x.naturalWidth>0}',arg=img.get_attribute('src'));images.append(img.get_attribute('src'))
        for a in page.locator('a[href]').all():
            href=a.get_attribute('href');assert (REVIEW/href).resolve().exists(),href;links.append(href)
        assert page.locator('section').count()==30;assert page.locator('table').count()==25
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=false)')
        for name in ('e01','e02','e04','v04','upper-good-black'):
            page.locator('#'+name).evaluate('(x)=>x.scrollIntoView({block:"start"})');page.screenshot(path=str(OUT/('browser-'+name+'.png')))
        page.set_viewport_size({'width':600,'height':900});page.locator('#e01').evaluate('(x)=>x.scrollIntoView({block:"start"})');page.screenshot(path=str(OUT/'browser-narrow.png'));browser.close()
    assert not errors;save(OUT/'browser-check.json',dict(images=len(images),tables=25,sections=30,links=len(links),errors=errors,narrow_viewport=600));print(len(images),'images / 25 tables / 30 sections / local links and desktop+narrow render pass')
if __name__=='__main__':main()
