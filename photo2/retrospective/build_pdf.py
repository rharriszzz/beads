"""Export RETROSPECTIVE.md with tables, figures, navigation and public source links.

Requires this checkout's Playwright/Chromium and markdown-it-py. Run from the root:
PLAYWRIGHT_BROWSERS_PATH=/home/rharris/.cache/beads-playwright \
  .venv/bin/python photo2/retrospective/build_pdf.py
The HTML and page previews are temporary; only the PDF and receipt are delivered.
"""
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlparse
import hashlib
import importlib.metadata
import json
import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'photo2/RETROSPECTIVE.md'
PDF = SOURCE.with_suffix('.pdf')
RECEIPT = Path(__file__).with_name('pdf-export.json')
SOURCE_COMMIT = '988402b699be0a3a59ed90591f1188c5980f6b74'
PUBLIC = f'https://github.com/rharriszzz/beads/blob/{SOURCE_COMMIT}/'

CSS = """
@page {size:Letter; margin:19mm 17mm 19mm;}
* {box-sizing:border-box}
body {font-family:'DejaVu Sans',sans-serif; color:#202b35; font-size:10pt; line-height:1.45; margin:0;}
h1 {font-size:23pt;line-height:1.2;color:#173a52;margin:0 0 6mm}
h2 {font-size:15pt;line-height:1.2;margin:8mm 0 3mm;color:#173a52}
h3 {font-size:11.5pt;line-height:1.3;margin:5mm 0 2mm;color:#173a52}
h1,h2,h3 {break-after:avoid}
p {margin:0 0 3.1mm;orphans:3;widows:3}
a {color:#145975;text-decoration:none;overflow-wrap:anywhere}
strong {font-weight:700}
ul,ol {padding-left:6mm;margin:2mm 0 4mm}
li {margin:0 0 2mm;orphans:3;widows:3}
table {width:100%;border-collapse:collapse;table-layout:fixed;font-size:8pt;line-height:1.35;margin:4mm 0 5mm}
thead {display:table-header-group}
th {background:#e7eef3;color:#173a52;text-align:left;font-weight:700}
td,th {padding:2mm 1.7mm;vertical-align:top;border:0.25mm solid #ccd5dc;overflow-wrap:anywhere}
tr {break-inside:avoid}
tr:nth-child(even) td {background:#f7f9fa}
code {font-family:'DejaVu Sans Mono',monospace;font-size:.88em;overflow-wrap:anywhere}
pre {white-space:pre-wrap;overflow-wrap:anywhere;font-size:8pt;line-height:1.35;
     padding:3mm;border:0.25mm solid #d4dde3;background:#f4f7f9;break-inside:avoid;margin:4mm 0}
pre code {font-size:inherit}
figure {margin:5mm 0;break-inside:avoid}
figure img {display:block;width:100%;height:auto;max-height:175mm;object-fit:contain}
figcaption {font-size:8.5pt;line-height:1.4;color:#53626f;margin-top:2mm}
.cover {break-after:page;padding-top:13mm}
.eyebrow {text-transform:uppercase;letter-spacing:.13em;font-size:9pt;color:#607889;margin-bottom:7mm}
.subtitle {font-size:13pt;line-height:1.5;margin:7mm 0}
.provenance {font-size:8.5pt;color:#53626f;margin:8mm 0}
nav {margin-top:12mm;border-top:1px solid #ccd5dc;padding-top:5mm}
nav a {display:block;margin:0 0 3mm;font-size:11pt}
"""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', text))


def main():
    original_hash = sha(SOURCE)
    committed = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:photo2/RETROSPECTIVE.md'], cwd=ROOT)
    assert hashlib.sha256(committed).hexdigest() == original_hash, 'Review source commit before exporting a changed report'
    markdown = MarkdownIt('commonmark').enable('table')
    tokens = markdown.parse(SOURCE.read_text())
    headings = []
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            name = tokens[i+1].content
            anchor = 'section-' + str(len(headings)+1)
            token.attrSet('id', anchor)
            headings.append(dict(level=token.tag, text=name, anchor=anchor))
        if token.type == 'inline':
            for child in token.children or []:
                if child.type == 'link_open':
                    href = child.attrGet('href')
                    url = urlparse(href)
                    if not url.scheme and url.path:
                        target = (SOURCE.parent/unquote(url.path)).resolve()
                        assert target.exists(), target
                        child.attrSet('href', PUBLIC+target.relative_to(ROOT).as_posix()+
                                      ('#'+url.fragment if url.fragment else ''))
                if child.type == 'image':
                    child.attrSet('src', (SOURCE.parent/child.attrGet('src')).resolve().as_uri())
    content = markdown.renderer.render(tokens, markdown.options, {})
    toc = ''.join(f'<a href="#{h["anchor"]}">{escape(h["text"])}</a>' for h in headings if h['level']=='h2')
    html = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<title>Reverse engineering beads photo 2 — Retrospective</title><style>{CSS}</style>
