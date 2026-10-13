"""Local Chromium R266 comparison/alternatives/native replay checks."""
import json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from .server import make_server
from .experiment_r266 import ROOT,WORK,OUT,save


def main():
    server=make_server(ROOT/'photo2/output/r265-first-dark/joint',port=0)
    threading.Thread(target=server.serve_forever,daemon=True).start();checks=[]
    def check(ok,message):
        assert ok,message
        checks.append(message);print('PASS',message,flush=True)
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport=dict(width=1500,height=1000));errors=[];page.on('pageerror',lambda e:errors.append(str(e)));url=f'http://127.0.0.1:{server.server_port}'
            for run in ('straight-0-selected12','annular-0-selected12','straight-0-selected6','annular-0-selected6'):
                page.goto(url+'/?run='+run+'&id=P128275');page.wait_for_function('regionTest?.state.ready&&regionTest.state.replay!==null',timeout=60000)
                data=json.loads((WORK/run/'regions.json').read_text())
                check(page.evaluate('regionTest.data.generation_id')==data['generation_id'],run+' correct generation')
                page.wait_for_function('(run)=>document.getElementById("methodRun").value===run',arg=run);check(page.locator('#methodRun').input_value()==run,run+' comparison selected')
                check('rise 0 DN' in page.inner_text('#status'),run+' strict setting explained')
                for button,index in [('largest',0),('median',len(data['regions'])//2),('smallest',-1)]:
                    ordered=sorted(data['regions'],key=lambda r:(-r['pixel_count'],r['id']));page.click('#'+button);page.wait_for_function('regionTest.state.replay!==null');check(page.evaluate('regionTest.state.selected')==ordered[index]['id'],run+' '+button)
                page.evaluate("regionTest.select('P128275')");page.wait_for_function('regionTest.state.replay!==null');page.click('#step');trace=page.evaluate('regionTest.state.replay');check(trace['accepted'][0][3]>0,run+' exact native replay')
                if run.startswith('annular'):
                    check('Annular layer' in page.inner_text('#pixelInfo'),'Annular layer and running minimum shown')
                    check(all(a[3]<=trace['accepted'][a[2]][3] for a in trace['accepted'][1:]),'Strict annular parent descent in browser trace')
                check(len(data['suppressed'])>0,run+' suppression inventory nonempty')
                r=data['suppressed'][0];page.locator('#maximaMode').select_option('alternatives');page.fill('#jump',r['id']);page.locator('#jump').press('Enter');page.wait_for_function('regionTest.state.replay!==null');check('suppressed' in page.inner_text('#details') and r['suppressed_by'] in page.inner_text('#details'),run+' suppressed maximum and winner explained')
                check(page.locator('#details button').count()>0,run+' related maxima navigable')
                page.locator('#details button').first.click();page.wait_for_function('regionTest.state.replay!==null');check(page.evaluate('regionTest.state.selected')!=r['id'],run+' related maximum selection')
                deferred=data['deferred'][0];page.evaluate('(id)=>regionTest.select(id)',deferred['id']);page.wait_for_function('regionTest.state.replay!==null');check('deferred' in page.inner_text('#details'),run+' deferral inspectable')
                page.click('#stopNext');check(page.evaluate('regionTest.state.stop')==0,run+' stopped native sample inspectable')
                page.screenshot(path=str(OUT/(run+'-viewer.png')))
            page.evaluate("regionTest.select('P128275')");before=page.evaluate('regionTest.state.view');page.locator('#methodRun').select_option('straight-0-selected12');page.wait_for_function('regionTest?.state.ready&&regionTest.state.replay!==null');after=page.evaluate('regionTest.state.view');check(before==after,'Method switch preserves native viewport and selected ID')
            check(page.request.get(url+'/r266-data/../../REQUEST_LOG.md').status==404,'Comparison endpoint prevents traversal')
            check(not errors,'No JavaScript errors');browser.close()
    finally:server.shutdown();server.server_close()
    save(OUT/'browser-r266-checks.json',dict(count=len(checks),checks=checks))
if __name__=='__main__':main()
