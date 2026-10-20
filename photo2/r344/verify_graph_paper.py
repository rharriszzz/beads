"""Independent direction, seam, interval, copy-color and nonrectangular-cut audit."""
from common import *
from graph_paper import layout, pattern_layout, representative, boundary, X_SCALE, Y_SCALE, RX, RY
import math


def independent_xy(k,x0):
    # Exhaust integer x sites rather than reuse the modular producer equation.
    candidates=[(x,(2*k-x)//13) for x in range(x0,x0+13) if (2*k-x)%13==0]
    assert len(candidates)==1
    x,y=candidates[0];assert (x+y)%2==0
    return x,y


def above_cut(x,y,cut):
    # Horizontal spans classify every bead center; vertical cuts sit at the
    # opposite x parity and therefore cannot pass through a bead in that row.
    for (a,b),(c,d) in zip(cut,cut[1:]):
        if b==d and min(a,c)<=x<=max(a,c):
            return y>b
    raise AssertionError((x,y,cut))


def segment_misses_ellipse(point,p,q):
    # Distance to a segment in normalized ellipse coordinates.
    center=np.array([point['x']*X_SCALE,point['y']*Y_SCALE]);scale=np.array([RX,RY])
    a=(np.array(p)*[X_SCALE,Y_SCALE]-center)/scale
    b=(np.array(q)*[X_SCALE,Y_SCALE]-center)/scale
    v=b-a;t=float(np.clip(-a@v/(v@v),0,1)) if v@v else 0
    return float(np.linalg.norm(a+t*v))>1


def main():
    seal=read(OUT/'presentation-input-seal.json')
    assert all(sha(ROOT/name)==h for name,h in seal.items()),'Presentation changed scientific data'
    assert all(sha(OUT/Path(name).name)==h for name,h in seal.items()),'Fresh science differs from the preserved delivery'
    archives={}
    for phase in ['pre-graph-paper-37a23300','pre-seven-sides-ff61d4e0']:
        archive=ROOT/'photo2/r344'/phase;prior=read(archive/'manifest.json')
        for name,h in prior.items():
            old=Path(name)
            archived=archive/(old.name if old.parent==Path('photo2') else old.relative_to('photo2/r344'))
            assert sha(archived)==h
        archives[phase]=len(prior)
    # Recount each new individual judgment against the identical R343 cohort.
    # These are independent support calculations, not extra pigment decisions.
    _,before,coords=load_graph(ROOT/'photo2/r343/graph.json.gz')
    blocks=read(OUT/'evaluation.json')['geographic_blocks'];effects=[]
    for changed in [[],[CORRECTIONS[0]],[CORRECTIONS[1]],CORRECTIONS]:
        colors={o:('yellow' if o in changed else before[o]['color']) for o in coords}
        statuses=Counter();affected=[]
        for residue in range(208):
            ids=sorted(o for o in coords if (7*coords[o][0]+6*coords[o][1])%208==residue)
            ct=Counter(colors[o] for o in ids);regions={c:sorted({blocks[o] for o in ids if colors[o]==c}) for c in ct}
            supported=len(ct)==1 and len(ids)>=3 and len(next(iter(regions.values())))>=3
            state='conflicting' if len(ct)>1 else 'supported' if supported else 'insufficient'
            statuses[state]+=1
            if residue in [29,127]:affected.append(dict(position=residue,counts=dict(ct),regions_by_color=regions,status=state,ids=ids))
        effects.append(dict(changed_ids=list(changed),indexed=len(coords),**dict(statuses),affected_positions=affected))
    assert [(e['supported'],e['conflicting'],e['insufficient']) for e in effects]==[(197,4,7),(198,3,7),(198,3,7),(199,2,7)]
    save(OUT/'correction-effects.json',dict(states=effects,cohort_unchanged=True,rule_unchanged=True,geometry_changed=False))
    paper=read(OUT/'graph-paper-layout.json');pattern=read(OUT/'pattern208.json')
    direction_checks=seam_checks=point_checks=cut_checks=horizontal_checks=0
    def check_rows(points,x0):
        checks=0
        for y in sorted({r['y'] for r in points}):
            row=sorted((r for r in points if r['y']==y),key=lambda r:r['x'])
            basic=[r for r in row if x0<=r['x']<x0+13]
            left=[r for r in row if r['x']<x0];right=[r for r in row if r['x']>=x0+13]
            assert len(left)==len(right)==7 and len(basic) in [6,7] and len(row)==len(basic)+14
            assert [r['k'] for r in left]==list(range(basic[0]['k']-7,basic[0]['k']))
            assert [r['k'] for r in right]==list(range(basic[-1]['k']+1,basic[-1]['k']+8))
            assert all(b['x']-a['x']==2 and b['k']-a['k']==1 for a,b in zip(row,row[1:]))
            assert all(r['side']=='left' for r in left) and all(r['side']=='right' for r in right)
            checks+=len(row)-1
        return checks
    def check_sides(trial):
        # Midpoints between adjacent centers leave RX=18px inside a24px
        # half-pitch. Horizontal joins at half rows leave RY=14px inside16px.
        assert RX < X_SCALE and RY < Y_SCALE/2
        lo,hi=trial['rows'];sides=trial['side_boundaries']
        assert all(len(path)==2*(hi-lo+1) for path in sides.values())
        for i,y in enumerate(range(lo,hi+1)):
            row=sorted(r['x'] for r in trial['points'] if r['y']==y and r['side']=='basic')
            for name,x in [('left',row[0]-1),('right',row[-1]+1)]:
                assert sides[name][2*i:2*i+2]==[[x,y-.5],[x,y+.5]]
            assert sum(row[0]-1<r['x']<row[-1]+1 for r in trial['points'] if r['y']==y)==len(row)
        return hi-lo+1
    side_row_checks=check_sides(paper)
    horizontal_checks+=check_rows(paper['points'],paper['x0'])
    for point in paper['points']:
        x,y,k=point['x'],point['y'],point['k'];a,b=point['a'],point['b']
        assert x==a-b and y==a+b and k==7*a+6*b==(x+13*y)//2
        canonical=independent_xy(k,paper['x0']);s=point['lateral_copy']
        assert (x,y)==(canonical[0]+13*s,canonical[1]-s)
        assert point['position']==k%208 and point['in_chosen_interval']==(paper['x0']<=x<paper['x0']+13 and 0<=k<208)
        e=pattern['entries'][k%208]
        assert (point['strict_color'],point['provisional_color'])==(e['strict_color'],e['provisional_color'])
        point_checks+=1
        for dx,dy,dk in [(2,0,1),(-1,1,6),(1,1,7)]:
            assert (x+dx+13*(y+dy))//2-k==dk
            nx,ny=independent_xy(k+dk,paper['x0']);multiple=(x+dx-nx)//13
            assert x+dx-nx==13*multiple and y+dy-ny==-multiple;direction_checks+=1;seam_checks+=bool(multiple)
    canonical=[r for r in paper['points'] if r['side']=='basic']
    chosen=[r for r in canonical if 0<=r['k']<208]
    assert len(chosen)==208 and sorted(r['k'] for r in chosen)==list(range(208))
    assert {r['y'] for r in chosen}==set(range(32))
    for y in range(32):assert sum(r['y']==y for r in chosen)==(6 if y%2==0 else 7)
    assert min(r['k'] for r in canonical)<0 and max(r['k'] for r in canonical)>207
    assert [13,-1]==[6-(-7),6+(-7)] and 7*6+6*(-7)==0
    assert [0,32]==[16-16,16+16] and 7*16+6*16==208
    assert [13,415]==[214-201,214+201] and 7*214+6*201==2704
    assert np.array_equal(np.array([13,415]),13*np.array([0,32])+np.array([13,-1]))
    cases=[]
    for length in [1,2,7,13,17,52,104,207,208,209,299,338]:
        for origin in [-23,0,5,111]:
            for x0 in [-13,-1,0,7]:
                trial=layout(length,origin,x0);rows=trial['points'];inside=[]
                side_row_checks+=check_sides(trial)
                horizontal_checks+=check_rows(rows,x0)
                for r in rows:
                    cx,cy=independent_xy(r['k'],x0);s=(r['x']-cx)//13
                    assert (r['x'],r['y'])==(cx+13*s,cy-s)
                    geometric=x0<=r['x']<x0+13 and above_cut(r['x'],r['y'],trial['start_boundary']) and not above_cut(r['x'],r['y'],trial['end_boundary'])
                    assert geometric==r['in_chosen_interval']
                    if geometric:inside.append(r['k'])
                    for cut in [trial['start_boundary'],trial['end_boundary']]:
                        # Only nearby rows can intersect the boundary.
                        if abs(r['y']-cut[0][1])<2:
                            for a,b in zip(cut,cut[1:]):assert segment_misses_ellipse(r,a,b);cut_checks+=1
                assert sorted(inside)==list(range(origin,origin+length))
                dx,dy=2*length-13*round(2*length/13),round(2*length/13)
                assert dx+13*dy==2*length and (dx+dy)%2==0
                cases.append(dict(length=length,start=origin,x0=x0,chosen=len(inside),translation_xy=[dx,dy],start_cut=trial['start_boundary'],end_cut=trial['end_boundary']))
    # The current opaque colors and simple ellipse shape are identical for all
    # copies of a position; no displayed copy adds a new observation.
    groups=defaultdict(set)
    identities=defaultdict(set)
    for r in paper['points']:
        groups[r['position']].add((r['strict_color'],r['provisional_color']))
        identities[r['k']].add((r['position'],tuple(r['canonical_xy']),r['strict_color'],r['provisional_color']))
    assert len(groups)==208 and all(len(values)==1 for values in groups.values())
    assert all(len(values)==1 for values in identities.values())
    toy='RBYBRYBBRYRBYBRYB';toy_paper=pattern_layout(toy,start=5,x0=7)
    assert len(toy)==17 and sum(r['in_chosen_interval'] for r in toy_paper['points'])==17
    for r in toy_paper['points']:
        assert r['strict_color']=={'R':'red','Y':'yellow','B':'black'}[toy[(r['k']-5)%17]]
    # Concrete second-seam examples: these are the seventh extensions of a
    # seven-bead row, not optional extra observations.
    y1=sorted([r for r in paper['points'] if r['y']==1],key=lambda r:r['x'])
    assert (y1[0]['x'],y1[0]['k'],y1[0]['lateral_copy'])==(-15,-1,-2)
    assert (y1[-1]['x'],y1[-1]['k'],y1[-1]['lateral_copy'])==(25,19,2)
    save(OUT/'graph-paper-verification.json',dict(passed=True,scientific_products_byte_preserved=len(seal),archived_historical_presentation_files=sum(archives.values()),archives=archives,maker_correction_states_independently_recounted=4,display_points=point_checks,
                                               chosen_unique_indices=208,canonical_display_points=len(canonical),rows_of_chosen_block=32,row_counts=[6,7]*16,
                                               direction_equations=direction_checks,seam_transitions=seam_checks,general_cases=len(cases),boundary_ellipse_clearance_tests=cut_checks,
                                               side_beads_each_row=7,current_row_symbol_counts=[20,21]*24,horizontal_index_steps_checked=horizontal_checks,
                                               unique_unwrapped_display_indices=len(identities),same_index_display_aliases=point_checks-len(identities),sequence_only_17_color_example=True,
                                               solid_side_boundaries=True,side_boundary_row_checks=side_row_checks,side_lines_clear_of_ellipses=True,
                                               second_seam_examples=[y1[0],y1[-1]],
                                               general_case_results=cases,strict_unknown_positions=[e['residue'] for e in pattern['entries'] if e['strict_color']=='?'],
                                               equations=dict(index='2k=x+13y',kernel_AB=[6,-7],kernel_XY=[13,-1],period208_AB=[16,16],period208_XY=[0,32],conditional_H_XY=[13,415]),
                                               caveat='Presentation and indexing algebra only; no additional photographic evidence, physical count, color correction or winding adoption.'))
    print('PASS graph-paper math',point_checks,'points;',len(cases),'general cases;',cut_checks,'ellipse-cut checks')


if __name__=='__main__':
    main()
