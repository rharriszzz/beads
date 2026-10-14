"""Inspect the frozen sample BEFORE development; old/J differences are not truth."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r285-mpl')
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r282.common import ROOT,read,photo,pixels
from .select import OUT,bank
REVIEW=ROOT/'photo2/review/r285'

def main():
    REVIEW.mkdir(parents=True,exist_ok=True);native,_,_=photo();obs={o['id']:o for o in bank()};rows=read(OUT/'selection.json')['development'];thumbs=[]
    for r in rows:
        o=obs[r['observation_id']];origin=np.array(o['seed'])-40;x,y=origin;im=native[y:y+81,x:x+81];Image.fromarray(im).save(REVIEW/(r['example']+'-native.png'))
        fig,axs=plt.subplots(1,4,figsize=(12,3.3));a=o['variants']['A'];j=o['variants']['J'];pa=set(map(tuple,pixels(a['measured_support'])));pj=set(map(tuple,pixels(j['measured_support'])))
        for ax in axs:ax.imshow(im,interpolation='nearest');ax.set_xlim(0,80);ax.set_ylim(80,0);ax.set_xticks([]);ax.set_yticks([])
        axs[0].set_title('Unmodified photo enlarged')
        for ax,m in zip(axs[1:3],('A','J')):
            rr=o['variants'][m];c=np.array(rr['subpixel_contour'])-origin
            if len(c):ax.plot(c[:,0],c[:,1],color='cyan',lw=1)
            if rr['measured_photo_location']:ax.plot(*(np.array(rr['measured_photo_location'])-origin),'+',color='white')
            ax.plot(40,40,'x',color='orange');ax.set_title(m+f" / {rr['metrics']['area']} pixels")
        for pts,color in [(pa-pj,'red'),(pj-pa,'lime')]:
            pts=np.array(sorted(pts)).reshape(-1,2)-origin
            if len(pts):axs[3].scatter(pts[:,0],pts[:,1],s=4,c=color,alpha=.7,marker='s',linewidths=0)
        axs[3].set_title('J loss red / gain green\nA is NOT ground truth')
        fig.suptitle(r['example']+' '+r['category']+' / '+r['color']);fig.tight_layout();path=REVIEW/(r['example']+'-baseline.png');fig.savefig(path,dpi=125);plt.close(fig);thumbs.append(Image.open(path).convert('RGB'))
    for k in range(4):
        selected=thumbs[k*4:k*4+4];canvas=Image.new('RGB',(selected[0].width,sum(x.height for x in selected)),'white');y=0
        for im in selected:canvas.paste(im,(0,y));y+=im.height
        canvas.save(REVIEW/f'selection-sheet-{k+1}.png')

if __name__=='__main__':main()
