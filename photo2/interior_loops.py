"""R157 diagnostic interior loops from maker marks and local HSV evidence.

Positive bead interiors only: these are neither bead outlines nor automatic
detections. Manual marks/selected numbers are explicit diagnostic assistance.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-matplotlib')
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from scipy.ndimage import label,distance_transform_edt,binary_fill_holes
from scipy.spatial import cKDTree

ROOT=Path(__file__).resolve().parents[1]
HELD={22,23,24,25}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def angle_delta(a,b):return (a-b+180)%360-180


def component_at(mask,point):
    labels,count=label(mask)
    x,y=point
    ident=labels[y,x]
    if not ident:
        yy,xx=np.where(mask)
        if not len(xx):return np.zeros_like(mask)
        nearest=np.argmin((xx-x)**2+(yy-y)**2)
        if (xx[nearest]-x)**2+(yy[nearest]-y)**2>16:return np.zeros_like(mask)
        ident=labels[yy[nearest],xx[nearest]]
    return labels==ident


def summarize(hsv,mask,reference=None,use_hue=True):
    q=hsv[mask]
    if not len(q):return None
    result=dict(pixels=int(mask.sum()),hue_used=use_hue,
        saturation_p10_p50_p90=np.percentile(q[:,1],[10,50,90]).tolist(),
        value_p10_p50_p90=np.percentile(q[:,2],[10,50,90]).tolist())
    if use_hue:
        hue=q[:,0]*360
        if reference is None:reference=float(np.degrees(np.angle(np.mean(np.exp(1j*np.radians(hue)))))%360)
        result.update(hue_reference_deg=reference,
            hue_delta_p10_p50_p90_deg=np.percentile(angle_delta(hue,reference),[10,50,90]).tolist())
    return result


def extract(rgb,annotations,number,margin=3):
    rows={a['number']:a for a in annotations if a['number'] not in HELD}
    row=rows[number];seed=np.array([row['x'],row['y']])
    nearest=min(np.linalg.norm(seed-[a['x'],a['y']]) for n,a in rows.items() if n!=number)
    leash=.45*nearest
    x0,y0=np.floor(seed-leash-2).astype(int);x1,y1=np.ceil(seed+leash+3).astype(int)
    hsv=rgb_to_hsv(rgb[y0:y1,x0:x1]);yy,xx=np.mgrid[y0:y1,x0:x1]
    distance=np.hypot(xx-seed[0],yy-seed[1]);disk=distance<=leash
    local=distance<=3.5
    initial=summarize(hsv,local)
    median_s=initial['saturation_p10_p50_p90'][1]
    median_v=initial['value_p10_p50_p90'][1]
    point=np.rint(seed-[x0,y0]).astype(int)
    parameters=dict(leash_fraction_of_nearest_training_mark=.45,leash_px=float(leash),
                    interior_inset_px=margin,seed_patch_radius_px=3.5)
    highlight=None
    if median_s>.45 and median_v>.4:
        useful=local&(hsv[:,:,1]>.45)&(hsv[:,:,2]>.4)
        hue=summarize(hsv,useful)['hue_reference_deg']
        spread=np.percentile(np.abs(angle_delta(hsv[:,:,0][useful]*360,hue)),90)
        hue_width=max(14.,float(spread)*1.6)
        smin=float(np.percentile(hsv[:,:,1][useful],10)*.65)
        vmin=float(np.percentile(hsv[:,:,2][useful],10)*.75)
        support=disk&(np.abs(angle_delta(hsv[:,:,0]*360,hue))<=hue_width)&(hsv[:,:,1]>=smin)&(hsv[:,:,2]>=vmin)
        mode='chromatic';parameters.update(hue_reference_deg=hue,hue_halfwidth_deg=hue_width,
                                          saturation_min=smin,value_min=vmin)
        # Color names are a display convention; they do not choose support pixels.
        name='red' if abs(angle_delta(hue,0))<abs(angle_delta(hue,60)) else 'yellow'
    else:
        mode='reflection-and-dark-surround';name='black candidate';hue=None
        vhi=float(np.percentile(hsv[:,:,2][disk],90))
        slow=float(np.percentile(hsv[:,:,1][disk],40))
        highlight_candidate=disk&(hsv[:,:,2]>=vhi)&(hsv[:,:,1]<=slow)
        candidates,count=label(highlight_candidate)
        choices=[]
        for ident in range(1,count+1):
            mask=candidates==ident
            if mask.sum()<3:continue
            cy,cx=np.mean(np.argwhere(mask),axis=0)
            choices.append((np.linalg.norm(np.array([cx+x0,cy+y0])-seed),mask))
        if not choices:raise ValueError(f'{number}: no supported local reflection; do not invent a loop')
        highlight=min(choices,key=lambda a:a[0])[1]
        vdark=float(np.percentile(hsv[:,:,2][disk],65))
        hstats=summarize(hsv,highlight)
        neutral_max=min(.5,hstats['saturation_p10_p50_p90'][2]+.18)
        highlight_distance=distance_transform_edt(~highlight)
        nearby=highlight_distance<=7
        support=disk&nearby&((hsv[:,:,2]<=vdark)|(hsv[:,:,1]<=neutral_max)|highlight)
        support|=disk&(highlight_distance<=4)
        parameters.update(highlight_value_min=vhi,highlight_saturation_max=slow,
            dark_surround_value_max=vdark,neutral_transition_saturation_max=neutral_max,
            reflection_neighborhood_px=7,local_reflection_transition_fill_px=4,
            highlight=summarize(hsv,highlight,use_hue=False))
    support=component_at(support,point)
    # Unknown holes/gaps remain excluded. A closed contour does not turn an
    # enclosed pixel into bead evidence merely because it is enclosed.
    support&=disk
    safe=distance_transform_edt(support)>=margin+1
    safe=component_at(safe,point)
    if not safe.any():raise ValueError(f'{number}: no conservative inset core')
    if np.any(binary_fill_holes(safe)&~safe):
        raise ValueError(f'{number}: inset contains an unresolved hole; do not fill it as bead')
    fig,ax=plt.subplots()
    paths=ax.contour(xx,yy,safe.astype(float),levels=[.5]).allsegs[0]
    plt.close(fig)
    closed=[p for p in paths if len(p)>3 and np.allclose(p[0],p[-1])]
    if not closed:raise ValueError(f'{number}: no closed interior loop')
    loop=max(closed,key=len)
    # The dense closed contour is the sampling route, not an estimated edge.
    rounded=np.rint(loop).astype(int)
    line=np.zeros_like(safe)
    line[rounded[:,1]-y0,rounded[:,0]-x0]=True
    ring=safe if highlight is None else safe&~highlight
    if safe.sum()<16:raise ValueError(f'{number}: inset leaves only {safe.sum()} pixels; retain as unresolved')
    rejected=np.column_stack((xx[~support],yy[~support]))
    contour_margin=float(cKDTree(rejected).query(loop)[0].min())
    if contour_margin<margin:raise ValueError(f'{number}: loop approaches support rejection too closely')
    chromatic=mode=='chromatic'
    result=dict(number=number,observation_id=row['id'],seed_xy=seed.tolist(),mode=mode,
        display_color=name,parameters=parameters,crop=[int(x0),int(y0),int(x1),int(y1)],
        loop_xy=loop.tolist(),enclosed_core=summarize(hsv,safe,hue,chromatic),
        loop_samples=summarize(hsv,line,hue,chromatic),nonhighlight_core=summarize(hsv,ring,hue,chromatic),
        minimum_core_distance_to_support_rejection_px=float(distance_transform_edt(support)[safe].min()),
        minimum_contour_distance_to_support_rejection_px=contour_margin,
        enclosed_pixels=int(safe.sum()),status='conservative diagnostic proposal; maker review pending')
    return result


def draw(ax,rgb,crop,result=None):
    x0,y0,x1,y1=crop
    ax.imshow(rgb[y0:y1,x0:x1],extent=[x0-.5,x1-.5,y1-.5,y0-.5],interpolation='nearest')
    ax.set_xlim(x0,x1);ax.set_ylim(y1,y0)
    if result:
        loop=np.array(result['loop_xy']);ax.plot(loop[:,0],loop[:,1],color='lime',lw=1.3)
        ax.plot(*result['seed_xy'],'+',color='white',ms=5,mew=.8)
    ax.set_xlabel('oriented source x');ax.set_ylabel('source y')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers',type=int,nargs='+',default=[8,11,14,17,20])
    parser.add_argument('--inset',type=int,default=3)
    args=parser.parse_args()
    image=ROOT/'beads-photo-2.jpg';save=ROOT/'photo2/manual-labels-r146.json'
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(image)).convert('RGB'))/255
    annotations=json.loads(save.read_text())['annotations']
    results=[extract(rgb,annotations,n,args.inset) for n in args.numbers]
    out=ROOT/'photo2/review/r157';out.mkdir(parents=True,exist_ok=True)
    fig,axs=plt.subplots(2,len(results),figsize=(3*len(results),6),constrained_layout=True,squeeze=False)
    for i,result in enumerate(results):
        x,y=result['seed_xy'];crop=[int(x)-24,int(y)-27,int(x)+25,int(y)+28]
        draw(axs[0,i],rgb,crop);axs[0,i].set_title(f'Raw: bead {result["number"]}',fontsize=10)
        draw(axs[1,i],rgb,crop,result);axs[1,i].set_title(result['display_color']+' interior loop',fontsize=10)
    fig.suptitle('Q157.1: green loops must remain comfortably inside one bead.\nSame raw pixels above; no predicted bead outlines. White + = existing maker mark.',fontsize=11)
    fig.savefig(out/'interior-review.png',dpi=170);plt.close(fig)
    crop=[1180,130,1540,520]
    fig,axs=plt.subplots(1,2,figsize=(10,6),constrained_layout=True)
    draw(axs[0],rgb,crop);axs[0].set_title('Raw wider context')
    draw(axs[1],rgb,crop);axs[1].set_title('Five conservative interior loops only')
    for result in results:
        loop=np.array(result['loop_xy']);axs[1].plot(loop[:,0],loop[:,1],color='lime',lw=1.1)
        x,y=np.mean(loop,axis=0);axs[1].text(x+4,y-4,str(result['number']),color='white',fontsize=9,
            bbox=dict(facecolor='black',alpha=.5,pad=.2,edgecolor='none'))
    fig.savefig(out/'wider-interiors.png',dpi=160);plt.close(fig)
    report=dict(image_sha256=sha(image),annotation_sha256=sha(save),script_sha256=sha(__file__),
        coordinate_system='EXIF oriented source pixels; x right, y down',hsv_units='H degrees (circular); S/V 0–1',
        heldout_numbers_excluded=sorted(HELD),assistance='Maker marks and chosen central bead numbers; not automatic reconstruction',
        meaning='Positive interior evidence only; outside pixels unknown, no inferred silhouette or outward anchor',
        results=results)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([dict(number=r['number'],mode=r['mode'],color=r['display_color'],
        enclosed_pixels=r['enclosed_pixels'],loop_samples=r['loop_samples'],parameters=r['parameters']) for r in results],indent=2))


if __name__=='__main__':main()
