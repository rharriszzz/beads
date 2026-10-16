from .calibrate import *
def main():
    data,_=load_evidence();m=measurements()
    for ident in [767,694,121,631]:
        old=read(ROOT/f'photo2/r297/results/pilot/exports/model-{ident}.json.gz')['parameters']
        p=deepcopy(old);p['axis_nodes']=read(BASE/f'results/joint-{ident}.json.gz')['parameters']['axis_nodes']
        fixed=read(BASE/'results/control-dimensions.json.gz')['parameters']
        p.update(axial=fixed['axial'],scale=fixed['scale'])
        r=fit(p,data,m,'joint',max_nfev=24,physical=True);r['family_source']=ident
        save(BASE/f'results/physical-{ident}.json.gz',r)
        print(ident,{k:r['parameters'][k] for k in ['axial','scale','minor','elevation','perspective']},r['metrics'],r['physical']['state'],flush=True)
if __name__=='__main__':main()
