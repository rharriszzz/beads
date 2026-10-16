"""Photo-only measurement; refuses to replace the frozen ledger."""
import numpy as np
from scipy.ndimage import label
from PIL import Image, ImageDraw
from photo2.bead_detection.brightness_r270 import color_managed_photo,linearize
from photo2.bead_debugger.surface import moments
from photo2.r297.common import pixels
from .common import *

def measure():
    old=read(ROOT/'photo2/review/r276/observations.json')['observations'];rgb,icc=color_managed_photo();lin=linearize(rgb/255.);lum=lin@np.array([.2126,.7152,.0722]);rows=[]
    for r in old:
        xy=np.array(r['xy']);region=pixels({'runs':r['region_runs']});patch=pixels(r['bright_patch'])
        row=dict(id=r['id'],color=r['color'],historical_peak=r['xy'],historical_centroid=r['bright_shape']['centroid'] if r['bright_shape'] else None,historical_patch=r['bright_patch'],positive_interior=r['region_runs'],sector=r['sector'],split='comparison' if r['sector'] in [1,5,9,13] else 'development',historical_specular_candidate=r['specular_candidate'],source='photo2/review/r276/observations.json',selected=False)
        if not len(region):row.update(eligible=False,reason='No positive interior');rows.append(row);continue
        floor=float(np.percentile(lum[region[:,1],region[:,0]],30));values=lum[patch[:,1],patch[:,0]];peak=patch[np.argmax(values)];maximum=float(values.max());sat=r['brightest']['hsv_srgb']['s'];components=[]
        lo=region.min(0);hi=region.max(0);a=np.zeros(tuple((hi-lo+1)[::-1]),bool);a[region[:,1]-lo[1],region[:,0]-lo[0]]=True
        for threshold in [.4,.5,.6]:
            yy,xx=np.mgrid[lo[1]:hi[1]+1,lo[0]:hi[0]+1];mask=a&(lum[yy,xx]>=floor+threshold*(maximum-floor));lab,_=label(mask);v=lab[peak[1]-lo[1],peak[0]-lo[0]];yy,xx=np.where((lab==v)&(v>0));pts=np.c_[xx+lo[0],yy+lo[1]];w=lum[pts[:,1],pts[:,0]]-floor;components.append((pts,moments(pts,w)))
        pts,shape=components[1];sensitivity=max(np.linalg.norm(np.array(m['centroid'])-shape['centroid']) for _,m in components) if shape and all(m for _,m in components) else 100.
        near=patch[values>=maximum*.98];peak_unc=float(np.max(np.linalg.norm(near-peak,axis=1))) if len(near) else 100.
        confidence=bool(r['specular_candidate'] and r['contrast']>=.4 and (sat<=.32 if r['color']!='yellow' else sat<=.55 and r['peak_desaturation']>=.25) and 3<=len(pts)<=90 and sensitivity<=1.5 and peak_unc<=3.)
        row.update(peak=peak.tolist(),centroid=shape['centroid'] if shape else None,shape=shape,patch=pts.tolist(),area_px2=len(pts),peak_rgb_native=r['brightest']['rgb_native'],peak_saturation=sat,contrast=r['contrast'],desaturation=r['peak_desaturation'],threshold_centroids=[m['centroid'] if m else None for _,m in components],centroid_sensitivity_px=float(sensitivity),peak_98percent_radius_px=peak_unc,uncertainty_px=max(1.,sensitivity,peak_unc),eligible=confidence,reason='Localized desaturated peak with contrasted positive interior; specularity probable, not independently proven' if confidence else 'Ambiguous optical type or broad/unstable/weak localization',specular_status='stronger photographic candidate' if confidence else 'ambiguous',background_linear_luminance=floor)
        rows.append(row)
    for sector in range(16):
        for color,quota in [('yellow',2),('red',1),('black',1)]:
            group=[r for r in rows if r['eligible'] and r['sector']==sector and r['color']==color]
            group.sort(key=lambda r:(-(r['contrast']*(1-r['peak_saturation']))/(1+r['centroid_sensitivity_px']),r['id']))
            for r in group[:quota]:r['selected']=True
    # Spatial cross-reference, never transfer the old geometry's owners.
    old257=read(ROOT/'photo2/review/r257/observations.json')['observations']
    for r in rows:
        q=min(old257,key=lambda z:np.linalg.norm(np.array(z['xy'])-r['historical_peak']));dist=float(np.linalg.norm(np.array(q['xy'])-r['historical_peak']))
        r['r257_nearby']=dict(id=q['id'],distance_px=dist,reliable_candidate=q['reliable_candidate']) if dist<=8 else None
    return dict(utc=utc(),photo_sha256=sha(ROOT/'beads-photo-2.jpg'),icc=icc,observations=rows,historical_r257=old257,selection='Photo-only fixed gates; per sector at most 2 yellow/1 red/1 black ranked by contrast, desaturation and threshold sensitivity; no residuals or geometry.',limitations='No calibrated PSF or radiometry. Threshold sensitivity is not a confidence interval. Yellow pigment remains visible; common-light failure cannot alone refute one physical lamp.'),rgb

def montage(doc,rgb):
    chosen=[r for r in doc['observations'] if r['selected']];out=Image.new('RGB',(8*180,((len(chosen)+7)//8)*180),'#20262b');d=ImageDraw.Draw(out)
    for i,r in enumerate(chosen):
        x,y=r['peak'];crop=Image.fromarray(rgb[y-36:y+37,x-36:x+37]).resize((146,146),Image.Resampling.NEAREST);xx=(i%8)*180;yy=(i//8)*180;out.paste(crop,(xx,yy+30));d.text((xx,yy),f"{i} {r['id']}\n{r['color']} s{r['sector']}",fill='white')
    out.save(BASE/'evidence/inspection.png')

def main():
    path=BASE/'evidence/measurements.json.gz'
    if path.exists():raise SystemExit('Frozen measurements exist; use isolated replay')
    doc,rgb=measure();save(path,doc);montage(doc,rgb)
    chosen=[r for r in doc['observations'] if r['selected']]
    save(BASE/'evidence/selection.json',dict(utc=utc(),ids=[r['id'] for r in chosen],measurements_sha256=sha(path),count=len(chosen),colors={c:sum(r['color']==c for r in chosen) for c in ['yellow','red','black']},sectors=sorted(set(r['sector'] for r in chosen)),localization_assessment='3px/5px targets are meaningful engineering tests for selected localized patches; peak ties and 40/50/60% centroid movement are bounded by photo-only gates. Blur, unknown diffuse mixture and the lack of an independently measured PSF prevent treating them as measurement precision. Targets unchanged.'))
    print(read(BASE/'evidence/selection.json'))
if __name__=='__main__':main()
