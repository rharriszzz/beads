from .calibrate import *
def main():
    data,_=load_evidence();m=measurements();shape=read(BASE/'results/control-camera-roll.json.gz')['parameters']
    for ident in [767,121,694,631]:
        old=read(ROOT/f'photo2/r297/results/pilot/exports/model-{ident}.json.gz')['parameters'];p=deepcopy(old)
        p['axis_nodes']=read(BASE/f'results/joint-{ident}.json.gz')['parameters']['axis_nodes']
        for k in ['axial','scale','elevation','roll']:p[k]=shape[k]
        r=fit(p,data,m,'joint',max_nfev=16,physical=True);r['family_source']=ident
        save(BASE/f'results/roll-{ident}.json.gz',r)
        print(ident,{k:r['parameters'][k] for k in ['axial','scale','minor','elevation','perspective','roll']},r['metrics'],r['physical']['state'],flush=True)
if __name__=='__main__':main()
