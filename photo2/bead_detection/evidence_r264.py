"""Explicit assistant visual judgments and native HSV diagnostics, never runtime priors."""
import csv
import gzip
import json
import numpy as np
from PIL import Image, ImageOps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from .hue_r264 import ROOT, WORK, OUT, HUES
from .bounded_detect import save

# Review observations, not physical centers, measured boundaries or maker labels.
DUPLICATES=[
 ('R00956',['P093728','P093784'],'partly cropped red body'),
 ('R01284',['P126280','P126338'],'partly cropped upper red body'),
 ('R01284',['P128275','P128915'],'central yellow body'),
 ('R01284',['P129734','P130143'],'lower yellow body'),
 ('pair',['P032240','P032353'],'central red body'),
 ('pair',['P032495','P032732'],'left red body'),
 ('R01307',['P133010','P133073'],'one bright reflection on dark body'),
 ('top-transition',['P014974','P015269'],'yellow body near 1281,304'),
 ('top-transition',['P015149','P015350'],'red body near 1237,312'),
 ('top-transition',['P015270','P015849'],'yellow body near 1307,315'),
 ('inner-transition',['P071430','P071619'],'red body near 1524,1487'),
 ('inner-transition',['P072237','P072238'],'red body near 1544,1500'),
]
MISSES=[
 ('R00956',[2255,1919],'yellow below the rim-supported middle yellow','stronger',list(HUES)),
 ('R01284',[1005,2678],'shadowed yellow to the right of the duplicated yellow','stronger',list(HUES)),
 ('R01307',[1929,2712],'pale upper colored body; precise color uncertain','stronger',list(HUES)),
 ('R01307',[1920,2761],'lower yellow body','stronger',list(HUES)),
 ('inner-transition',[1601,1445],'shadowed red-looking patch; separate body plausible, identity less certain','tentative',list(HUES)),
 ('top-transition',[1342,276],'red body whose P013502 proposal exceeds the cap at hue >=10','stronger',[10,12,15,20]),
]


def native_line(a,b):
    # Integer Bresenham route: every sampled point is an original pixel.
    x,y=a;xx,yy=b;dx=abs(xx-x);dy=-abs(yy-y);sx=1 if x<xx else -1;sy=1 if y<yy else -1;err=dx+dy
    out=[]
    while True:
        out.append((x,y))
        if (x,y)==(xx,yy):return out
        e=2*err
        if e>=dy:err+=dy;x+=sx
        if e<=dx:err+=dx;y+=sy


