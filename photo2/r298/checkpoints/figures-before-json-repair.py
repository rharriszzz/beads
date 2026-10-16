"""Native raw/old/new panels and standalone scientific error plots."""
from PIL import Image,ImageDraw
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .calibrate import *
from photo2.r297.common import photo

def main():
    review=ROOT/'photo2/review/r298';sel=read(BASE/'results/selection.json');a=read(BASE/'results/model-0.json.gz');b=read(BASE/f"results/model-{sel['primary']}.json.gz");m=measurements();rgb,_,_=photo();im=Image.fromarray(rgb).convert('RGBA');old=Image.open(review/'surfaces-0.png');new=Image.open(review/f"surfaces-{sel['primary']}.png");audit=[]
    for j,r in enumerate(m['beads']):
        x,y=np.rint(r['point']).astype(int);box=(x-70,y-70,x+70,y+70);raw=im.crop(box);raw.convert('RGB').save(review/f'raw-{r["id"]}.png');can=Image.new('RGB',(840,308),'white');draw=ImageDraw.Draw(can)
        for i,overlay in enumerate([None,old,new]):
            crop=raw.copy()
            if overlay is not None:
                crop=Image.alpha_composite(crop,overlay.crop(box));d=ImageDraw.Draw(crop);poly=np.array(r['polygon'])-[box[0],box[1]];d.line([tuple(v) for v in poly]+[tuple(poly[0])],fill=(215,160,255,255),width=1)
            can.paste(crop.convert('RGB').resize((280,280)),(280*i,24));draw.text((280*i+6,5),['Original unmarked','R297 + uncertain measured contour','R298 + uncertain measured contour'][i],fill='black')
        can.save(review/f'comparison-{r["id"]}.png');xy=np.rint(r['polygon']).astype(int);audit.append(dict(id=r['id'],raw_box=list(box),raw_crop_sha256=sha(review/f'raw-{r["id"]}.png'),landmark_pixels=xy.tolist(),landmark_rgb=rgb[xy[:,1],xy[:,0]].tolist(),source_region=r['source_region']))
    good=np.array([r['fit_eligible'] for r in m['envelope']]);arc=np.array([r['arc'] for r in m['envelope']]);target=np.array([r['bounds'] for r in m['envelope']]);fig,axs=plt.subplots(3,1,figsize=(13,9),sharex=True,layout='constrained')
    for model,color,label in [(a,'#aa6c00','R297'),(b,'#008775','R298 primary')]:
        errors=target-np.array(model['envelope']);axs[0].plot(arc[good],np.diff(errors,axis=1).ravel()[good],'.-',color=color,label=label,alpha=.8);axs[1].plot(arc[good],errors.mean(1)[good],'.-',color=color,alpha=.8);axs[2].plot(arc[good],np.diff(np.array(model['envelope']),axis=1).ravel()[good],'.-',color=color,label=label,alpha=.8)
    axs[2].plot(arc[good],np.diff(target,axis=1).ravel()[good],'.',color='#804b9c',label='Observed profile width')
    for ax in axs[:2]:ax.axhline(0,color='gray',lw=.7)
    axs[0].set_ylabel('Measured − predicted width (px)');axs[1].set_ylabel('Common-mode edge residual (px)');axs[2].set_ylabel('Transverse profile width (px)');axs[2].set_xlabel('Image-reference arclength (native px)');axs[0].legend();axs[2].legend();fig.suptitle('Identical eligible photographic profiles; all geography retrospective\nCommon-mode edge residual is axis evidence through surfaces, not measured physical-axis error');fig.savefig(review/'dimensional-errors.png',dpi=150);plt.close(fig)
    save(BASE/'evidence/measurement-audit.json',dict(photo_sha256=sha(ROOT/'beads-photo-2.jpg'),beads=audit))
if __name__=='__main__':main()
