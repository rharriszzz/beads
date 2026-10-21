"""Validate/export the illustrated explanation. No scientific inputs are written."""
from html import escape
from pathlib import Path
from urllib.parse import unquote, urlparse
import hashlib
import json
import re
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'photo2/PATTERN_VISIBILITY_ILLUSTRATED.md'
PDF = SOURCE.with_suffix('.pdf')
BASELINE = '81a6be1f63344ffdf9cac1920ec304822c73460f'
BRANCH = 'photo-2-strategy-v3'
PUBLIC = 'https://github.com/rharriszzz/beads/blob/'
CSS = '''
@page {size:Letter;margin:18mm 16mm 18mm;}
* {box-sizing:border-box}
body {font:10.5pt/1.43 'DejaVu Sans',sans-serif;color:#20303d;margin:0;}
h1 {font-size:25pt;line-height:1.14;color:#173a52;margin:0 0 6mm}
h2 {font-size:16pt;line-height:1.2;color:#173a52;margin:7mm 0 3mm}
h3 {font-size:12pt;line-height:1.25;color:#173a52;margin:5mm 0 3mm}
h1,h2,h3 {break-after:avoid}
p {margin:0 0 3.2mm;orphans:3;widows:3;break-inside:avoid}
a {color:#145975;text-decoration:none;overflow-wrap:anywhere}
ul {padding-left:6mm;margin:2mm 0 4mm}
li {margin:0 0 2mm;orphans:3;widows:3}
code {font: .87em 'DejaVu Sans Mono',monospace;overflow-wrap:anywhere}
pre {padding:3mm;background:#f2f6f8;border:.25mm solid #d6e0e6;
 font-size:9pt;line-height:1.4;break-inside:avoid;white-space:pre-wrap;margin:4mm 0}
pre code {font-size:inherit}
table {width:100%;border-collapse:collapse;font-size:9pt;line-height:1.4;margin:4mm 0 5mm;break-inside:avoid}
th,td {padding:1.6mm 1.5mm;border:.25mm solid #ccd6df;text-align:left;vertical-align:top}
th {background:#e8f0f4;color:#173a52}
tr {break-inside:avoid}
thead {display:table-header-group}
tr:nth-child(even) td {background:#f7f9fb}
figure {break-inside:avoid;margin:5mm 0}
figure img {width:100%;height:auto;max-height:173mm;object-fit:contain;display:block}
figcaption {font-size:9pt;line-height:1.4;color:#4c606f;margin-top:2.5mm}
figure.chart {break-before:page;break-after:page;margin:0}
figure.chart img {max-height:210mm}
figure.chart figcaption {font-size:8.7pt}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compact(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC',text))


def validate_source(text, verification):
    data=json.loads((HERE.parent/'visibility-example-checks.json').read_text())
    rows=re.findall(r'\| (\d+)–(\d+) \| `([RYB?]+)` \| `([RYBb]+)` \|',text)
    assert len(rows)==16
    assert ''.join(r[2] for r in rows)==data['actual_current_strict_sequence']
    assert ''.join(r[3] for r in rows)==data['actual_marked_candidate_sequence']
    assert [(int(a),int(b)) for a,b,_,_ in rows]==[(i,i+12) for i in range(0,208,13)]
    for key in ['pattern_A','pattern_B','pattern_27']:
        word=verification['revised_toys'][key]
        grouped=' '.join(word[i:i+13] for i in range(0,len(word),13))
        assert grouped in text
    for chunk in [data['middle_example']['word'][i:i+13] for i in range(0,52,13)]:
        assert chunk in text
    assert verification['front_A_equals_B'] and verification['changed_body_front_surface_pixels']==0
    for path,digest in verification['actual_source_sha256'].items():
        assert sha(ROOT/path)==digest
    assessment=json.loads((ROOT/'photo2/r347/answers/assessment.json').read_text())
    entries=assessment['epochs']['maker_assessment']['entries']
    assert sum(e['status']=='supported' for e in entries)==201
    assert sum(e['status']=='conflicting' for e in entries)==0
    assert len(data['actual_insufficient_positions'])==7


def main():
    source_hash=sha(SOURCE)
    text=SOURCE.read_text()
    verification=json.loads((HERE/'verification.json').read_text())
    validate_source(text,verification)
    md=MarkdownIt('commonmark').enable('table')
    tokens=md.parse(text)
    headings=[];links=[]
    for i,t in enumerate(tokens):
        if t.type=='heading_open':
            anchor='section-'+str(len(headings)+1)
            t.attrSet('id',anchor)
            headings.append(dict(text=tokens[i+1].content,tag=t.tag,anchor=anchor))
        if t.type=='inline':
            for child in t.children or []:
                if child.type not in ['link_open','image']:
                    continue
                attr='src' if child.type=='image' else 'href'
                href=child.attrGet(attr);url=urlparse(href)
                if url.scheme or not url.path:
                    continue
                target=(SOURCE.parent/unquote(url.path)).resolve()
                assert target.exists(),target
                rel=target.relative_to(ROOT).as_posix()
                if child.type=='image':
                    child.attrSet(attr,target.as_uri())
                else:
                    old=subprocess.run(['git','cat-file','-e',f'{BASELINE}:{rel}'],cwd=ROOT,
                                       stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
                    child.attrSet(attr,PUBLIC+(BASELINE if old else BRANCH)+'/'+rel+
                                  ('#'+url.fragment if url.fragment else ''))
                    links.append(dict(path=rel,revision=BASELINE if old else BRANCH))
    body=md.renderer.render(tokens,md.options,{})
    html=f'<!doctype html><html lang="en"><meta charset="utf-8"><title>Why a hidden bead pattern can still be recovered</title><style>{CSS}</style><main>{body}</main></html>'
    failed=[]
    with tempfile.TemporaryDirectory(prefix='beads-visibility-pdf-') as temp:
        htmlpath=Path(temp)/'review.html';htmlpath.write_text(html)
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            version=browser.version
            page=browser.new_page(viewport={'width':695,'height':1000})
            page.on('requestfailed',lambda request:failed.append(request.url))
            page.goto(htmlpath.as_uri())
            page.evaluate('document.fonts.ready')
            assert page.locator('img').count()==8
            assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
            page.evaluate('''() => {for(const p of document.querySelectorAll('main p')) {
              if(p.children.length===1 && p.firstElementChild.tagName==='IMG') {
                const img=p.firstElementChild, figure=document.createElement('figure');
                if(img.src.includes('05-full-pattern')) figure.className='chart';
                p.replaceWith(figure);figure.append(img);
                const caption=figure.nextElementSibling;
                if(caption?.tagName==='P' && caption.firstElementChild?.tagName==='EM') {
                  const c=document.createElement('figcaption');c.innerHTML=caption.innerHTML;
                  figure.append(c);caption.remove();
                }
              }
            }}''')
            blocks=page.locator('main h1,main h2,main h3,main p,main li,main td,main th,main pre,main figcaption').all_inner_texts()
            images=page.locator('img').evaluate_all('(xs)=>xs.map(x=>({src:x.src,width:x.naturalWidth,height:x.naturalHeight}))')
            assert not failed
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            page.pdf(path=str(PDF),print_background=True,prefer_css_page_size=True,
                     display_header_footer=True,outline=True,tagged=True,
                     header_template='<div style="font:8px DejaVu Sans;color:#687782;margin:0 16mm">Bead patterns · Illustrated explanation</div>',
                     footer_template='<div style="font:8px DejaVu Sans;color:#687782;margin:0 16mm;width:100%;text-align:right">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>')
            browser.close()
    extracted=subprocess.check_output(['pdftotext','-raw',str(PDF),'-'],text=True)
    cleaned=re.sub(r'Page \d+ of \d+','',extracted.replace('Bead patterns · Illustrated explanation',''))
    missing=[b for b in blocks if compact(b) not in compact(cleaned)]
    assert not missing,repr(missing[:3])
    bbox=ET.fromstring(subprocess.check_output(['pdftotext','-bbox',str(PDF),'-']))
    ns={'x':'http://www.w3.org/1999/xhtml'};bounds=0
    for p in bbox.findall('.//x:page',ns):
        for w in p.findall('.//x:word',ns):
            assert 0<=float(w.attrib['xMin'])<=float(w.attrib['xMax'])<=float(p.attrib['width'])
            assert 0<=float(w.attrib['yMin'])<=float(w.attrib['yMax'])<=float(p.attrib['height'])
            bounds+=1
    info=subprocess.check_output(['pdfinfo',str(PDF)],text=True)
    urls=subprocess.check_output(['pdfinfo','-url',str(PDF)],text=True)
    assert 'file:' not in urls
    assert sha(SOURCE)==source_hash
    receipt=dict(source=str(SOURCE.relative_to(ROOT)),source_sha256=source_hash,
                 pdf=str(PDF.relative_to(ROOT)),pdf_sha256=sha(PDF),
                 pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M).group(1)),
                 bytes=PDF.stat().st_size,chromium=version,
                 format='US Letter; searchable tagged text; bookmarks; embedded images',
                 text_blocks_verified=len(blocks),word_bounds_verified=bounds,
                 link_paths_checked=links,figures=[dict(path=str(Path(unquote(urlparse(i['src']).path)).relative_to(ROOT)),
                     sha256=sha(Path(unquote(urlparse(i['src']).path))),width=i['width'],height=i['height']) for i in images],
                 checks=dict(all_text_present=True,images_loaded=True,no_horizontal_overflow=True,
                     no_local_file_hyperlinks=True,full_208_table_matches_saved_candidate_and_R347=True,
                     illustrated_words_match_verification=True,scientific_input_hashes_unchanged=True))
    (HERE/'pdf-export.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
