"""Maker decisions, role exclusions, and native rechecks of five blocked links."""
import argparse,copy,time
from collections import Counter
import numpy as np
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from .common import *
DECISIONS=[
 ('K-1508-3038',2,'E5-1499-3037','phantom / not a separate bead',None,True),
 ('K-2225-1294',2,'E7-2235-1306','excluded because reflection evidence is too weak',None,True),
 ('NEW-946-2684',2,'E5-0948-2669','excluded because evidence is too weak',None,True),
 ('NEW-985-2766',2,'E5-0986-2754','excluded because evidence is too weak / no room for a second body',None,True),
 ('R332-B-0196-0183',1,'R332-B-0196-0183','rejected visible-body candidate; sampled neighbor/shadow response',None,True),
 ('R332-B-0138-0130',1,'R332-B-0138-0130','rejected visible-body candidate; no independently distinguishable glass',None,True),
 ('R332-B-0098-0092',1,'R332-B-0098-0092','maker-confirmed bead association; deferred reflection-free body','black',True),
 ('C-1979-2669',1,'C-1979-2669','accepted bead association; excluded edge observation','yellow',True),
 ('REC266-P146299',1,'REC266-P146299','maker-corrected yellow; excluded edge observation','yellow',True),
 ('NEW-1927-2829',1,'NEW-1927-2829','maker-corrected red; excluded edge observation','red',True)]
EXCLUDED={r[2] for r in DECISIONS}

def lighting_record(photo,obs):
    o='E5-1499-3037';x,y=np.rint(obs[o]['xy']).astype(int);box=[x-8,y-8,x+9,y+9]
    return dict(id=o,xy=obs[o]['xy'],role='lighting observation only; not a separate bead',bbox=box,native_RGB=photo[box[1]:box[3],box[0]:box[2]],bead_identity=False,bead_center=None)

def foreground(photo):
    rgb=photo.astype(float)/255.;r,g,b=rgb.transpose(2,0,1);raw=((r>1.5*b)&(r>.13))|(rgb.max(2)<.30);fg=ndi.binary_closing(raw,iterations=5)
    lab,_=ndi.label(~fg);sizes=np.bincount(lab.ravel());small=sizes<600;small[0]=False;fg|=small[lab];lab,_=ndi.label(fg);sizes=np.bincount(lab.ravel());sizes[0]=0
    return (lab==sizes.argmax()).astype(float),raw.astype(float)

def corridor(a,z,obs,fg,exclude=()):
    p=np.array(obs[a]['xy']);q=np.array(obs[z]['xy']);v=q-p;length2=float(v@v);blocks=[]
    for o,r in obs.items():
        if o in [a,z] or o in exclude:continue
        delta=np.array(r['xy'])-p;t=float(delta@v/length2)
        if .2<t<.8 and np.linalg.norm(delta-t*v)<7:blocks.append(o)
    pts=np.linspace(p,q,31);fraction=float(ndi.map_coordinates(fg,[pts[:,1],pts[:,0]],order=1,mode='nearest').mean())
    return dict(allowed=not blocks and fraction>.95,foreground_fraction=fraction,intervening_observations=sorted(blocks),sample_xy=pts)

