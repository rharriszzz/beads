"""Photo-only dimensional observations. No fitted geometry enters extraction."""
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw
from photo2.r297.common import ROOT, read, save, sha, photo, pixels
from photo2.r293.geometry import Reference
from photo2.r282.phase1 import image_features
BASE=ROOT/'photo2/r298'
# Analyst digitization on native raw crops, before model fit. Crop coordinate origin
# is saved explicitly. These are uncertain visible contours, NOT verified masks.
POLYGONS=[
 [[45,43],[52,36],[61,38],[68,47],[68,59],[62,69],[53,71],[45,64]],
 [[42,51],[48,43],[59,39],[68,43],[72,51],[67,59],[56,65],[47,62]],
 [[41,53],[44,46],[54,41],[66,41],[72,47],[70,55],[60,64],[49,65]],
 [[40,45],[47,40],[58,41],[69,46],[73,54],[67,61],[56,64],[45,60]],
 [[42,44],[48,41],[57,46],[66,58],[66,66],[58,71],[48,67],[42,57]],
 [[44,49],[49,44],[57,44],[65,51],[68,61],[65,69],[56,72],[48,64]],
 [[44,44],[52,39],[62,41],[67,48],[66,59],[61,68],[51,70],[44,62]],
 [[43,51],[47,44],[57,40],[67,40],[72,46],[70,54],[62,61],[51,64]],
 [[45,43],[52,41],[59,46],[64,56],[68,66],[63,71],[54,70],[47,60]],
 [[45,42],[52,39],[61,42],[68,49],[71,57],[67,64],[57,66],[47,60]],
 [[44,44],[51,39],[59,40],[66,46],[68,55],[62,65],[53,69],[44,61]],
 [[45,44],[53,40],[60,43],[65,51],[68,61],[65,69],[57,72],[49,65]],
 [[44,44],[50,40],[59,43],[65,51],[65,60],[59,69],[51,73],[44,65]],
 [[24,59],[29,53],[39,53],[48,58],[53,66],[51,73],[42,78],[31,73]],
 [[42,40],[48,37],[56,40],[65,50],[69,60],[66,68],[57,68],[48,59]],
 [[45,44],[53,40],[61,44],[67,53],[68,63],[63,70],[54,69],[46,61]],
]
def main():
    if (BASE/'evidence/measurements.json').exists():raise SystemExit('Measurements already frozen')
    rgb,path,meta=photo();ref=Reference();regions=read(BASE/'evidence/inspection-regions.json');beads=[]
    for j,(row,poly) in enumerate(zip(regions,POLYGONS)):
        origin=np.rint(row['point']).astype(int)-55;xy=np.array(poly)+origin
        c=xy.mean(0);q=ref.project([c]);a=q['arc'][0];k=min(np.searchsorted(ref.arc,a),len(ref.delta)-1)
        t=ref.delta[k]/ref.lengths[k];n=np.array([-t[1],t[0]])
        extent=np.ptp(xy@np.array([t,n]).T,axis=0)
        beads.append(dict(id=f'B{j:02}',source_region=row['id'],point=c.tolist(),polygon=xy.tolist(),crop_origin=origin.tolist(),tangent=t.tolist(),normal=n.tolist(),extent_px=extent.tolist(),uncertainty_px=[3.,3.],arc=float(a),split='comparison' if j%4==3 else 'development',status='analyst visible-contour estimate; dark margins/occlusion uncertain; not a full-body certificate',provenance='native unmarked inspection-regions crops, contour digitized before fitting'))
    f=image_features(rgb);hue=f['hsv'][:,:,0]*360;dist=abs((hue-f['background_hue']+180)%360-180)
    # Frozen photographic profiles: no target model width or axis correction used.
    arcs=np.arange(0,ref.length,48.);out=[]
    offsets=np.arange(-95,96);lanes=np.arange(-12,13,3)
    for j,a in enumerate(arcs):
        c=np.array([np.interp(a,ref.arc,ref.points[:,d]) for d in range(2)])
        k=min(np.searchsorted(ref.arc,a),len(ref.delta)-1);t=ref.delta[k]/ref.lengths[k];n=np.array([-t[1],t[0]])
        xy=c+lanes[:,None,None]*t+offsets[None,:,None]*n;ij=np.rint(xy).astype(int);x,y=ij[:,:,0],ij[:,:,1]
        alternatives=[]
        for hd,lf in [(18,.025),(22,.035),(26,.045)]:
            paper=(dist[y,x]<hd)&(f['hsv'][y,x,1]>.18)&(f['lum'][y,x]>lf)
            body=~paper
            # Require a supported run; isolated image noise is retained in samples
            # but cannot move a profile boundary.
            body=ndi.binary_opening(body,structure=np.ones((1,3)))
            bounds=[]
            for r in body:
                ids=np.flatnonzero(r)
                ids=ids[(offsets[ids]>-85)&(offsets[ids]<85)]
                if len(ids):bounds.append([float(offsets[ids[0]]),float(offsets[ids[-1]])])
            alternatives.append(np.median(bounds,axis=0).tolist() if bounds else [-95.,95.])
        v=np.array(alternatives);bounds=v[1];unc=np.maximum(3.,np.ptp(v,axis=0)+2.)
        # Upper-luminance paper threshold can catch cast shadows; mark sensitivity.
        reliable=bool(max(unc)<=8 and bounds[0]>-80 and bounds[1]<80 and bounds[0]<-20 and bounds[1]>20)
        out.append(dict(id=f'E{j:03}',arc=float(a),point=c.tolist(),tangent=t.tolist(),normal=n.tolist(),bounds=bounds.tolist(),uncertainty_px=unc.tolist(),alternatives=alternatives,eligible=reliable,split='comparison' if j%4==3 else 'development',samples_xy=ij.reshape(-1,2).tolist(),samples_rgb=rgb[y,x].reshape(-1,3).tolist(),meaning='median of nine native cross-section material/paper transitions; conditional edge proxy, shadow and dark-body ambiguity',thresholds=[[18,.025],[22,.035],[26,.045]]))
    result=dict(photo_sha256=sha(path),photo_path=str(path.relative_to(ROOT)),beads=beads,envelope=out,method='Frozen R298 photo-only measurements; no physical center or identity labels',limits='All comparison geography retrospective. Uncertainty is annotation/threshold sensitivity, not confidence intervals. Bead contours may omit occluded body.')
    save(BASE/'evidence/measurements.json',result)
    print('beads',len(beads),'envelope',len(out),'eligible',sum(r['eligible'] for r in out),'median width',np.median([np.diff(r['bounds'])[0] for r in out if r['eligible']]))
    print('bead extents',np.round([r['extent_px'] for r in beads],1))
    for start in [0,16,32,48,64,80,96,112,128,144,160,176]:
        sheet=Image.new('RGB',(1000,4*215),'white');draw=ImageDraw.Draw(sheet)
        for z,r in enumerate(out[start:start+16]):
            c=np.rint(r['point']).astype(int);origin=c-100;crop=Image.fromarray(rgb[c[1]-100:c[1]+100,c[0]-100:c[0]+100]);d=ImageDraw.Draw(crop)
            for bound in r['bounds']:
                v=np.array(r['point'])+bound*np.array(r['normal'])-origin;t=np.array(r['tangent']);d.line([tuple(v-12*t),tuple(v+12*t)],fill='cyan',width=1)
            sheet.paste(crop,(z%4*250,z//4*215));draw.text((z%4*250,z//4*215+200),r['id']+' '+str(r['eligible'])+' '+str(r['bounds']),fill='black')
        sheet.save(BASE/f'evidence/envelope-inspection-{start:03}.png')
    sheet=Image.new('RGB',(1320,1440),'white');draw=ImageDraw.Draw(sheet)
    for j,r in enumerate(beads):
        o=np.array(r['crop_origin']);crop=Image.fromarray(rgb[o[1]:o[1]+110,o[0]:o[0]+110]);d=ImageDraw.Draw(crop);d.line([tuple(x-o) for x in np.array(r['polygon'])]+[tuple(np.array(r['polygon'][0])-o)],fill='cyan',width=1)
        sheet.paste(crop.resize((330,330)),(j%4*330,j//4*360));draw.text((j%4*330,j//4*360+332),r['id']+' axial/face '+str(np.round(r['extent_px'],1)),fill='black')
    sheet.save(BASE/'evidence/bead-inspection.png')
if __name__=='__main__':main()
