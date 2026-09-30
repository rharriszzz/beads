"""Snapshot-to-snapshot manual graph audit; no pose or image inference."""
import argparse,hashlib,json,os
from pathlib import Path
import numpy as np
from analyze_label_series import analyze,edges_from_document,STEPS

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations',type=Path,default=ROOT/'photo2/manual-labels-r161.json')
    parser.add_argument('--previous',type=Path,default=ROOT/'photo2/manual-labels-r146.json')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r161')
    args=parser.parse_args()
    doc=json.loads(args.annotations.read_text());old=json.loads(args.previous.read_text())
    image=ROOT/doc['source']['filename']
    assert sha(image)==doc['source']['sha256'] and old['source']==doc['source']
    report=analyze(doc,max_omissions=0)
    args.output.mkdir(parents=True,exist_ok=True)
    report['provenance']=dict(annotations_sha256=sha(args.annotations),previous_sha256=sha(args.previous),
        image_sha256=sha(image),script_sha256=sha(Path(__file__)),
        graph_analyzer_sha256=sha(ROOT/'photo2/analyze_label_series.py'))
    a={p['id']:p for p in old['annotations']};b={p['id']:p for p in doc['annotations']}
    old_edges={(e.start,e.end,e.direction) for e in edges_from_document(old)}
    new_edges={(e.start,e.end,e.direction) for e in edges_from_document(doc)}
    report['extension']=dict(previous_revision=old['revision'],added_beads=sorted(p['number'] for k,p in b.items() if k not in a),
        removed_beads=sorted(p['number'] for k,p in a.items() if k not in b),
        changed_existing_beads=sorted(a[k]['number'] for k in a.keys()&b.keys() if a[k]!=b[k]),
        added_links=[list(e) for e in sorted(new_edges-old_edges)],
        removed_links=[list(e) for e in sorted(old_edges-new_edges)],
        duplicate_recorded_links=len(report['edges'])-len(new_edges))
    if len(report['conditional_charts'])!=1:
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        raise SystemExit('No consistent single chart; inspect the saved report, do not repair the labels automatically.')
    chart=report['conditional_charts'][0];coords=chart['coordinates']
    edges=report['edges'];numbers=sorted(int(n) for n in coords)
    # Independent incidence-matrix validation of the recorded triangle cycle basis.
    edge_lookup={(e['start'],e['end']):i for i,e in enumerate(edges)}
    rows=[];incidence=np.zeros((len(edges),len(numbers)))
    for i,e in enumerate(edges):
        incidence[i,numbers.index(e['start'])]=-1;incidence[i,numbers.index(e['end'])]=1
        delta=np.array(coords[str(e['end'])])-coords[str(e['start'])]
        assert np.array_equal(delta,STEPS[e['direction']])
    for tri in report['triangles']:
        x,y,z=tri['beads'];row=np.zeros(len(edges))
        for start,end in [(x,y),(y,z),(z,x)]:
            forward=(start,end) in edge_lookup
            row[edge_lookup[(start,end) if forward else (end,start)]]=1 if forward else -1
        rows.append(row)
    basis=np.array(rows);rank=int(np.linalg.matrix_rank(basis))
    assert np.array_equal(basis@incidence,np.zeros((len(rows),len(numbers))))
    assert rank==report['cycle_rank'] and chart['coordinate_collisions']==0
    report['independent_cycle_check']=dict(triangle_count=len(rows),triangle_matrix_rank=rank,
        all_triangle_rows_close=True,all_recorded_unit_links_match_chart=True)
    report['relative_families']={}
    for name,weights in [('A',{'d1':1,'d2':7,'d3':6}),('B',{'d1':-1,'d2':6,'d3':7})]:
        candidate=next(c for c in chart['relative_index_candidates'] if c['weights']==weights)
        origin=candidate['offsets']['20'];offsets={n:k-origin for n,k in candidate['offsets'].items()}
        assert len(set(offsets.values()))==len(numbers)
        lo,hi=min(offsets.values()),max(offsets.values())
        report['relative_families'][name]=dict(weights=weights,origin_bead=20,offsets=offsets,
            minimum=lo,maximum=hi,span=hi-lo,unlabelled_slots_in_span=hi-lo+1-len(numbers),
            status='Conditional offsets; missing slots are not inferred hidden beads or recovered whole-string indices')
    report['previous_model_domain']=dict(minimum=-60,maximum=47,
        status='R160 ray-model domain; extend with latent-neighbor margins before testing this larger patch')
    report['diagonal_runs']={}
    for direction in ['d2','d3']:
        nxt={e['start']:e['end'] for e in edges if e['direction']==direction}
        incoming=set(nxt.values());paths=[]
        for start in sorted(nxt):
            if start in incoming:continue
            path=[start]
            while path[-1] in nxt:path.append(nxt[path[-1]])
            paths.append(path)
        maximum=max(len(p)-1 for p in paths)
        report['diagonal_runs'][direction]=dict(maximum_recorded_steps=maximum,
            longest_recorded_paths=[p for p in paths if len(p)-1==maximum],
            status='Links count steps; an m-step run contains m+1 numbered bodies')
    report['nominal_one_step_difference']=dict(direction6_steps=7,direction7_steps=6,
        familyA=dict(d2_steps=6,d3_steps=7),familyB=dict(d2_steps=7,d3_steps=6),
        centerline_distance=18.618276905,nominal_rows=6.461538,
        reference_sha256=sha(ROOT/'photo2/PATCH_SUFFICIENCY.md'),
        status='Earlier nominal outward-angle comparison scale, not a guaranteed minimum; intermediate bodies can be hidden')
    pairs=[(a,b) for a in range(1,14) for b in range(1,14) if 6*a==7*b]
    shortest=min(pairs,key=lambda p:sum(p));assert shortest==(7,6)
    report['conditional_diagonal_identity_test']=dict(
        minimum_direction6_steps=shortest[0],minimum_direction7_steps=shortest[1],
        total_links=13,unique_bodies_if_paths_meet=13,unique_bodies_if_paths_do_not_meet=14,
        tests=[dict(d2_steps=6,d3_steps=7,A_endpoint_index_difference=0,B_endpoint_index_difference=-13),
               dict(d2_steps=7,d3_steps=6,A_endpoint_index_difference=13,B_endpoint_index_difference=0)],
        guaranteed_only_if=['Each link is an exact consecutive neighbor in the named direction',
            'Endpoint and intermediate bead identities are correct',
            'The two paths share a start and move forward in the same major-circle sense',
            'Necklace contains more than 13 distinct beads; the current 40-body inventory supplies this lower bound if identities are correct'],
        present_in_current_graph=False,
        current_graph_evidence='Both index maps are injective and the 47 local triangles span all 47 cycles; no family-specific closure/collision witness',
        limitation='Minimum for this two-forward-diagonal-path identity test, not a universal minimum for helicity inference or a promise of visible paths')
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r161-mpl')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from PIL import Image,ImageOps
    rgb=ImageOps.exif_transpose(Image.open(image)).convert('RGB');x0,y0,x1,y1=doc['view_crop']
    fig,axes=plt.subplots(1,3,figsize=(16,8),constrained_layout=True)
    for ax in axes[:2]:
        ax.imshow(rgb.crop(doc['view_crop']),extent=[x0-.5,x1-.5,y1-.5,y0-.5],interpolation='nearest')
        ax.set_xlabel('Source x');ax.set_ylabel('Source y')
    axes[0].set_title('Raw context; source image unchanged')
    axes[1].set_title('Maker locations: cyan new 28–40; white previous 1–27')
    for p in doc['annotations']:
        n=p['number'];color='cyan' if n in report['extension']['added_beads'] else 'white'
        axes[1].plot(p['x'],p['y'],'+',color=color,ms=5)
        axes[1].annotate(str(n),(p['x'],p['y']),xytext=(4,-4),textcoords='offset points',color=color,
            fontsize=7,bbox=dict(facecolor='black',alpha=.65,pad=.6))
    colors={'d1':'#b96800','d2':'#007f9e','d3':'#8e55b1'}
    for e in edges:
        axes[2].annotate('',coords[str(e['end'])],coords[str(e['start'])],
            arrowprops=dict(arrowstyle='->',color=colors[e['direction']],lw=.9,shrinkA=8,shrinkB=8))
    for n,(u,v) in coords.items():
        axes[2].text(u,v,n,ha='center',va='center',fontsize=7,
            bbox=dict(boxstyle='circle',facecolor='#bfffff' if int(n)>27 else 'white',edgecolor='gray',pad=.2))
    us,vs=zip(*coords.values())
    axes[2].set_xlim(min(us)-1,max(us)+1);axes[2].set_ylim(min(vs)-1,max(vs)+1)
    axes[2].set_aspect('equal');axes[2].grid(alpha=.2)
    axes[2].set_xlabel('d1 count u');axes[2].set_ylabel('d2 count v')
    axes[2].set_title('Conditional chart: d1 →, d2 ↑, d3 ↖\n40 beads; 86 links; 47 closing cycles')
    fig.suptitle('Revision 296: all previous locations and links preserved. Numbers are observation names, not bead_index.',fontsize=12)
    fig.savefig(args.output/'extended-chart.png',dpi=160);plt.close(fig)
    print(json.dumps(dict(revision=doc['revision'],beads=report['bead_count'],links=report['recorded_link_count'],
        cycle_rank=report['cycle_rank'],triangle_rank=rank,six_neighbors=report['six_recorded_neighbors']),indent=2))


if __name__=='__main__':main()
