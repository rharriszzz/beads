"""Offline reading-size preview of this Markdown page, not a GitHub service test.
Uses a small adapter for the Markdown constructs used in this page. Outputs the
preview and screenshots to /tmp; the scientific and historical HTML are untouched.
Run with PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright.
"""
import html, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent
TMP=Path('/tmp/r329-guide-preview');TMP.mkdir(exist_ok=True)
def inline(s):
    s=html.escape(s)
    s=re.sub(r'!\[([^]]*)\]\(([^)]+)\)',r'<a href="\2"><img alt="\1" src="\2"></a>',s)
    s=re.sub(r'(?<!!)\[([^]]*)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
    return re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
def slug(s):return re.sub(r'[^\w\- ]','',s.lower()).replace(' ','-')
def preview():
    blocks=[];code=False;table=False;listing=False
    for line in (HERE/'READING_THE_PHOTOGRAPH.md').read_text().splitlines():
        if line.startswith('```'):
            blocks.append('</code></pre>' if code else '<pre><code>');code=not code;continue
        if code:blocks.append(html.escape(line)+'\n');continue
        if listing and not line.startswith('- '):blocks.append('</ul>');listing=False
        if table and not line.startswith('|'):blocks.append('</tbody></table>');table=False
        if not line:continue
        if line.startswith('#'):
            h,s=line.split(' ',1);blocks.append(f'<h{len(h)} id="{slug(s)}">{inline(s)}</h{len(h)}>')
        elif line.startswith('- '):
            if not listing:blocks.append('<ul>');listing=True
            blocks.append('<li>'+inline(line[2:])+'</li>')
        elif line.startswith('|'):
            if re.match(r'^\|[\s|:-]+$',line):continue
            if not table:blocks.append('<table><tbody>');table=True
            blocks.append('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in line.strip('|').split('|'))+'</tr>')
        else:blocks.append('<p>'+inline(line)+'</p>')
    page='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>R329 Markdown reading preview</title>'
    page+=f'<base href="{HERE.as_uri()}/"><style>body{{color:#1f2328;font:16px/1.6 system-ui,sans-serif;margin:0 auto;padding:32px;max-width:880px}}img{{display:block;width:100%;height:auto}}h1,h2{{border-bottom:1px solid #d1d9e0;padding-bottom:.3em}}h2{{margin-top:48px}}a{{color:#0969da}}code,pre{{background:#f4f6f8}}pre{{overflow:auto;padding:16px}}table{{display:block;max-width:100%;overflow:auto;border-collapse:collapse}}td{{border:1px solid #d1d9e0;padding:8px}}@media(max-width:600px){{body{{padding:16px}}}}</style>'
    page+='\n'.join(blocks);(TMP/'index.html').write_text(page)
def main():
    preview()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1100,'height':900});errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((TMP/'index.html').as_uri());page.wait_for_load_state('load')
        assert page.locator('img').count()==12
        assert page.locator('img').evaluate_all('(ii)=>ii.every(i=>i.complete&&i.naturalWidth>0)')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for name in ['c-both-primitives','e-disputed-pair','f-model-ownership','g-early-working','g-early-alternative','h-lower-working','h-lower-alternative']:
            page.locator(f'img[src="images/{name}.png"]').screenshot(path=str(TMP/(name+'.png')))
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(TMP/'narrow.png'));page.context.set_offline(True);page.reload()
        assert page.locator('img').evaluate_all('(ii)=>ii.every(i=>i.complete&&i.naturalWidth>0)')
        assert not errors;browser.close()
    receipt={'passed':True,'preview_scope':'Offline HTML adapter for the Markdown used on this page; not a test of the live GitHub renderer.','embedded_images_loaded':12,'desktop_width':1100,'content_width':880,'narrow_width':390,'horizontal_overflow':False,'offline':True,'image_full_resolution_links':True,'screenshots_directory':str(TMP),'page_errors':errors}
    (HERE/'browser-verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