def run(out):
    t=time.perf_counter();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    # The causal investigation must exist before applying any maker changes.
    evidence=read(artifact('evidence/investigation.json.gz'));assert len(evidence['cases'])==2
    old=read(ROOT/'photo2/r335/results/graph.json.gz');g=copy.deepcopy(old);raw=read(ROOT/'photo2/r332/results/graph.json.gz');obs={r['id']:r for r in g['observations']};co={r['id']:r['ab'] for r in g['coordinates']};proposals={r['id']:r for r in raw['provisional_observations']};panels=read(ROOT/'photo2/r335/review/panels.json.gz');cases=read(ROOT/'photo2/r335/review/ledger.json.gz')['primary'];ledger=[]
    for photo,number,oid,status,color,inactive in DECISIONS:
        case=next(c for c in cases if c['id']==photo);panel=panels[case['panel']];key=next(k for k in panel['key'] if k['number']==number);assert key['id']==oid
        row=dict(photograph=photo,panel='target',local_feature=number,id=oid,original_xy=key['xy'],original_color=key['color'],original_ab=key['ab'],status=status,maker_color=color,exclude_active=inactive,
                 authority='R336 maker photographic review',roles=dict(counting=False,indexing=False,link_obstruction=False,geometry_fitting=False,pattern_extraction=False))
        if oid in proposals and oid in ['R332-B-0098-0092','C-1979-2669']:
            row.update(accepted_association=dict(measured_support=proposals[oid]['xy'],predicted_site=proposals[oid]['prediction'],ab=proposals[oid]['cell'],same_bead=True),association_identity_count=1)
            if oid=='R332-B-0098-0092':row['not_alias_of']='D40-K-1036-2780';row['cache_aliases']=proposals[oid].get('alternatives',[])
        if oid=='E5-1499-3037':row['retained_evidence_role']='lighting observation only; does not establish another bead'
        if oid in obs:
            obs[oid]['r336_status']=status
            if color:obs[oid]['color']=color
        ledger.append(row)
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));save(out/'lighting-observations.json',lighting_record(photo,obs));fg,rawmask=foreground(photo);links=[]
    for edge in raw['coordinate_only_edges']:
        a,z=edge['source'],edge['target'];before=corridor(a,z,obs,fg);after=corridor(a,z,obs,fg,EXCLUDED);rawcheck=corridor(a,z,obs,rawmask,EXCLUDED)
        residual=np.array(co[z])-co[a]-edge['delta_ab'];assert rep(residual)==(0,0)
        nearby=[e for e in old['edges'] if (a in [e['source'],e['target']] or z in [e['source'],e['target']])]
        lengths=[float(np.linalg.norm(np.array(obs[e['source']]['xy'])-obs[e['target']]['xy'])) for e in nearby if e['family']==edge['family']]
        length=float(np.linalg.norm(np.array(obs[z]['xy'])-obs[a]['xy']));ratio=length/np.median(lengths)
        # Same-color-independent common local spacing check. Supports are not
        # centers: use a broad plausibility interval, not a sphere-packing proof.
        geometry_ok=.65<=ratio<=1.45
        row=dict(edge=edge,before=before,after=after,raw_mask_foreground=rawcheck['foreground_fraction'],length=length,local_family_median=float(np.median(lengths)),length_ratio=ratio,geometry_plausible=bool(geometry_ok),accepted=bool(after['allowed'] and geometry_ok),equation_residual=residual)
        if row['accepted']:g['edges'].append(dict(source=a,target=z,delta_ab=edge['delta_ab'],family=edge['family'],origin='R336',status='accepted working repair',foreground_fraction=after['foreground_fraction'],intervening_observations=[],admission='maker blocker exclusion + remaining native corridor + common local spacing + exact modulo-H equation'))
        links.append(row)
    # Distinct active roles; unindexed supports are not separate confirmed bead
    # blockers merely because a recorded point exists.
    degree=Counter(o for e in old['edges'] for o in [e['source'],e['target']]);fixed_core={o for o in co if degree[o]>=4 and o not in EXCLUDED};records=[]
    for o,r in obs.items():
        inactive=o in EXCLUDED
        roles=dict(counting=not inactive and o in co,indexing=not inactive and o in co,geometry_fitting=not inactive and o in co,link_obstruction=not inactive and (o in co or o=='C-2058-0820'),pattern_extraction=not inactive and o in fixed_core)
        r['r336_roles']=roles;r['r336_status']=r.get('r336_status','working indexed observation' if o in co else 'provisional unresolved unindexed observation');records.append(r)
    archive=dict(g,observations=records,schema='r336-retained-evidence-with-roles-v1',baseline_commit=BASE,decisions='photo2/r336/results/maker-decisions.json')
    save(out/'retained-graph.json.gz',archive)
    active=dict(archive,observations=[r for r in records if r['id'] not in EXCLUDED],coordinates=[r for r in g['coordinates'] if r['id'] not in EXCLUDED],edges=[e for e in g['edges'] if e['source'] not in EXCLUDED and e['target'] not in EXCLUDED],schema='r336-active-working-graph-v1')
    active['indexed_colors']=dict(Counter(obs[r['id']]['color'] for r in active['coordinates']));save(out/'graph.json.gz',active)
    # Native brightness comparisons retain surface-response locations as such.
    brightness=[]
    for oid,refs in [('E7-2235-1306',['K-2225-1294','K-2244-1307']),('E5-0948-2669',['NEW-946-2684','K-0951-2652']),('E5-0986-2754',['NEW-985-2766','MAT25-K-0980-2735'])]:
        values=[]
        for o in [oid]+refs:
            x,y=np.rint(obs[o]['xy']).astype(int);p=photo[y-5:y+6,x-5:x+6].astype(float)/255.;yy,xx=np.indices(p.shape[:2]);v=(p@np.array([.299,.587,.114]))[(xx-5)**2+(yy-5)**2<=25]
            values.append(dict(id=o,xy=obs[o]['xy'],peak_luminance=float(v.max()),q90_luminance=float(np.quantile(v,.9))))
        brightness.append(dict(excluded=oid,comparisons=values,interpretation='Matched local 5px intensity apertures; reflections are not bead centers or proof of separate identity.'))
    save(out/'maker-decisions.json',dict(decisions=ledger,uniform_geometry='All bead outside sizes/shapes shared regardless of pigment; local support spacings and actual body alignment constrain identity. No highlight becomes a bead center.',all_original_pixels_preserved=True))
    save(out/'link-audit.json',dict(links=links,brightness=brightness,policy='No automatic link from exclusion alone. Five old proposals rechecked in native pixels and unchanged lattice.'))
    summary=dict(recorded_retained=len(records),recorded_active=len(active['observations']),indexed_retained=len(co),indexed_active=len(active['coordinates']),links_retained=len(g['edges']),links_active=len(active['edges']),added_links=sum(r['accepted'] for r in links),deactivated_historical_links=len(g['edges'])-len(active['edges']),explicit_decisions=10,recorded_exclusions=sum(o in obs for o in EXCLUDED),confirmed_deferred_associations=2,fixed_interior_pattern_cohort=len(fixed_core),colors=active['indexed_colors'],seconds=time.perf_counter()-t)
    save(out/'summary.json',summary);print(summary)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(p.parse_args().output)
