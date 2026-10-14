"""Truth is opened only here, after frozen inference artifacts exist.

Membership-only oracle is constructed by the renderer provider, never by solver.
"""
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from .run import read,save,sha

def membership(o,owner):
    pix=np.array(o['pixels'],int);v=owner[pix[:,1],pix[:,0]];v=v[v>=0]
    if not len(v):return -1,0.
    ids,n=np.unique(v,return_counts=True);j=n.argmax();return int(ids[j]),float(n[j]/len(pix))

def evaluate(out):
    allrows=[];geom=[];fourths=[];hashes=[];detection=[];by_method={m:Counter() for m in 'ABC'};localization=[]
    for folder in sorted(out.glob('scene-*')):
        scene=out/'synthetic-scenes'/folder.name
        # Require completed predictions and scores BEFORE opening truth.
        pairs=read(folder/'pairs.json.gz');cases=read(folder/'test1.json');obs=read(folder/'observations.json.gz');by={o['id']:o for o in obs}
        for pair in pairs:
            f=folder/pair['before_C'];score=read(folder/pair['after_C']);assert sha(f)==score['frozen_sha256'];hashes.append(dict(path=str(f.relative_to(out)),sha256=sha(f)))
        truth=read(scene/'truth.json');owner=np.load(scene/'truth-membership.npy');centroids={};areas={}
        for j in range(len(truth['indices'])):
            yy,xx=np.where(owner==j)
            if len(xx)>=50:centroids[j]=np.array([xx.mean(),yy.mean()]);areas[j]=len(xx)
        member={o['id']:membership(o,owner) for o in obs}
        counts=Counter(k for k,p in member.values() if p>=.5 and k in centroids)
        detection.append(dict(scene=folder.name,observations=len(obs),visible_truth_bodies=len(centroids),detected_distinct=len(counts),same_body_extra_observations=sum(max(0,n-1) for n in counts.values()),background_or_low_purity=sum(p<.5 for k,p in member.values()),small_visibility=sum(p>=.5 and k not in centroids for k,p in member.values())))
        for o in obs:
            k,purity=member[o['id']]
            if purity>=.5 and k in centroids:
                err=float(np.linalg.norm(np.array(o['centroid'])-centroids[k]));localization.append(dict(scene=folder.name,color=truth['classes'][k],error_px=err,uncertainty=o['uncertainty'],covered=err<=o['uncertainty'],visible_area=areas[k]))
        for case in cases:
            a=by[case['anchor']];ak,ap=member[a['id']]
            target=[]
            if ap>=.5 and ak in centroids:
                distances={j:np.linalg.norm(c-centroids[ak]) for j,c in centroids.items() if j!=ak};dmin=min(distances.values());target=[j for j,d in distances.items() if d<=dmin+2.]
            for method,m in case['methods'].items():
                bk,bp=member.get(m['top'],(-1,0));top=('invalid_anchor' if not target else 'false_candidate' if bp<.5 or bk not in centroids else 'same_body_duplicate' if bk==ak else 'correct' if bk in target else 'wrong_body')
                decision=top if m['answer'] else 'ambiguous';alt_members=[member[i][0] for i in m['alternatives'] if member[i][1]>=.5]
                row=dict(scene=folder.name,anchor=a['id'],method=method,top_status=top,decision=decision,truth_nearest_members=target,top_member=bk,anchor_member=ak,alternatives_contain_truth=bool(set(target)&set(alt_members)),alternative_count=len(m['alternatives']),color=truth['classes'][ak] if ak>=0 else -1,hand=truth['parameters']['hand'],pitch=truth['parameters']['pitch'],specular=truth['parameters']['specular'],same_color_scene=truth['scene'] in (4,5,8,9))
                allrows.append(row);by_method[method][decision]+=1;by_method[method]['top_'+top]+=1;by_method[method]['total']+=1
        for pair in pairs:
            ak,ap=membership(pair['A'],owner);bk,bp=membership(pair['B'],owner);frozen=read(folder/pair['before_C']);scores=read(folder/pair['after_C'])['scores'];actual=truth['indices'][bk]-truth['indices'][ak] if min(ak,bk)>=0 else None
            for h,s in zip(frozen['hypotheses'],scores):
                relation=bool(actual and abs(actual)==abs(h['delta']) and ap>=.5 and bp>=.5 and ak!=bk);target=None;error=None;correct=False;baseline=None;area=None
                if relation:
                    direction=int(actual/h['delta']);k=truth['indices'][ak]+direction*h['target'];j=k+14
                    if j in centroids:
                        target=j;cen=h['C_centroid'];error=float(np.linalg.norm(np.array(cen)-centroids[j])) if cen else None
                        match=member.get(s['match'],(-1,0));correct=bool(match[0]==j and match[1]>=.5)
                        baseline=min(float(np.linalg.norm(np.array(x)-centroids[j])) for x in frozen['photographic_baseline_C_regions']['centers'])
                        area=areas[j]
                geom.append(dict(scene=folder.name,mode=pair['mode'],A=pair['A']['id'],B=pair['B']['id'],hand=h['hand'],delta=h['delta'],rank=h['rank'],AB_loss=h['AB_loss'],AB_actual_delta=actual,AB_correct_family=relation,C_visible_truth=target is not None,C_error_px=error,C_match_correct=correct,C_conditional_match=s['match'] is not None,C_truth_member=target,physical_valid=h['physical_valid'],baseline_best_of_three_error_px=baseline,truth_visible_area=area,parameters=h['parameters']))
            for df in pair['before_D']:
                d=read(folder/df);sf=folder/df.replace('-before-D.json.gz','-after-D.json');sc=read(sf);assert sc['frozen_sha256']==sha(folder/df)
                hand=d['parameters']['hand'];parent=next((h for h,s in zip(frozen['hypotheses'],scores) if h['hand']==hand and s['match']),None)
                valid=bool(parent and actual and abs(actual)==abs(parent['delta']));error=None;correct=False;c_correct=False
                if valid:
                    direction=int(actual/parent['delta']);ck=truth['indices'][ak]+direction*parent['target']+14
                    cm=member.get(d['fit_uses'][2],(-1,0));c_correct=cm[0]==ck and cm[1]>=.5
                    dk=truth['indices'][ak]+direction*d['D_target']+14
                    if dk in centroids and d['D_centroid'] is not None:
                        error=float(np.linalg.norm(np.array(d['D_centroid'])-centroids[dk]));dm=member.get(sc['score']['match'],(-1,0));correct=dm[0]==dk and dm[1]>=.5
                fourths.append(dict(scene=folder.name,mode=pair['mode'],physical_valid=d['physical_valid'],ABC_RMS_px=d['ABC_RMS_px'],C_identity_correct=c_correct,D_error_px=error,D_identity_correct=correct,D_status=sc['score']['status'],D_match=sc['score']['match'],singular_values=d['jacobian_singular_values'],bounds_hit=d['bounds_hit']))
    groups={}
    for field in ('color','hand','pitch','specular','same_color_scene'):
        groups[field]={}
        for value in sorted(set(str(r[field]) for r in allrows)):
            groups[field][value]={m:dict(Counter(r['decision'] for r in allrows if str(r[field])==value and r['method']==m)) for m in 'ABC'}
    geomsummary={}
    for mode in ('end-to-end','oracle'):
        rr=[r for r in geom if r['mode']==mode];valid=[r for r in rr if r['C_error_px'] is not None]
        geomsummary[mode]=dict(pairs=len(set((r['scene'],r['A']) for r in rr)),hypotheses=len(rr),correct_AB_family=sum(r['AB_correct_family'] for r in rr),visible_C_comparisons=len(valid),conditional_C_correct=sum(r['C_match_correct'] for r in valid),conditional_C_wrong=sum(r['C_conditional_match'] and not r['C_match_correct'] for r in rr),physically_valid=sum(r['physical_valid'] for r in rr),median_C_error_px=float(np.median([r['C_error_px'] for r in valid])) if valid else None,median_baseline_best3_error_px=float(np.median([r['baseline_best_of_three_error_px'] for r in valid])) if valid else None)
    summary=dict(test1={m:dict(v) for m,v in by_method.items()},stratified=groups,localization=dict(n=len(localization),median_error_px=float(np.median([r['error_px'] for r in localization])),interval_coverage=float(np.mean([r['covered'] for r in localization]))),test2=geomsummary,fourth_predictions=len(fourths),physically_valid_fourth_predictions=0,evaluation_policy='visible truth area >=50 native px; nearest centroid ties within 2 px; majority membership >=.5; IDs opened after frozen predictions; no synthetic-label parameter tuning')
    save(out/'detection-evaluation.json',detection);save(out/'synthetic-test1-evaluation.json',allrows);save(out/'synthetic-test2-evaluation.json',geom);save(out/'synthetic-fourth-evaluation.json',fourths);save(out/'localization-evaluation.json',localization);save(out/'evaluation-freeze-hashes.json',hashes);save(out/'synthetic-summary.json',summary)
    print(summary)
