"""Unmodified native-photo comparisons with thin automatic outlines."""
import argparse
from PIL import Image,ImageDraw
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','reserved','start','r292-feedback']);a=p.parse_args();native,_,_=photo()
    if a.stage=='r292-feedback':rows=[read(ROOT/q['candidate_path']) for q in read(EVIDENCE/'r292-review-analysis.json')['records']]
    elif a.stage=='start':rows=[read(REVIEW/'data'/(cid+'.json')) for cid in read(REVIEW/'manifest.json')['start_here']]
    else:rows=read(OUT/(a.stage+'.json.gz'))['records']
    for batch in range((len(rows)+7)//8):
        group=rows[batch*8:(batch+1)*8];sheet=Image.new('RGB',(1040,290*((len(group)+1)//2)),'#222');dr=ImageDraw.Draw(sheet)
        for i,r in enumerate(group):
            p=r['feature']['point'];rect=[p[0]-30,p[1]-30,p[0]+31,p[1]+31]
            for j,label in enumerate(('Original','Automatic visible-region proposal')):
                x0=(i%2)*520+j*260;y0=(i//2)*290;im=Image.fromarray(native[rect[1]:rect[3],rect[0]:rect[2]]).resize((244,244),Image.Resampling.NEAREST);ink=ImageDraw.Draw(im)
                if j:
                    for s in r['A']['segments']:ink.line([((q[0]-rect[0]+.5)*4,(q[1]-rect[1]+.5)*4) for q in s['endpoints']],fill='#00eeee' if s['supported'] else '#ffae42',width=1)
                    ink.ellipse((119,119,125,125),outline='white')
                sheet.paste(im,(x0,y0+35));dr.text((x0+3,y0+3),r['case_id']+'\n'+label,fill='white')
        sheet.save(OUT/f'{a.stage}-{batch+1:02}.png')
    print('Saved',a.stage,len(rows),'original-photo comparisons')
if __name__=='__main__':main()
