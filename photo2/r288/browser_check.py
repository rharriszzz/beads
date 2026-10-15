"""Local rendered review through the project's persistent Chromium launcher."""
from playwright.sync_api import sync_playwright
from .common import *

def main():
    errors=[];images=[];links=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1500,'height':1050})
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((REVIEW/'index.html').as_uri())
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
        for img in page.locator('img').all():
            img.scroll_into_view_if_needed()
            page.wait_for_function('(src)=>{const x=[...document.images].find(i=>i.getAttribute("src")==src);return x.complete&&x.naturalWidth>0}',arg=img.get_attribute('src'))
            images.append(img.get_attribute('src'))
        for a in page.locator('a[href]').all():
            href=a.get_attribute('href');assert (REVIEW/href).resolve().exists(),href;links.append(href)
        sections=page.locator('section').count();tables=page.locator('table').count()
        assert sections==27 and tables==25,(sections,tables)
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=false)')
        for name in ('N07','N11','Q06','Q14','Q01-weak'):
            page.locator('#'+name).evaluate('(x)=>x.scrollIntoView({block:"start"})')
            page.screenshot(path=str(OUT/('browser-'+name+'.png')))
        page.set_viewport_size({'width':600,'height':900})
        page.locator('#N07').evaluate('(x)=>x.scrollIntoView({block:"start"})')
        page.screenshot(path=str(OUT/'browser-narrow.png'))
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'), 'narrow layout overflow'
        browser.close()
    assert not errors,errors
    save(OUT/'browser-check.json',dict(images=len(images),tables=tables,sections=sections,links=len(links),errors=errors,narrow_viewport=600))
    print(len(images),'images',tables,'tables',sections,'sections; desktop/narrow/local links pass')

if __name__=='__main__':main()
