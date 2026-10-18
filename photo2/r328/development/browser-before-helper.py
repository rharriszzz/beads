import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='photo2/r328/results');args=ap.parse_args();out=Path(args.output).resolve()
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':900});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((out/'index.html').as_uri());assert page.locator('svg image').count()==13
        page.locator('#step').fill('-1');page.locator('#step').dispatch_event('input');assert 'one component' in page.locator('#status').inner_text();page.screenshot(path=str(out/'growth-start.png'))
        page.locator('#step').fill('187');page.locator('#step').dispatch_event('input');assert 'return checked' in page.locator('#status').inner_text();page.screenshot(path=str(out/'browser-desktop.png'),full_page=True)
        for i,name in enumerate(['upper','inward','lower','black']):page.locator('.panels').nth(i).screenshot(path=str(out/f'{name}-comparison.png'))
        page.locator('#raw').click();assert page.locator('svg line').first.evaluate("e=>e.style.visibility==='hidden'");page.locator('#raw').click()
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');page.context.set_offline(True);page.reload();assert page.locator('svg image').count()==13;assert not errors;b.close()
    (out/'browser-verification.json').write_text(json.dumps(dict(passed=True,desktop=True,narrow=True,offline=True,slider=True,overlay_toggle=True,errors=errors),indent=2)+'\n');print('PASS browser growth controls/native crops/desktop/narrow/offline')
if __name__=='__main__':main()
