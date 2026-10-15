"""Fixed known-geometry stress diagnostics, not extra fitted photographic models."""
from .common import *
from .physics import forward,bright_truth

def main():
    result=[]
    for name in ('scene-06','scene-09'):
        folder=OUT/'synthetic'/name;scene=read(folder/'evaluation.json');p=scene['scene']['parameters'];fields={}
        for key,q in [('pose_plus10deg',{**p,'inclination':p['inclination']+10}),('light_rotated15deg',{**p,'light':(np.array([[np.cos(np.pi/12),-np.sin(np.pi/12),0],[np.sin(np.pi/12),np.cos(np.pi/12),0],[0,0,1]])@p['light']).tolist()})]:
            f=forward(q);fields[key]={j:bright_truth(f['specular'],f['owner']==j-14) for j in range(29)}
        for b in scene['beads']:
            mm=b['measurements']['on']
            if len(mm)!=1 or mm[0]['purity']<.95 or b['visible_area']<40:continue
            row=dict(scene=name,owner=b['owner'],color=b['color'],errors={},missing=[])
            options={key:v[b['owner']] for key,v in fields.items()};options['known']=b['normal_prediction']
            neighbor=next((a for a in scene['beads'] if a['owner']==b['owner']+1),None);options['wrong_next_identity']=neighbor['normal_prediction'] if neighbor else None
            for k,v in options.items():
                if v:row['errors'][k]=float(np.linalg.norm(np.array(mm[0]['patch'])-v['centroid']))
                else:row['missing'].append(k)
            result.append(row)
    summary={}
    for k in ('known','pose_plus10deg','light_rotated15deg','wrong_next_identity'):
        paired=[r for r in result if k in r['errors'] and 'known' in r['errors']]
        summary[k]=dict(perturbed=stats([r['errors'][k] for r in paired],2*1.7845369838*9),paired_known=stats([r['errors']['known'] for r in paired],2*1.7845369838*9),missing=sum(k in r['missing'] for r in result))
    save(OUT/'sensitivity.json',dict(rows=result,summary=summary,scope='Two preselected evaluation scenes, fixed +10deg camera, +15deg light azimuth, next-body wrong identity; no fitting, lost predictions explicitly counted.'))
if __name__=='__main__':main()
