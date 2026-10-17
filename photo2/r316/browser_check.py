from playwright.sync_api import sync_playwright
from photo2.r297.common import ROOT,save,utc
OUT=ROOT/'photo2/r316/results'
def main():
    errors=[]
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1450,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((OUT/'index.html').as_uri());page.wait_for_load_state('load');assert page.locator('h1').inner_text().startswith('R316');assert page.locator('table tr').count()==37;assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');page.screenshot(path=str(OUT/'review/browser-desktop.png'));page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1');page.screenshot(path=str(OUT/'review/browser-narrow.png'));page.context.set_offline(True);page.reload();page.wait_for_load_state('load');assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)');b.close()
    assert not errors;save(OUT/'browser-check.json',dict(passed=True,utc=utc(),checks=['36 photographic ledger rows','desktop','narrow no horizontal overflow','offline images'],errors=errors))
if __name__=='__main__':main()