<section class="cover"><p class="eyebrow">Historical and technical retrospective</p>
<h1>Reverse engineering<br>beads photo 2</h1>
<p class="subtitle">The development process, final evidence and lessons for future projects</p>
<p>Through R347 and its maker answers, with the R348 analysis.</p>
<p class="provenance">Faithful PDF export of photo2/RETROSPECTIVE.md<br>
Source revision: <a href="{PUBLIC}photo2/RETROSPECTIVE.md">{SOURCE_COMMIT[:8]}</a><br>
Figures are embedded; evidence links open immutable GitHub sources.</p>
<nav aria-label="Contents">{toc}</nav></section><main>{content}</main></html>'''
    failed = []
    with tempfile.TemporaryDirectory(prefix='beads-retrospective-pdf-') as temp:
        html_path = Path(temp)/'retrospective.html'
        html_path.write_text(html)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            version = browser.version
            page = browser.new_page(viewport={'width': 665, 'height': 1000})
            page.on('requestfailed', lambda request: failed.append(request.url))
            page.goto(html_path.as_uri())
            page.evaluate('document.fonts.ready')
            assert page.locator('img').count() == 3
            assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
            # Keep each figure with its original caption, without altering text.
            page.evaluate('''() => {for (const p of document.querySelectorAll('main p')) {
              if (p.children.length===1 && p.firstElementChild.tagName==='IMG') {
                const figure=document.createElement('figure'); p.replaceWith(figure);
                figure.append(p.firstElementChild);
                const caption=figure.nextElementSibling;
                if(caption?.tagName==='P' && caption.firstElementChild?.tagName==='EM') {
                  const f=document.createElement('figcaption');f.innerHTML=caption.innerHTML;
                  figure.append(f);caption.remove();
                }
              }
            }}''')
            blocks = page.locator('main h1, main h2, main h3, main p, main li, main td, main th, main pre, main figcaption').all_inner_texts()
            figures = page.locator('img').evaluate_all('(xs)=>xs.map(x=>({src:x.src,width:x.naturalWidth,height:x.naturalHeight}))')
            assert not failed, failed
            assert page.locator('a[href^="file:"]').count() == 0
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), 'Horizontal clipping'
            page.pdf(path=str(PDF), print_background=True, prefer_css_page_size=True,
                     display_header_footer=True,
                     header_template='<div style="font:8px DejaVu Sans;color:#687782;margin:0 17mm;width:100%">Beads photo 2 · Retrospective</div>',
                     footer_template='<div style="font:8px DejaVu Sans;color:#687782;margin:0 17mm;width:100%;text-align:right">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
                     outline=True, tagged=True)
            browser.close()
    extracted = subprocess.check_output(['pdftotext', '-raw', str(PDF), '-'], text=True)
    cleaned = re.sub(r'Page \d+ of \d+', '', extracted.replace('Beads photo 2 · Retrospective', ''))
    missing = [text for text in blocks if compact(text) not in compact(cleaned)]
    assert not missing, 'PDF text missing or interleaved: '+repr(missing[:3])
    info = subprocess.check_output(['pdfinfo', str(PDF)], text=True)
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    bbox = ET.fromstring(subprocess.check_output(['pdftotext', '-bbox', str(PDF), '-']))
    ns = {'x': 'http://www.w3.org/1999/xhtml'}
    words_checked = 0
    for pdf_page in bbox.findall('.//x:page', ns):
        for word in pdf_page.findall('.//x:word', ns):
            box = word.attrib
            assert 0 <= float(box['xMin']) <= float(box['xMax']) <= float(pdf_page.attrib['width'])
            assert 0 <= float(box['yMin']) <= float(box['yMax']) <= float(pdf_page.attrib['height'])
            words_checked += 1
    destinations = subprocess.check_output(['pdfinfo', '-dests', str(PDF)], text=True)
    linked_sections = len(re.findall(r'^\s+\d+\s+\[', destinations, re.M))
    assert linked_sections == sum(h['level'] == 'h2' for h in headings)
    urls = subprocess.check_output(['pdfinfo', '-url', str(PDF)], text=True)
    assert 'file:' not in urls
    assert sha(SOURCE) == original_hash
    result = dict(source='photo2/RETROSPECTIVE.md', source_commit=SOURCE_COMMIT,
                  source_sha256=original_hash, pdf='photo2/RETROSPECTIVE.pdf',
                  pdf_sha256=sha(PDF), pages=pages, bytes=PDF.stat().st_size,
                  format='US Letter; searchable tagged text, bookmarks, linked contents, embedded figures',
                  markdown_it_py=importlib.metadata.version('markdown-it-py'),
                  chromium=version, exported_at=datetime.now(timezone.utc).isoformat(),
                  text_blocks_verified=len(blocks), headings=len(headings),
                  word_bounds_verified=words_checked, linked_contents_destinations=linked_sections,
                  figures=[dict(path=str(Path(unquote(urlparse(f['src']).path)).relative_to(ROOT)),
                                sha256=sha(Path(unquote(urlparse(f['src']).path))),
                                width=f['width'], height=f['height']) for f in figures],
                  checks=dict(all_source_text_blocks_present=True, images_loaded=True,
                              no_horizontal_overflow=True, no_local_file_hyperlinks=True,
                              markdown_source_unchanged=True, failed_requests=failed))
    RECEIPT.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
