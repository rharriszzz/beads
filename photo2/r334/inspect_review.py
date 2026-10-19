"""Inspect exact historical R333 panels and their expandable stable-ID keys."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path('/home/rharris/git/beads')
def main():
    out=ROOT/'photo2/r334/development';errors=[];records=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1600,'height':1100});page.on('pageerror',lambda e:errors.append(str(e)));page.goto((ROOT/'photo2/r333/review/index.html').as_uri());page.wait_for_function('window.R333_STATE&&R333_STATE.frames>2');page.locator('#case-05').scroll_into_view_if_needed()
        for figure_id,nums in [('MAT25-K-2237-2196',[25]),('K-1904-2820',[36,7,33])]:
            figures=page.locator('#case-05 .pair').last.locator('figure');found=[]
            for j in range(figures.count()):
                fig=figures.nth(j)
                if figure_id in fig.inner_text():
                    fig.locator('details').evaluate('(el)=>el.open=true');key=fig.locator('details').inner_text();fig.screenshot(path=str(out/(figure_id+'-actual-panel.png')));found.append(dict(case='case-05',figure=figure_id,local_numbers=nums,key_text=key,images=fig.locator('img').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("src"))')))
            assert len(found)==1,figure_id;records+=found
        for name in ['case-02','case-03','case-04','case-05']:
            page.locator('#'+name).locator('details').first.evaluate('(el)=>el.open=true');assert 'Every numbered ID' in page.locator('#'+name).inner_text()
        assert not errors;browser.close()
    (out/'R333-dom-inspection.json').write_text(json.dumps(dict(passed=True,records=records,errors=errors),indent=2)+'\n');print('PASS exact R333 panels and expanded keys')
if __name__=='__main__':main()
