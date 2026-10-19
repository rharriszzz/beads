"""Pigment inference from common-geometry body samples with specular exclusion.

No motif, expected color, periodic index or spiral membership is an input.
Outputs include exact used/excluded pixels and abstention. Automatically proposed
color edits remain provisional; maker review alone is authoritative this round.
"""
import argparse,time
from pathlib import Path
from collections import Counter
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from .common import *

class BodyAudit:
    def __init__(self,graph,observations,coordinates):
        self.g=graph;self.obs=observations;self.co=coordinates;self.photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));self.rgb=self.photo.astype(float)/255.;self.names=sorted(observations);self.xy=np.array([observations[o]['xy'] for o in self.names]);self.tree=cKDTree(self.xy)
        self.value=self.rgb.max(2);self.blur=ndi.gaussian_filter(self.value,2.0);self.gradient=np.hypot(ndi.sobel(self.value,axis=0),ndi.sobel(self.value,axis=1))/8
    def sample(self,xy,radius=12,exclude_id=None):
        center=np.array(xy);x,y=np.rint(center).astype(int);r=radius;x0=max(0,x-r);y0=max(0,y-r);p=self.rgb[y0:y+r+1,x0:x+r+1];yy,xx=np.indices(p.shape[:2]);xx+=x0;yy+=y0;dx=xx-center[0];dy=yy-center[1];disk=dx*dx+dy*dy<=r*r;domain=disk.copy();neighbor_ids=[]
        for j in self.tree.query_ball_point(center,2*r+6):
            name=self.names[j];other=self.xy[j]
            if name==exclude_id or np.linalg.norm(other-center)<8:continue
            # Same conservative support-Voronoi rule for every pigment; aliases
            # closer than8px are logged elsewhere, never used to crop a body.
            od=(xx-other[0])**2+(yy-other[1])**2;domain&=dx*dx+dy*dy<.86*od;neighbor_ids.append(name)
        red,green,blue=p.transpose(2,0,1);v=p.max(2);chroma=v-p.min(2)
        # BLACK FIRST: common geometry and intensity ONLY. Neither pink-paper
        # chromaticity nor RGB/hue features can enter this mask or test.
        common=domain&(v>.012)
        if common.sum()<15:return dict(valid=False,reason='too little common-geometry support',body_pixels=[],highlight_pixels=[],paper_pixels=[],feature=None,xy=xy,radius=r,black_test=dict(decision='unknown',reason='insufficient common region'))
        q65,q82,q97=np.quantile(v[common],[.65,.82,.97]);contrast=v-self.blur[y0:y+r+1,x0:x+r+1]
        seeds=common&(((v>=q82)&(contrast>.018))|(v>=max(q97,q65+.035)))
        q20,q95=np.quantile(v[common],[.20,.95]);shoulder=q20+max(.08,.45*(q95-q20));support=common&(v>=shoulder);lobes,_=ndi.label(support);selected=set(lobes[seeds].tolist())-{0};spec=ndi.binary_dilation(np.isin(lobes,list(selected)),iterations=1)&common
        # Identify the measured reflection lobe nearest the recorded support;
        # its centroid is a reflection descriptor, NEVER a bead center.
        lab,num=ndi.label(spec);choices=[]
        for label in range(1,num+1):
            sy,sx=np.where(lab==label)
            if len(sx)>=3:choices.append((float(np.min((sx+x0-center[0])**2+(sy+y0-center[1])**2)),label))
        selected_lobe=lab==min(choices)[1] if choices else np.zeros_like(common)
        ring=ndi.binary_dilation(selected_lobe,iterations=4)&~ndi.binary_dilation(selected_lobe,iterations=1)&common&~spec
        intensity=.299*red+.587*green+.114*blue
        ry,rx=np.where(ring);ringpoints=np.c_[rx+x0,ry+y0];gray=intensity[ring]
        if len(gray):
            sy,sx=np.where(selected_lobe);reflection=np.array([sx.mean()+x0,sy.mean()+y0]);angles=np.arctan2(ringpoints[:,1]-reflection[1],ringpoints[:,0]-reflection[0]);coverage=len(set(((angles+np.pi)/(2*np.pi)*8).astype(int).clip(0,7).tolist()))
            blacktest=dict(ring_pixels=ringpoints.tolist(),reflection_pixels=np.c_[sx+x0,sy+y0].tolist(),ring_count=len(gray),sectors=coverage,median_intensity=float(np.median(gray)),q75_intensity=float(np.quantile(gray,.75)),dark_fraction=float(np.mean(gray<=.15)),raw_positive=bool(len(gray)>=25 and coverage>=4 and np.median(gray)<=.13 and np.quantile(gray,.75)<=.18 and np.mean(gray<=.15)>=.70),raw_negative=bool(len(gray)>=25 and coverage>=4 and (np.median(gray)>=.20 or np.mean(gray<=.15)<=.30)),geometry_valid=bool(len(gray)>=25 and coverage>=4),hue_used=False)
        else:blacktest=dict(ring_pixels=[],reflection_pixels=[],ring_count=0,sectors=0,geometry_valid=False,raw_positive=False,raw_negative=False,hue_used=False)
        # Only the later red/yellow calculation may use chromatic information.
        paper=(blue>red*.55)&(green>red*.20)&(blue>green*1.35)&(v>.10)
        domain=common&~paper
        uncertain_edge=self.gradient[y0:y+r+1,x0:x+r+1]>.18
        body=domain&~spec&~uncertain_edge
        labels,num=ndi.label(body);sizes=np.bincount(labels.ravel());small=sizes<5;small[0]=False;body&=~small[labels]
        points=np.c_[xx[body],yy[body]];px=p[body]
        if len(px)<12:return dict(black_test=blacktest,valid=False,reason='too little body after highlight exclusion',body_pixels=points.tolist(),highlight_pixels=np.c_[xx[spec],yy[spec]].tolist(),paper_pixels=np.c_[xx[disk&paper],yy[disk&paper]].tolist(),feature=None,xy=xy,radius=r)
        value=px.max(1);chrom=value-px.min(1);saturation=chrom/np.maximum(value,.01);angle=np.arctan2(points[:,1]-center[1],points[:,0]-center[0]);sectors=set(((angle+np.pi)/(2*np.pi)*8).astype(int).clip(0,7).tolist())
        quant=np.quantile(px,[.2,.4,.6,.8],axis=0).ravel();ratios=px/(px.sum(1)[:,None]+.03);rq=np.quantile(ratios,[.25,.5,.75],axis=0).ravel();feature=np.r_[quant,rq,np.quantile(value,[.2,.5,.8]),np.quantile(saturation,[.2,.5,.8])]
        # Keep raw pixel statistics. Illumination normalization is added later
        # using adjacent strongly colored bodies, independently of motif colors.
        return dict(black_test=blacktest,median_intensity=float(np.median(.299*px[:,0]+.587*px[:,1]+.114*px[:,2])),valid=bool(len(px)>=35 and len(sectors)>=3),reason=None if len(px)>=35 and len(sectors)>=3 else 'insufficient body count/angular support',body_pixels=points.tolist(),highlight_pixels=np.c_[xx[spec],yy[spec]].tolist(),paper_pixels=np.c_[xx[disk&paper],yy[disk&paper]].tolist(),boundary_excluded_pixels=np.c_[xx[domain&uncertain_edge],yy[domain&uncertain_edge]].tolist(),domain_pixels=np.c_[xx[domain],yy[domain]].tolist(),feature=feature.tolist(),xy=xy,radius=r,body_count=len(px),highlight_count=int(spec.sum()),sectors=len(sectors),median_value=float(np.median(value)),q80_value=float(np.quantile(value,.8)),median_chroma=float(np.median(chrom)),median_RGB=np.median(px,axis=0).tolist(),red_material_fraction=float(((px[:,0]>1.8*px[:,1])&(px[:,0]>2.5*px[:,2])&(px[:,0]>.16)).mean()),yellow_material_fraction=float(((px[:,1]>.35*px[:,0])&(px[:,1]>1.8*px[:,2])&(px[:,0]>.9*px[:,1])&(px[:,0]>.16)).mean()),neighbor_guards=neighbor_ids)

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=reviewed_dataset('relocated');ledger=read(artifact('corrections/ledger.json'));authoritative={r['id'] for r in ledger['ordinary_color_corrections']}|{ledger['location_correction']['id']};inventory=set(obs);targets=dict(obs);status={o:'recorded' for o in obs}
    for key,kind in [('provisional_observations','provisional'),('unrepresented_candidates','unassociated-native')]:
        for r in g[key]:
            if r['id'] in targets:continue
            targets[r['id']]=dict(id=r['id'],xy=r['xy'],color=r['color']);status[r['id']]=kind
    names=sorted(targets);audit=BodyAudit(g,obs,co);records={};sampletime=time.perf_counter()
    # All colors use identical radii, exclusion rules and feature construction.
    for o in names:records[o]=[audit.sample(targets[o]['xy'],radius,o) for radius in [9,12,15]]
    sampling_seconds=time.perf_counter()-sampletime
    ix={o:i for i,o in enumerate(ids)};tree=cKDTree([obs[o]['xy'] for o in ids]);blocks={}
    for o in names:blocks[o]=int(b[ix[o]]) if o in ix else int(b[tree.query(targets[o]['xy'])[1]])
    # Nearby confidently chromatic material supplies local lighting/shadow scale.
    # We do not use a black candidate's specular hue as a white-balance estimate.
    anchors=[]
    for o in ids:
        r=records[o][1]
        if r.get('valid') and obs[o]['color'] in ['red','yellow'] and r.get('median_intensity',0)>.18:anchors.append(o)
    atree=cKDTree([obs[o]['xy'] for o in anchors]);lighting={}
    for o in names:
        dd,jj=atree.query(targets[o]['xy'],k=min(10,len(anchors)));use=[anchors[int(j)] for d,j in zip(np.atleast_1d(dd),np.atleast_1d(jj)) if d<220 and anchors[int(j)]!=o]
        if not use:use=[anchors[int(np.atleast_1d(jj)[0])]]
        vals=[records[q][1]['median_value'] for q in use];lighting[o]=dict(value=float(np.median(vals)),ids=use,RGB=np.median([records[q][1]['median_RGB'] for q in use],axis=0).tolist(),intensity=float(np.median([records[q][1]['median_intensity'] for q in use])))
    # Cross-fit pigment votes on OTHER geographic sections. Legacy labels are
    # weak training evidence except explicit maker review. Features have no index.
    values=np.zeros((len(names),3,3,3));counts=np.zeros((len(names),3),int);mean_features=[]
    for ri,radius in enumerate([9,12,15]):
        features=[];valid=[]
        for o in names:
            r=records[o][ri];raw=np.array(r['feature'] if r.get('feature') is not None else [0.]*27);light=lighting[o]['value'];feat=np.r_[raw,raw[:12]/max(light,.10),r.get('median_value',0)/max(light,.1),r.get('red_material_fraction',0),r.get('yellow_material_fraction',0)];features.append(feat);valid.append(r['valid']);counts[names.index(o),ri]=len(r['body_pixels'])
        features=np.array(features);valid=np.array(valid);mean_features.append(features)
        for block in range(12):
            train=np.array([j for j,o in enumerate(names) if o in inventory and blocks[o]!=block and valid[j] and obs[o]['color']!='black']);test=np.array([j for j,o in enumerate(names) if blocks[o]==block]);scale=np.maximum(np.percentile(features[train],75,axis=0)-np.percentile(features[train],25,axis=0),.04);knn=cKDTree(features[train]/scale);_,nn=knn.query(features[test]/scale,k=51);label=np.array([COLORS.index(obs[names[j]]['color']) for j in train]);near=label[nn]
            for ki,k in enumerate([15,31,51]):values[test,ri,ki]=np.stack([(near[:,:k]==col).mean(1) for col in range(3)],axis=1)
    historical=read(ROOT/'photo2/r330/refinement/refinement.json.gz')['color_candidates'];spatial={r['id']:r for r in read(ROOT/'photo2/r333/diagnosis/diagnosis.json.gz')['all_predictions']};rows=[]
    for j,o in enumerate(names):
        votes=values[j].reshape(9,3);normal_winner=int(votes.mean(0).argmax());valid=sum(r['valid'] for r in records[o]);r=records[o][1];light=lighting[o]['value'];lightgray=lighting[o]['intensity'];tests=[]
        for sample in records[o]:
            test=dict(sample.get('black_test',{}));ratio=test.get('median_intensity',1)/max(lightgray,.1);test['relative_to_adjacent_colored_body']=ratio
            test['positive']=bool(test.get('raw_positive') and ratio<=.65)
            test['negative']=bool(test.get('raw_negative'))
            tests.append(test)
        positives=sum(test['positive'] for test in tests);negatives=sum(test['negative'] for test in tests);gate='black' if positives>=2 and negatives==0 else 'not-black' if negatives>=2 and positives==0 else 'unknown'
        normal_stable=bool(np.all(votes.argmax(1)==normal_winner));normal_mean=float(votes[:,normal_winner].mean());normal_minimum=float(votes[:,normal_winner].min())
        if gate=='black':
            winner=2;mean=float(np.mean([t.get('dark_fraction',0) for t in tests]));minimum=float(min(t.get('dark_fraction',0) for t in tests));stable=True;abstain=False;prediction='black'
        elif gate=='not-black':
            winner=normal_winner;mean=normal_mean;minimum=normal_minimum;stable=normal_stable;abstain=not(valid==3 and stable and minimum>=.60 and mean>=.78);prediction='?' if abstain else COLORS[winner]
        else:
            winner=2 if positives else normal_winner;mean=normal_mean;minimum=normal_minimum;stable=normal_stable;abstain=True;prediction='?'
        red_guard=False;expected=spatial.get(o,{}).get('prediction','?');original=targets[o]['color']
        row=dict(id=o,status=status[o],xy=targets[o]['xy'],original_raw_color=next((r['original_color'] for r in ledger['ordinary_color_corrections'] if r['id']==o),ledger['location_correction']['original_color'] if o==ledger['location_correction']['id'] else original),overlay_color=original,maker_reviewed=o in authoritative,body_prediction=prediction,plurality=COLORS[winner],abstain=abstain,abstention_reasons=(["intensity-only black test is ambiguous or lacks surrounding material"] if gate=='unknown' else ["red/yellow body calculation lacks stable support"] if abstain else []),black_test=dict(decision=gate,scales=tests,hue_used=False),red_yellow_calculation_used=gate=='not-black',votes=votes.tolist(),mean_votes=([0.,0.,mean] if gate=='black' else votes.mean(0).tolist()),minimum_vote=minimum,stable=stable,valid_scales=valid,body_counts=counts[j].tolist(),samples=records[o],lighting=lighting[o],red_guard=red_guard,shadow_normalized_body_value=r.get('median_value',0)/max(light,.1),historical_R330_hypothesis=historical.get(o),R333_spatial_expectation=expected,pattern_agrees=expected==prediction and prediction!='?',strong_provisional=bool(o not in authoritative and original!=prediction and prediction!='?'),rank_score=float(mean+minimum+.15*(expected==COLORS[winner])+.10*(o in historical)),policy='Black is tested first using grayscale annulus intensity only. Red/yellow body features run only after a not-black decision. Pattern/historical expectation enters rank after classification; auto suggestions never become authoritative.')
        rows.append(row)
    candidates=sorted([r for r in rows if not r['maker_reviewed'] and r['overlay_color']!=r['plurality'] and r['plurality']=='black'],key=lambda r:(not r['strong_provisional'],-r['rank_score']))
    # Separate transparent retrospective controls. Geographic exclusions prevent
    # training on target-section labels; thresholds still designed after maker
    # examples were exposed, so this is not independent photographic accuracy.
    makercontrols=[dict(id=r['id'],body_prediction=r['body_prediction'],plurality=r['plurality'],abstain=r['abstain'],votes=r['mean_votes']) for r in rows if r['maker_reviewed']]
    established=read(ROOT/'photo2/r328/results/established-subset.json');refids={o for e in established['links']+established['peripheral_links'] for o in [e['source'],e['target']]};refrows=[dict(id=r['id'],label=r['overlay_color'],prediction=r['body_prediction'],abstain=r['abstain'],section=blocks[r['id']]) for r in rows if r['id'] in refids]
    result=dict(records=rows,ranked_color_candidates=candidates,maker_controls=makercontrols,historical_reference_controls=refrows,counts=dict(total=len(rows),recorded=len(obs),provisional=sum(status[o]=='provisional' for o in names),provisional_black=sum(status[o]=='provisional' and targets[o]['color']=='black' for o in names),unassociated_native=sum(status[o]=='unassociated-native' for o in names),abstentions=sum(r['abstain'] for r in rows),strong_provisional_color_changes=sum(r['strong_provisional'] for r in rows),ranked_red_to_black=sum(r['overlay_color']=='red' for r in candidates),strong_provisional_red_to_black=sum(r['overlay_color']=='red' and r['strong_provisional'] for r in candidates),maker_corrections=8),sampling_seconds=sampling_seconds,seconds=time.perf_counter()-t,thresholds=dict(radii=[9,12,15],minimum_body_pixels=35,minimum_sectors=3,minimum_vote=.60,mean_vote=.78,all_nine_votes_same=True,black_first=dict(median_intensity=.13,q75_intensity=.18,dark_fraction_cutoff=.15,minimum_dark_fraction=.70,minimum_pixels=25,minimum_sectors=4,maximum_lighting_ratio=.65,minimum_positive_scales=2,negative_scales_allowed=0,hue_used=False)),policy='All automatically suggested changes remain provisional. Historical/control labels are already exposed; geographic cross-fit is computational prediction, not new independent accuracy. No motif colors enter pigment inference.')
    save(out/'audit.json.gz',result);save(out/'summary.json',dict(counts=result['counts'],maker_controls=makercontrols,reference_controls=refrows,seconds=result['seconds']));print('CLASSIFICATION',result['counts'],'maker',makercontrols,'seconds',result['seconds'],flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
