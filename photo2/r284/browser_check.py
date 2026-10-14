"""Read-only Chromium inspection of local review artifacts; writes screenshots/audit."""
from playwright.sync_api import sync_playwright
from photo2.r282.common import read,save
from .run import OUT
from .review import REVIEW


def main():
    errors=[];images=[];links=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True);page=browser.new_page(viewport={'width':1600,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)));page.goto((REVIEW/'index.html').as_uri())
        page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
        for img in page.locator('img').all():
            img.scroll_into_view_if_needed();page.wait_for_function('(src)=>{let x=[...document.images].find(i=>i.getAttribute("src")==src);return x.complete&&x.naturalWidth>0}',arg=img.get_attribute('src'))
            images.append(img.get_attribute('src'))
        for a in page.locator('a[href]').all():
            href=a.get_attribute('href')
            if not href.startswith('#'):assert (REVIEW/href).resolve().exists(),href;links.append(href)
        for name in ('two-sided','duplicate','abstention'):
            page.locator('#'+name+' > a').first.evaluate('(x)=>x.scrollIntoView({block:"start"})');page.screenshot(path=str(OUT/('browser-'+name+'.png')))
        assert page.locator('section').count()==8
        assert len(images)==27 # eight full + eight raw + three focus + eight reflection/body
        assert page.locator('table').count()==25
        page.set_viewport_size({'width':600,'height':900});page.locator('#two-sided > a').first.evaluate('(x)=>x.scrollIntoView({block:"start"})');page.screenshot(path=str(OUT/'browser-narrow.png'))
        browser.close()
    assert not errors
    save(OUT/'browser-check.json',dict(images=images,links=len(links),errors=errors,cases=8,panels=19,tables=25,native_images=8))
    print('27 images / 19 comparison-evidence panels / 25 tables / links pass')

if __name__=='__main__':main()
