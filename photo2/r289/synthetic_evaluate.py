"""Known-body evaluation, with multiplicity and missing observations retained."""
from collections import Counter
from .common import *

def main():
    scenes=[read(p) for p in sorted((OUT/'synthetic').glob('*/evaluation.json'))];assert len(scenes)==12
    rows=[];denominators=[];physics=[]
    for s in scenes:
        for b in s['beads']:
            meta=dict(scene=s['scene']['id'],split=s['scene']['split'],owner=b['owner'],color=b['color'],diameter=b['diameter'],visible_fraction=b['visible_fraction'],visible_area=b['visible_area'])
            if b['specular'] and b['normal_prediction']:
                physics.append(dict(**meta,centroid_error=float(np.linalg.norm(np.array(b['specular']['centroid'])-b['normal_prediction']['centroid'])),peak_error=float(np.linalg.norm(np.array(b['specular']['peak'])-b['normal_prediction']['peak']))))
            for mode in ('on','off'):
                mm=b['measurements'][mode];pure=[m for m in mm if m['purity']>=.95]
                denominators.append(dict(**meta,mode=mode,observations=len(mm),pure=len(pure),eligible=b['visible_area']>=40,status='missing' if not mm else 'multiple' if len(mm)>1 else 'contaminated' if not pure else 'unique'))
                if len(mm)!=1 or not pure or b['visible_area']<40:continue
                m=mm[0];rows.append(dict(**meta,mode=mode,measurement=m,visible=b['visible_centroid'],physical=b['physical_center'],specular=b['specular'],normal_prediction=b['normal_prediction']))
    models={};scores={};residuals=[]
    for mode in ('on','off'):
        for col in ('red','yellow','black'):
            for target in ('visible','physical'):
                tr=[r for r in rows if r['mode']==mode and r['color']==col and r['split']=='development']
                te=[r for r in rows if r['mode']==mode and r['color']==col and r['split']=='evaluation']
                for method in ('point','patch','weighted'):
                    if not tr:continue
                    shift=np.mean([np.array(r[target])-r['measurement'][method] for r in tr],axis=0)
                    key=f'{mode}/{col}/{target}/{method}';models[key]=dict(train=len(tr),shift=shift.tolist())
                    for calibrated in (False,True):
                        errors=[]
                        for r in te:
                            p=np.array(r['measurement'][method])+(shift if calibrated else 0);err=float(np.linalg.norm(p-r[target]));errors.append(err)
                            residuals.append(dict(scene=r['scene'],owner=r['owner'],color=col,mode=mode,target=target,method=('constant_' if calibrated else 'raw_')+method,prediction=p.tolist(),truth=r[target],error=err,visible_fraction=r['visible_fraction']))
                        scores[key+('/constant' if calibrated else '/raw')]=stats(errors,te[0]['diameter'] if te else 1)
                # Known geometry/light and correct identity: translate observed patch
                # by model's specular-to-target displacement, with no empirical fit.
                rr=[r for r in te if r['normal_prediction']]
                for method in ('point','patch'):
                    errors=[]
                    for r in rr:
                        f='peak' if method=='point' else 'centroid';p=np.array(r['measurement'][method])+r[target]-np.array(r['normal_prediction'][f]);err=float(np.linalg.norm(p-r[target]));errors.append(err)
                        residuals.append(dict(scene=r['scene'],owner=r['owner'],color=col,mode=mode,target=target,method='known_specular_'+method,prediction=p.tolist(),truth=r[target],error=err,visible_fraction=r['visible_fraction'],specular_fraction_at_peak=r['measurement']['specular_fraction_at_peak']))
                    scores[f'{mode}/{col}/{target}/known_specular_{method}']=stats(errors,rr[0]['diameter'] if rr else 1)
    counts={}
    for mode in ('on','off'):
        for split in ('development','evaluation'):
            for col in ('red','yellow','black'):
                rr=[r for r in denominators if r['mode']==mode and r['split']==split and r['color']==col and r['eligible']]
                counts[f'{mode}/{split}/{col}']=dict(eligible=len(rr),status=dict(Counter(r['status'] for r in rr)),observations=sum(r['observations'] for r in rr),duplicate_extras=sum(max(0,r['observations']-1) for r in rr))
    phys={}
    for split in ('development','evaluation'):
        for col in ('red','yellow','black'):
            rr=[r for r in physics if r['split']==split and r['color']==col]
            phys[f'{split}/{col}']=dict(centroid=stats([r['centroid_error'] for r in rr],rr[0]['diameter'] if rr else 1),peak=stats([r['peak_error'] for r in rr],rr[0]['diameter'] if rr else 1))
    # Empirical and known-geometry comparison on exactly the SAME eligible cases.
    paired={}
    for col in ('red','yellow','black'):
        for target in ('physical','visible'):
            rr=[r for r in rows if r['mode']=='on' and r['split']=='evaluation' and r['color']==col and r['normal_prediction']]
            shift=models.get(f'on/{col}/{target}/patch',{}).get('shift')
            for subset in ('all','specular_dominant','diffuse_dominant','heavily_occluded','mostly_visible'):
                qq=[r for r in rr if subset=='all' or subset=='specular_dominant' and r['measurement']['specular_fraction_at_peak']>=.5 or subset=='diffuse_dominant' and r['measurement']['specular_fraction_at_peak']<.5 or subset=='heavily_occluded' and r['visible_fraction']<.6 or subset=='mostly_visible' and r['visible_fraction']>=.6]
                if shift is None:continue
                paired[f'{col}/{target}/{subset}']=dict(empirical=stats([np.linalg.norm(np.array(r['measurement']['patch'])+shift-r[target]) for r in qq],qq[0]['diameter'] if qq else 1),known_geometry=stats([np.linalg.norm(np.array(r['measurement']['patch'])-r['normal_prediction']['centroid']) for r in qq],qq[0]['diameter'] if qq else 1))
    save(OUT/'synthetic-calibration.json',models);save(OUT/'synthetic-residuals.json.gz',residuals)
    save(OUT/'synthetic-summary.json',dict(scenes=12,scores=scores,coverage=counts,normal_vs_isolated_specular=phys,paired=paired,all_denominators=denominators,physical_vs_visible=stats([np.linalg.norm(np.array(b['physical_center'])-b['visible_centroid']) for s in scenes for b in s['beads'] if b['visible_area']>=40],2*1.7845369838*9),projection_checks=[s['projection_check'] for s in scenes],saturated_channels=sum(s['saturated_channels'] for s in scenes),limitations='Known-correct identity conditioning for localization; all duplicate/missing cases counted separately. Orthographic 29-bead scenes, illustrative materials, six development/six evaluation scenes; light changes across split. No photographic physical-center accuracy inferred.'))
    for k,v in scores.items():
        if k.startswith('on/') and '/physical/' in k and ('patch/constant' in k or 'known_specular_patch' in k):print(k,v)
if __name__=='__main__':main()
