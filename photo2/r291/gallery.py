"""Native-photo development diagnostics; saved results only."""
import argparse
from PIL import Image,ImageDraw
from .common import *

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['development','retrospective','reserved']);a=p.parse_args();rows=read(OUT/(a.stage+'.json.gz'))['records']
    sheet=Image.new('RGB',(1200,((len(rows)+7)//8)*180),'#eee');d=ImageDraw.Draw(sheet)
    for i,r in enumerate(rows):
        im=Image.open(OUT/'crops'/(r['case_id']+'.png'));scale=140/im.width;im=im.resize((140,140),Image.Resampling.NEAREST);draw=ImageDraw.Draw(im)
        for s in r['A']['segments']:
            points=[((x-r['box'][0]+.5)*scale,(y-r['box'][1]+.5)*scale) for x,y in s['endpoints']];draw.line(points,fill='#00e1ed' if s['supported'] else '#ffb342',width=1)
        p=r['feature']['point'];x=(p[0]-r['box'][0]+.5)*scale;y=(p[1]-r['box'][1]+.5)*scale;draw.ellipse((x-2,y-2,x+2,y+2),outline='white')
        x=(i%8)*150;y=(i//8)*180;sheet.paste(im,(x,y));d.text((x,y+142),r['case_id'],fill='black');d.text((x,y+155),f"{r['A']['candidate_pixels']['pixel_count']}px {r['A']['evidence']['T7']['supported_fraction']:.0%}",fill='black')
    sheet.save(OUT/(a.stage+'-overview.png'));print('Saved',a.stage,'overview')

if __name__=='__main__':main()
