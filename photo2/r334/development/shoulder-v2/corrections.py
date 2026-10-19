"""Resolve exact historical local keys; keep maker authority distinct from models."""
import argparse,time
from pathlib import Path
from PIL import Image,ImageOps
from scipy import ndimage as ndi
from .common import *

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);t=time.perf_counter();g,obs,co,ids,*_=raw_dataset();cases=read(ROOT/'photo2/r333/review/cases.json');rows=[]
    requests=[('E5-1616-2970',None),('NEW-1706-342',None),('NEW-2207-1350',None),('MAT25-K-2237-2196',25),('K-1904-2820',36),('K-1904-2820',7),('K-1904-2820',33)]
    for named,number in requests:
        matches=[]
        for case in cases:
            for kind,panel in [('target',case)]+[('comparison',p) for p in case['examples']]:
                if panel['id']!=named:continue
                key=[r for r in panel['key'] if (r['number']==number if number is not None else r['id']==named)]
                assert len(key)==1
                k=key[0];assert k['color']=='red';matches.append(dict(case=case['name'],parent_target=case['id'],panel_type=kind,photograph_identifier=named,local_number=k['number'],asset=panel.get('asset',case['name']),stable_id=k['id'],original_xy=k['xy'],original_ab=k['ab'],original_color=k['color']))
        assert matches and len({r['stable_id'] for r in matches})==1,(named,number,matches)
        k=matches[0];oid=k['stable_id'];assert k['original_xy']==obs[oid]['xy'];rows.append(dict(id=oid,mechanism='maker-confirmed ordinary color misclassification',original_color='red',corrected_color='black',original_xy=obs[oid]['xy'],corrected_xy=obs[oid]['xy'],original_ab=co[oid],corrected_ab=co[oid],references=matches,authority='R334 maker photographic review; independent of periodicity model',duplicate_mentions=2 if named=='MAT25-K-2237-2196' else 1))
    assert len(rows)==len({r['id'] for r in rows})==7
    # Native two-body inspection: yellow material above/left of the black body.
    # The box is a bounded inspection context selected from maker's named target,
    # not a detector. Find the connected dark-material component on the reviewed
    # lower body, exclude its reflection, and choose an ACTUAL material pixel.
    photo=np.asarray(ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB'));rgb=photo/255.;box=[2063,833,2083,858];x0,y0,x1,y1=box;p=rgb[y0:y1,x0:x1];v=p.max(2);chroma=v-p.min(2);dark=(v<.40)&(chroma<.30)&(v>.015);lab,_=ndi.label(dark);sizes=np.bincount(lab.ravel());sizes[0]=0;assert sizes.max()>=30;mask=lab==sizes.argmax();yy,xx=np.where(mask);pp=np.c_[xx+x0,yy+y0];assert len(pp)>=30
    # Representative is a robust interior material pixel near the component's
    # spatial median, never a predicted center or the colored highlight itself.
    med=np.median(pp,axis=0);dist=ndi.distance_transform_edt(mask);interior=np.array([dist[y-y0,x-x0] for x,y in pp]);choice=np.argmin(np.sum((pp-med)**2,axis=1)-2*interior);xy=pp[choice].astype(float).tolist();target='R332-R-0025-0023';oldxy=obs[target]['xy'];delta=np.array(xy)-oldxy
    nearest=sorted([dict(id=o,xy=r['xy'],color=r['color'],ab=co.get(o),distance=float(np.linalg.norm(np.array(r['xy'])-xy))) for o,r in obs.items() if o!=target],key=lambda r:r['distance'])[:8]
    yellow='C-2058-0820';assert yellow in obs and yellow not in co and obs[yellow]['color']=='yellow'
    incident=[e for e in g['edges'] if target in [e['source'],e['target']]]
    # Native corridor checks are repeated before an authoritative moved support
    # is delivered. Integer coordinates are not shifted to improve motif colors.
    corridors=[]
    allxy=np.array([obs[o]['xy'] for o in obs]);allnames=list(obs)
    for e in incident:
        other=e['target'] if e['source']==target else e['source'];q=np.array(obs[other]['xy']);start=np.array(xy);vec=q-start;length2=vec@vec;interveners=[]
        for oid,pos in zip(allnames,allxy):
            if oid in [target,other]:continue
            tt=(pos-start)@vec/length2
            if .2<tt<.8 and np.linalg.norm(pos-start-tt*vec)<7:interveners.append(oid)
        pts=np.rint(np.linspace(start,q,31)).astype(int);vv=rgb[pts[:,1],pts[:,0]];rr,gg,bb=vv.T;foreground=((rr>1.5*bb)&(rr>.13))|(vv.max(1)<.30)
        corridors.append(dict(other=other,source=e['source'],target=e['target'],delta_ab=e['delta_ab'],length_px=float(np.sqrt(length2)),intervening_observations=interveners,native_foreground_fraction=float(foreground.mean()),integer_equation_unchanged=True))
    assert not any(r['intervening_observations'] for r in corridors)
    location=dict(id=target,mechanism='maker-confirmed wrong visible body / observation location',original_color=obs[target]['color'],corrected_color='black',original_xy=oldxy,corrected_xy=xy,displacement_px=float(np.linalg.norm(delta)),original_ab=co[target],corrected_ab=co[target],lattice_site_changed=False,measured_material_pixels=pp.tolist(),inspection_box=box,location_kind='actual native dark-material representative, not physical bead center',references=[dict(case='case-05',panel_type='target',photograph_identifier=target,local_number=27,asset='case-05')],yellow_body=dict(id=yellow,xy=obs[yellow]['xy'],color='yellow',indexed=False,preserved=True,original_misplaced_support_alias_of=yellow,reason='distinct adjacent visible yellow body remains a recorded unindexed observation; no motif-driven site assignment'),nearest_existing_observations=nearest,incident_links=corridors,links_removed=[],links_added=[],coordinate_changes_in_ab=0,native_candidate_alias='REC266-P040667',candidate_alias_reason='cached colored reflection at (2067.2,843.9) lies on reviewed black body; not another bead',authority='Maker identifies adjacent yellow/black bodies; native pixel extraction supports new material representative')
    ledger=dict(baseline_commit=BASE,ordinary_color_corrections=rows,location_correction=location,unique_ordinary_color_corrections=7,unique_location_corrections=1,unresolved_number_mappings=[],all_R333_raw_records_preserved=True,seconds=time.perf_counter()-t,policy='Authoritative review overlay only; historical labels/coordinates remain immutable. C-1284-0332 and other unmentioned hypotheses remain provisional.')
    save(out/'ledger.json',ledger);print('CORRECTIONS',[r['id'] for r in rows],'location',oldxy,'->',xy,'pixels',len(pp),flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
