"""Diagnostic contact sheets from saved final candidates and real-photo crops."""
from PIL import Image, ImageDraw
from .common import *

def main():
    for stage in ('development','reserved'):
        rows=read(OUT/(stage+'.json.gz'))['records']
        sheet=Image.new('RGB',(8*150,((len(rows)+7)//8)*180),'#eee');labels=ImageDraw.Draw(sheet)
        for i,r in enumerate(rows):
            im=Image.open(OUT/'crops'/(r['case_id']+'.png'));scale=140/im.width
            im=im.resize((140,140),Image.Resampling.NEAREST);d=ImageDraw.Draw(im)
            for s in r['A']['segments']:
                points=[((x-r['box'][0]+.5)*scale,(y-r['box'][1]+.5)*scale) for x,y in s['endpoints']]
                d.line(points,fill='#00e1ed' if s['supported'] else '#ffb342',width=1)
            p=r['feature']['point'];x=(p[0]-r['box'][0]+.5)*scale;y=(p[1]-r['box'][1]+.5)*scale
            d.line((x-3,y,x+3,y),fill='white');d.line((x,y-3,x,y+3),fill='white')
            x=(i%8)*150;y=(i//8)*180;sheet.paste(im,(x,y))
            labels.text((x,y+142),r['case_id'][:24],fill='black')
            labels.text((x,y+155),f"{r['A']['candidate_pixels']['pixel_count']}px; partial",fill='black')
        sheet.save(OUT/(stage+'-overlays.png'))
    print('Final-data photographic contact sheets saved; no inference changed.')

if __name__=='__main__':main()
