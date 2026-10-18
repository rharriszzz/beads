import json
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT=Path(__file__).parent/'results'
def main():
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':900});page.goto((OUT/'shared-shape-review.html').resolve().as_uri());assert page.locator('svg image').count()==6;assert page.locator('table tr').count()>2
        page.screenshot(path=str(OUT/'shared-shape-desktop.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.context.set_offline(True);page.reload();assert page.locator('svg image').count()==6;b.close()
    (OUT/'shared-shape-browser.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True),indent=2)+'\n');print('PASS shared-shape review')
if __name__=='__main__':main()
