from playwright.sync_api import sync_playwright
from .common import OUT,REVIEW,read,save

def main():
    errors=[];checks=[]
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True);page=b.new_page(viewport={'width':1400,'height':1100})
        page.on('pageerror',lambda e:errors.append(str(e)));page.goto((REVIEW/'index.html').as_uri())
        for im in page.locator('section img').all():
            im.scroll_into_view_if_needed();im.evaluate('(x)=>x.loading="eager"')
            page.wait_for_function('(src)=>{let x=[...document.images].find(i=>i.getAttribute("src")==src);return x.complete&&x.naturalWidth>0}',arg=im.get_attribute('src'))
            checks.append(im.get_attribute('src'))
        selfcontained=read(REVIEW/'panels.json');assert len(checks)==len(selfcontained)
        assert all(len(r['caption'])>100 for r in selfcontained)
        page.locator('section').first.scroll_into_view_if_needed();page.screenshot(path=str(OUT/'browser-review.png'));b.close()
    assert not errors;save(OUT/'browser-check.json',dict(panels=checks,errors=errors,bottom_captions=True));print(len(checks),'browser panels pass')

if __name__=='__main__':main()
