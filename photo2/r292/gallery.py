"""Nearest-neighbor original-photo comparisons; no generated scientific scenes."""
import argparse
from PIL import Image,ImageDraw
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['start','development','reserved']);a=p.parse_args();manifest=read(REVIEW/'manifest.json');ids=manifest['start_here'] if a.stage=='start' else [c['case_id'] for c in manifest['cases'] if c['split']==a.stage];native,_,_=photo()
    for batch in range((len(ids)+3)//4):
        cases=ids[batch*4:(batch+1)*4];sheet=Image.new('RGB',(1200,330*len(cases)),'#202020');dr=ImageDraw.Draw(sheet)
        for row,cid in enumerate(cases):
            r=read(REVIEW/'data'/(cid+'.json'));px,py=r['feature']['point'];rect=[px-34,py-34,px+35,py+35];scale=4
            if r['analysis_limit_reached']:rect=r['box'];scale=276/(rect[2]-rect[0])
            for col,label in enumerate(('Original','R291 reference','R292 A','Observed separator')):
                im=Image.fromarray(native[rect[1]:rect[3],rect[0]:rect[2]]).resize((276,276),Image.Resampling.NEAREST);ink=ImageDraw.Draw(im)
                def xy(q):return ((q[0]-rect[0]+.5)*scale,(q[1]-rect[1]+.5)*scale)
                c=r['baseline']['A'] if label=='R291 reference' and r['baseline'] else r['A'] if label=='R292 A' else None
                if c:
                    for s in c['segments']:ink.line([xy(q) for q in s['endpoints']],fill='#00eeee' if s['supported'] else '#ffae42',width=1)
                if label=='Observed separator':
                    for arc in r['separator_arcs']:
                        ink.line([xy(q) for q in arc['path']],fill='#81f471' if arc['enforced'] else '#f395dd',width=1)
                        for q in (arc['path'][0],arc['path'][-1]):
                            x,y=xy(q);ink.ellipse((x-2,y-2,x+2,y+2),outline='white')
                if label!='Original':
                    x,y=xy(r['feature']['point']);ink.ellipse((x-3,y-3,x+3,y+3),outline='white')
                sheet.paste(im,(col*300,row*330+35));dr.text((col*300+4,row*330+5),f'{cid}\n{"No R291 baseline" if label=="R291 reference" and not r["baseline"] else label}',fill='white')
        sheet.save(OUT/f'{a.stage}-comparison-{batch+1:02}.png')
    print('Saved',a.stage,'photographic comparison sheets:',len(ids),'cases')
if __name__=='__main__':main()