def main():
    rgb=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'))
    hsv=rgb_to_hsv(rgb/255.)*[360,1,1]
    comparison=json.loads((OUT/'comparison.json').read_text())
    data={h:json.loads((WORK/str(h)/'regions.json').read_text()) for h in HUES}
    records={h:{r['id']:r for r in d['regions']+d['rejected']} for h,d in data.items()}
    ds=[]
    for i,(case,ids,note) in enumerate(DUPLICATES,1):
        ds.append(dict(label=f'D{i}',case=case,ids=ids,judgment=note,confidence='likely same body; assistant visual judgment',
                       by_hue={h:[dict(id=rid,status=records[h][rid]['status'],coordinate=records[h][rid]['location']) for rid in ids] for h in HUES}))
    ms=[]
    for i,(case,xy,note,confidence,hues) in enumerate(MISSES,1):
        near=sorted(data[8]['maxima'],key=lambda m:np.linalg.norm(np.array(m['peak'])-xy))[:4]
        ms.append(dict(label=f'M{i}',case=case,approximate_review_location=xy,judgment=note,confidence=confidence,missing_hues=hues,
                       nearest_raw_maxima_hue8=[{k:m[k] for k in ['id','region_id','peak','value_dn','meaningful','reason']} for m in near]))
    result=dict(provenance='Assistant visual review, not maker-confirmed truth; six purposive diagnostic crops, not exhaustive coverage',
                counting='12 likely two-support same-body groups: 24 participating supports, 12 apparent extras. All persist at all six settings. Not every support/cropped body is assigned. No inference from IoU alone.',
                duplicates=ds,missing=ms,
                missing_counts={h:dict(stronger=sum(m['confidence']=='stronger' and h in m['missing_hues'] for m in ms),tentative=sum(m['confidence']=='tentative' and h in m['missing_hues'] for m in ms)) for h in HUES},
                weak_location=dict(id='P091744',counted='detected but weak, not a missing location',question='Q264.1 pending maker review'),
                exclusions='Unclear dark bodies without obvious reflections and crop slivers are not declared misses. No full-photo missing count or statistical extrapolation.')
    save(OUT/'visual-review.json',result)
    fig,axes=plt.subplots(2,3,figsize=(15,10))
    for ax,c in zip(axes.flat,comparison['cases'][:6]):
        x0,y0,x1,y1=c['box'];ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest')
        for d in ds:
            if d['case']!=c['name']:continue
            xy=np.mean([r['coordinate'] for r in d['by_hue'][8]],axis=0)
            ax.plot(*xy,'+',color='cyan');ax.text(*xy,d['label'],color='cyan',fontsize=10)
        for m in ms:
            if m['case']!=c['name']:continue
            x,y=m['approximate_review_location'];ax.plot(x,y,'o',mfc='none',mec='white',ms=16);ax.text(x+2,y,m['label'],color='white',fontsize=10)
        ax.set(title=c['name'],xlim=(x0-.5,x1-.5),ylim=(y1-.5,y0-.5));ax.tick_params(labelsize=8)
    fig.suptitle('Review landmarks only: D = likely duplicated body; M = plausible missing location (M5 tentative; M6 only >=10°)')
    fig.tight_layout();fig.savefig(OUT/'visual-review.png',dpi=150);plt.close(fig)
    routes=[('red interior, brighter to darker',(1570,1453),(1579,1456)),
            ('yellow interior, brighter to darker',(1591,1476),(1605,1480)),
            ('shadowed red toward yellow, includes intervening boundary/gap',(1601,1445),(1624,1455))]
    fig,axes=plt.subplots(3,2,figsize=(11,10));export=[];stats=[]
    for (name,a,b),(ax,plot) in zip(routes,axes):
        x0,y0,x1,y1=[1535,1425,1640,1500]
        ax.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest')
        route=native_line(a,b);xy=np.array(route);ax.plot(xy[:,0],xy[:,1],'.-',color='cyan',lw=.6,ms=2)
        ax.text(*a,'A',color='white');ax.text(*b,'B',color='white');ax.set_title(name,fontsize=10)
        vals=np.array([hsv[y,x] for x,y in route]);h=(vals[:,0]+180)%360-180
        plot.plot(h,label='H (signed degrees)',color='#b63256');plot.set_ylabel('H° (wrap at ±180)');plot.set_xlabel('Native sample number, A → B')
        twin=plot.twinx();twin.plot(vals[:,1],label='S',color='#298037');twin.plot(vals[:,2],label='V',color='#1c6ac4');twin.set_ylim(0,1.05);twin.set_ylabel('S / V');plot.legend(loc='upper left');twin.legend(loc='upper right')
        for i,((x,y),q) in enumerate(zip(route,vals)):
            export.append([name,i,x,y,*map(int,rgb[y,x]),*q])
        stats.append(dict(name=name,start=list(a),end=list(b),start_hsv=vals[0].tolist(),end_hsv=vals[-1].tolist(),
                          circular_endpoint_hue_change=float(abs((vals[-1,0]-vals[0,0]+180)%360-180)),samples=len(route)))
    fig.tight_layout();fig.savefig(OUT/'hsv-routes.png',dpi=150);plt.close(fig)
    with (OUT/'hsv-routes.csv').open('w') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['route','sample','x','y','r','g','b','H_deg','S','V']);writer.writerows(export)
    save(OUT/'hsv-routes.json',stats)
    save(OUT/'missing-seed-diagnostics.json',ms)
    # Small conservative paper review window; semantic label remains visual.
    box=[1992,2628,1998,2635]
    counts={}
    for hue,d in data.items():
        hits={}
        for r in d['regions']:
            n=sum(1 for y,a,b in r['pixel_runs'] for x in range(a,b+1)
                  if box[0]<=x<box[2] and box[1]<=y<box[3])
            if n:hits[r['id']]=n
        counts[hue]=hits
    save(OUT/'paper-window.json',dict(box=box,classification='Assistant judgment: paper-dominated exterior beside a red bead; not a verified segmentation',support_pixels=counts))
    from .analyze_r264 import leaf_control
    leaves=json.loads((OUT/'leaf-control.json').read_text())
    worst=max((r for r in leaves if r['hue']==8),key=lambda r:r['coordinate_shift'])
    ids=[worst['id'],'P032353','P091744']
    fig,axes=plt.subplots(3,2,figsize=(10,12))
    for rid,(ax,bx) in zip(ids,axes):
        r=records[8][rid]
        with gzip.open(WORK/'8'/r['trace_file'],'rt') as f:t=json.load(f)
        control,restored=leaf_control(t,data[8]['parameters'])
        x,y=r['location'];box=[x-23,y-23,x+24,y+24];x0,y0,x1,y1=box
        for a in (ax,bx):
            a.imshow(rgb[y0:y1,x0:x1],extent=(x0-.5,x1-.5,y1-.5,y0-.5),interpolation='nearest')
            for curve in r['contours']:
                q=np.array(curve);a.plot(q[:,0],q[:,1],color='cyan',lw=.6)
            a.plot(*r['location'],'+',color='white',ms=10)
            a.set(xlim=(x0-.5,x1-.5),ylim=(y1-.5,y0-.5))
        for i in restored:bx.plot(*t['accepted'][i][:2],'.',color='lime',ms=2)
        bx.plot(*control['location'],'x',color='yellow',ms=10)
        ax.set_title(rid+' · production 8°')
        bx.set_title('Leaf sensitivity only · yellow × alternative')
    fig.tight_layout();fig.savefig(OUT/'leaf-coordinate-control.png',dpi=140);plt.close(fig)
    print(json.dumps(result['missing_counts'],indent=2))


if __name__=='__main__':main()
