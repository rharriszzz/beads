"""Print RESEARCH_ADVICE.md as two pages for one duplex US Letter sheet.

PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright \
  .venv/bin/python photo2/retrospective/build_advice_pdf.py
Requires markdown-it-py, Playwright/Chromium and Poppler's PDF utilities.
"""
from pathlib import Path
from urllib.parse import urlparse
import importlib.metadata
import json
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
from build_pdf import compact, sha

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'photo2/RESEARCH_ADVICE.md'
PDF = SOURCE.with_suffix('.pdf')
BACKGROUND_COMMIT = '886dd63a9f96679e3346874963778ec3b8ca8e8f'
CSS = """
@page {size:Letter;margin:15mm 17mm}
* {box-sizing:border-box}
body {margin:0;font:11pt/1.32 'DejaVu Sans',sans-serif;color:#202b35}
.sheet {height:calc(11in - 30mm);break-after:page}
.sheet:last-child {break-after:auto}
h1 {font-size:21pt;line-height:1.12;color:#173a52;margin:0 0 3mm}
h2 {font-size:14pt;line-height:1.2;color:#173a52;margin:5mm 0 3mm}
.sheet:nth-child(2) h2:first-child {margin-top:0}
h3 {font-size:11.4pt;line-height:1.25;color:#173a52;margin:3.8mm 0 1.3mm}
p {margin:0 0 2.3mm;orphans:2;widows:2}
a {color:#145975;text-decoration:none}
ul {padding-left:5mm;margin:2.5mm 0}
li {margin:0 0 2.1mm}
li p {margin:0}
table {width:100%;border-collapse:collapse;table-layout:fixed;font-size:9.1pt;line-height:1.27;margin:3mm 0}
td,th {padding:1.2mm;vertical-align:top;border:.2mm solid #c6d0d8}
th {text-align:left;background:#e9eff3;color:#173a52}
td:first-child {width:34%}
.sheet:nth-child(2)>p:last-child {font-size:8.1pt;line-height:1.3;color:#53626f;margin-top:3mm}
"""


def main():
    before = sha(SOURCE)
    sections = SOURCE.read_text().split('<!-- pagebreak -->')
    assert len(sections) == 2
    parser = MarkdownIt('commonmark').enable('table')
    rendered = []
    for section in sections:
        tokens = parser.parse(section)
        for token in tokens:
            for child in token.children or []:
                if child.type == 'link_open':
                    href = child.attrGet('href')
                    url = urlparse(href)
                    if not url.scheme and url.path:
                        path = (SOURCE.parent/url.path).resolve()
                        assert path.is_file()
                        child.attrSet('href', f'https://github.com/rharriszzz/beads/blob/{BACKGROUND_COMMIT}/'+
                                      path.relative_to(ROOT).as_posix()+('#'+url.fragment if url.fragment else ''))
        rendered.append('<article class="sheet">'+parser.renderer.render(tokens, parser.options, {})+'</article>')
    html = '<!doctype html><html lang="en"><meta charset="utf-8"><title>Conducting computational investigations</title><style>'+CSS+'</style>'+''.join(rendered)+'</html>'
    with tempfile.TemporaryDirectory(prefix='research-advice-pdf-') as temp:
        path = Path(temp)/'advice.html'
        path.write_text(html)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            version = browser.version
            page = browser.new_page(viewport={'width': 688, 'height': 1000})
            page.goto(path.as_uri())
            page.evaluate('document.fonts.ready')
            page.emulate_media(media='print')
            sizes = page.locator('.sheet').evaluate_all('(xs)=>xs.map(x=>({height:x.clientHeight,content:x.scrollHeight,width:x.clientWidth,contentWidth:x.scrollWidth}))')
            assert all(s['content'] <= s['height']+1 and s['contentWidth'] <= s['width']+1 for s in sizes), sizes
            blocks = page.locator('h1,h2,h3,p,li,td,th').all_inner_texts()
            page.pdf(path=str(PDF), prefer_css_page_size=True, print_background=True,
                     display_header_footer=True, header_template='<span></span>',
                     footer_template='<div style="font:8px DejaVu Sans;color:#687782;text-align:right;width:100%;margin:0 17mm">Conducting computational investigations · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                     tagged=True, outline=True)
            browser.close()
    info = subprocess.check_output(['pdfinfo', str(PDF)], text=True)
    assert re.search(r'^Pages:\s+2$', info, re.M), info
    text = subprocess.check_output(['pdftotext', '-raw', str(PDF), '-'], text=True)
    assert all(compact(b) in compact(text) for b in blocks), 'Missing source text'
    bbox = ET.fromstring(subprocess.check_output(['pdftotext', '-bbox', str(PDF), '-']))
    ns = {'x':'http://www.w3.org/1999/xhtml'}
    for pdf_page in bbox.findall('.//x:page', ns):
        for word in pdf_page.findall('.//x:word', ns):
            assert 0 <= float(word.attrib['xMin']) <= float(word.attrib['xMax']) <= float(pdf_page.attrib['width'])
            assert 0 <= float(word.attrib['yMin']) <= float(word.attrib['yMax']) <= float(pdf_page.attrib['height'])
    assert before == sha(SOURCE)
    receipt = dict(source=str(SOURCE.relative_to(ROOT)), source_sha256=before,
                   pdf=str(PDF.relative_to(ROOT)), pdf_sha256=sha(PDF), pages=2,
                   paper='US Letter; print two-sided and flip on the long edge',
                   body_font_pt=11, table_font_pt=9.1, source_text_blocks_verified=len(blocks),
                   all_words_within_page=True, sheet_dimensions=sizes,
                   background_commit=BACKGROUND_COMMIT, chromium=version,
                   markdown_it_py=importlib.metadata.version('markdown-it-py'))
    Path(__file__).with_name('advice-pdf.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
