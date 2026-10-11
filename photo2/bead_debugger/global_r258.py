"""Unanchored low-mode global fit from distributed bead evidence.

All curve positions can move, including unobserved spans. The basis contains
constant translation and first/second periodic harmonics, with no old-curve loss.
"""
import copy,json
import numpy as np
from PIL import Image,ImageDraw,ImageOps
from .refit import OUT,ROOT,BeadCurve,SurfaceLoss,physical,audit
from .generate import save

def apply_global(config,p):
    c=copy.deepcopy(config);u=np.arange(len(c['knots']))/len(c['knots']);a=2*np.pi*u
    b=np.c_[np.ones(len(u)),np.sin(a),np.cos(a),np.sin(2*a),np.cos(2*a)]
    m=BeadCurve(c);r,d,_=m.view.basis();inv=np.linalg.inv(np.array([r[:2],d[:2]]))/m.view.scale
    q=np.array(c['knots']);q[:,:2]+=(b@np.asarray(p[:10]).reshape(5,2))@inv.T;c['knots']=q.tolist();c['camera']['scale']*=float(np.exp(p[10] if len(p)>10 else 0.));return c

def run(budget=301):
    c=json.loads((OUT/'R258_distributed_C.json').read_text());losses={}
    for name in ['origin','straight-black','bend','opposite']:
        e=json.loads((OUT/(name+'-evidence.json')).read_text());losses[name]=SurfaceLoss(e['box'],e['observations'])
    p=np.zeros(11);steps=np.r_[np.full(10,1.5),.003];count=0;history=[]
    def score(q):
        nonlocal count
        count+=1;m=BeadCurve(apply_global(c,q));return float(np.mean([loss.evaluate(m) for loss in losses.values()])+.8*physical(m)['cost'])
    start=score(p);best=start
    while count+22<=budget:
        improved=False
        for j in range(11):
            choices=[]
            for sign in [-1,1]:
                q=p.copy();q[j]+=sign*steps[j];choices.append((score(q),q))
            value,q=min(choices,key=lambda a:a[0])
            if value<best-1e-6:best,p=value,q;improved=True
        history.append(dict(evaluations=count,objective=best,parameters=p.tolist()))
        if not improved:
            steps*=.5
            if max(steps[:10])<.18:break
    found=apply_global(c,p);found['id']='R258_global_low_modes';found['variant']='distributed global bead fit';found['independence']='All curve positions free in ten smooth global modes plus camera scale after four local fits; hidden spans are physically interpolated, not photo-verified';save(OUT/'R258_global_low_modes.json',found)
    e=json.loads((OUT/'spatial-holdout-evidence.json').read_text());losses['spatial-holdout']=SurfaceLoss(e['box'],e['observations'])
    result=dict(id=found['id'],parameters=p.tolist(),camera_scale_factor=float(np.exp(p[10])),evaluations=count,budget=budget,start_objective=start,objective=best,history=history,physical=physical(BeadCurve(found)),sections={name:dict(before=audit(c,loss),after=audit(found,loss)) for name,loss in losses.items()},
                protocol='Fit four-region training only; all physical curve locations may depart via constant/first/second harmonic modes; no curve anchors or displacement bounds; fifth region held out',status='Exploratory global candidate, not adopted reconstruction')
    save(OUT/'global-low-modes.json',result)
    photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');panels=[]
    from .models import load
    old=load('N2696_h+1_f0')[1]
    for m,title in [(old,'Original physical curve'),(BeadCurve(found),'Global bead-driven candidate; hidden spans uncertain')]:
        line=m.view.project(m.geometry(np.arange(found['n']))['line']);im=photo.copy();d=ImageDraw.Draw(im);d.line([tuple(p) for p in line]+[tuple(line[0])],fill=(50,255,255),width=3);im=im.resize((635,796));out=Image.new('RGB',(635,826),(20,32,42));out.paste(im,(0,30));ImageDraw.Draw(out).text((8,8),title,fill='white');panels.append(out)
    im=Image.new('RGB',(1270,826));im.paste(panels[0],(0,0));im.paste(panels[1],(635,0));im.save(OUT/'global-low-modes-before-after.png')
    print(result['parameters'],start,best,[(k,v['after']['metrics']['all']['ownership_mean']) for k,v in result['sections'].items()],flush=True)
if __name__=='__main__':run()
