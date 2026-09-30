"""Independent source-macro appearance/ID calibration for automatic proposals.

ID renders are evaluator-only. Detection sees the appearance PNG, never IDs,
source-loop indices, palette declarations or camera settings.
"""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from auto_label_beads import detect,adjacency,sha
from check_placement import source_parts,run_pov

ROOT=Path(__file__).resolve().parents[1]


def render(out,hand,palette=0,offset=0):
    parameters,placement,macro=source_parts()
    if hand<0:
        placement=placement.replace('360*(bead_index/exact_beads_per_row','-360*(bead_index/exact_beads_per_row')
    header=('#version 3.7;\nglobal_settings {assumed_gamma 1}\n'
        'camera {orthographic location <0,-40,65> look_at <0,0,8> right x*72 up y*72}\n'
        '#declare nbeads=312;\n#declare beads_per_row=6.5;\n#declare rclock=0;\n'
        +parameters+'\n#declare hole_size_per_bead_size=.14;\n'+macro)
    colors=[[(.02,.18,.8),(.95,.48,.015),(.009,.009,.009)],
            [(.02,.75,.18),(.7,.035,.55),(.009,.009,.009)]][palette]
    background=[(.52,.43,.34),(.25,.35,.48)][palette]
    loop='#declare bead_index=0;\n#while(bead_index<nbeads)\n'+placement
    ending=('#declare bead_index=bead_index+1;\n#end\n')
    appearance=header+'light_source {<0,-100,120> rgb 1.6}\n'
    appearance+=f'plane {{z,0 pigment{{rgb <{",".join(map(str,background))}>}} finish{{ambient .25 diffuse .7}}}}\n'
    for j,c in enumerate(colors):
        appearance+=f'#declare m{j}=material{{texture{{pigment{{rgb <{",".join(map(str,c))}>}} finish{{ambient .08 diffuse .7 phong 1.4 phong_size 45}}}}}};\n'
        appearance+=f'#declare b{j}=bead(m{j},.8,.7,1);\n'
    appearance+=loop+'#switch(mod(bead_index,3))\n'
    for j in range(3):appearance+=f'#case({j}) object{{b{j} rotate z*chain_angle translate t1+t2+<0,0,chain_minor+2*bead_radius> translate <{offset},0,0>}} #break\n'
    appearance+='#end\n'+ending
    name=f'hand{hand:+d}-palette{palette}-shift{offset}'
    scene=out/(name+'.pov');scene.write_text(appearance)
    png,command=run_pov(scene,800,800)
    ids=header+loop+('#declare code=bead_index+1;\n'
        '#declare m=material{texture{pigment{rgb <mod(code,256)/255,floor(code/256)/255,0>} finish{ambient 0 emission 1 diffuse 0}}};\n'
        'object{bead(m,.8,.7,1) rotate z*chain_angle translate t1+t2+<0,0,chain_minor+2*bead_radius>'
        +f' translate <{offset},0,0>'+'}\n'+ending)
    idscene=out/(name+'-ids.pov');idscene.write_text(ids)
    idpng,idcommand=run_pov(idscene,800,800)
    return png,idpng,dict(hand=hand,palette=palette,offset=offset,N=312,
        appearance_command=command,id_command=idcommand,
        scene_sha256=sha(scene),id_scene_sha256=sha(idscene),source_sha256=sha(ROOT/'beads.pov'))


def score(result,graph,ids,N):
    encoded=np.array(Image.open(ids).convert('RGB')).astype(int)
    labels=encoded[:,:,0]+256*encoded[:,:,1]-1
    area=np.bincount((labels+1).ravel(),minlength=N+1)[1:]
    # A visible area threshold is declared, not an exact visibility guarantee.
    eligible=area>=max(20,np.quantile(area[area>0],.5)*.35)
    body=[]
    for p in result['points']:
        x,y=np.round(p['source_xy']).astype(int);body.append(int(labels[y,x]))
    distinct=set(body)-{-1};detected=np.bincount(np.array(body)+1,minlength=N+1)[1:]
    relations=[]
    for e in graph['edges']:
        a,b=body[e['start']],body[e['end']]
        delta=min((a-b)%N,(b-a)%N) if a>=0 and b>=0 else None
        relations.append(dict(direction=e['direction'],delta=delta,true_neighbor=delta in (1,6,7)))
    return dict(proposals=len(body),eligible_visible=int(eligible.sum()),
        eligible_located=int(np.sum(eligible&(detected>0))),eligible_missed=np.flatnonzero(eligible&(detected==0)).tolist(),
        distinct_bodies=len(distinct),on_paper=body.count(-1),duplicate_points=int(sum(max(0,k-1) for k in detected)),
        adjacency_proposals=len(relations),true_unsigned_neighbors=sum(e['true_neighbor'] for e in relations),
        per_direction={d:dict(count=sum(e['direction']==d for e in relations),
            true_neighbor=sum(e['direction']==d and e['true_neighbor'] for e in relations),
            deltas={str(k):sum(e['direction']==d and e['delta']==k for e in relations) for k in (0,1,6,7,None)}) for d in ('d1','d2','d3')},
        point_body_ids=body,relations=relations,
        limitation='Visible-area eligibility is diagnostic; on-bead ownership does not establish one point per body, outward anchors or direction signs.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'photo2/output/r167/calibration')
    p.add_argument('--reuse',action='store_true');args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    reports=[]
    for hand,palette,offset in [(1,0,0),(-1,0,0),(1,1,2)]:
        name=f'hand{hand:+d}-palette{palette}-shift{offset}'
        if args.reuse:
            png=args.output/(name+'.png');ids=args.output/(name+'-ids.png')
            provenance=json.loads((args.output/(name+'-provenance.json')).read_text())
        else:
            png,ids,provenance=render(args.output,hand,palette,offset)
            (args.output/(name+'-provenance.json')).write_text(json.dumps(provenance,indent=2)+'\n')
        provenance.update(appearance_sha256=sha(png),id_sha256=sha(ids))
        try:
            result=detect(np.array(Image.open(png).convert('RGB')));graph=adjacency(result)
            report=dict(**provenance,**score(result,graph,ids,312),parameters=result['parameters'])
        except ValueError as exc:report=dict(**provenance,failed=str(exc))
        reports.append(report)
        print(name,{k:v for k,v in report.items() if k in ('proposals','eligible_visible','eligible_located','on_paper','duplicate_points','adjacency_proposals','true_unsigned_neighbors','failed')},flush=True)
        (args.output/'report.json').write_text(json.dumps(dict(script_sha256=sha(Path(__file__)),detector_sha256=sha(ROOT/'photo2/auto_label_beads.py'),cases=reports),indent=2)+'\n')


if __name__=='__main__':main()
