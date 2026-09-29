"""R150-R151: intrinsic 1/6/7 angles between minor-outward bead points.

Local straight-tube angles, not camera-projected directions. Shortest minor-circle
displacement connects neighbors; it does not follow the thread through a turn.
"""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/beads-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from bead_placement import Rope, place_tube_coordinates, minor_outward_point
from local_surface_fit import centers
from check_placement import ROOT, sha


def calculate(nbeads=None,anchor='outward'):
    rope = Rope(676 if nbeads is None else nbeads)
    q = rope.beads_per_row if nbeads is None else rope.exact_beads_per_row
    advance = .65*(2*rope.bead_radius)*1.05
    pitch = advance/q
    observation_radius=rope.chain_minor+(rope.bead_radius if anchor=='outward' else 0)
    rows = []
    for hand in (1,-1):
        for j in (1,6,7):
            delta = (hand*2*np.pi*j/q+np.pi)%(2*np.pi)-np.pi
            axial = j*pitch
            transverse = 2*observation_radius*np.sin(abs(delta)/2)
            rows.append(dict(hand=hand,index_step=j,axial=axial,
                minor_delta_deg=float(np.degrees(delta)),minor_arc=observation_radius*delta,
                transverse_chord=transverse,
                surface_angle_deg=float(np.degrees(np.arctan2(observation_radius*delta,axial))),
                chord_angle_deg=float(np.sign(delta)*np.degrees(np.arctan2(transverse,axial)))))
    return dict(nbeads=nbeads,nrows=None if nbeads is None else rope.nrows,
        exact_beads_per_turn=q,bead_radius=rope.bead_radius,minor_radius=rope.chain_minor,
        anchor=anchor,observation_radius=observation_radius,
        advance_per_turn=advance,pitch_per_index=pitch,rows=rows)


def validate_nominal(result):
    """Independently measure 3D displacement using the existing placement kernel."""
    errors=[]
    for row in result['rows']:
        for phase in (-103.,0.,47.,132.):
            p=[0,0,1,0,55,0,phase]
            xyz=centers(p,np.array([0,row['index_step']]),row['hand'])
            xyz[:,1:]*=result['observation_radius']/result['minor_radius']
            v=xyz[1]-xyz[0]
            measured=np.degrees(np.arctan2(np.linalg.norm(v[1:]),v[0]))
            errors.append(abs(measured-abs(row['chord_angle_deg'])))
    assert max(errors)<1e-10
    return dict(phase_trials_per_direction=4,comparisons=len(errors),max_chord_error_deg=max(errors))


def torus_points(rope,theta,phi,anchor):
    radius=rope.chain_minor+(rope.bead_radius if anchor=='outward' else 0)
    xyz,_=place_tube_coordinates(theta,phi,rope.chain_major,radius,rope.bead_radius)
    xyz[...,2]-=radius-rope.chain_minor
    return xyz


def torus_ranges(nbeads,anchor):
    """Exact 3D chords vs the centerline tangent halfway between endpoints.

Sample section phase at 0.5-degree intervals. Curvature makes angles depend on
section phase. These ranges describe a supplied generator N, not the photo N.
"""
    rope=Rope(nbeads);phi=np.arange(0.,360.,.5)
    result=[]
    for hand in (1,-1):
        for j in (1,6,7):
            theta=360*j/nbeads
            a=torus_points(rope,0,phi,anchor)
            b=torus_points(rope,theta,phi+hand*360*j/rope.exact_beads_per_row,anchor)
            v=b-a
            tangent=np.array([-np.sin(np.radians(theta/2)),np.cos(np.radians(theta/2)),0])
            axial=v@tangent
            transverse=np.linalg.norm(v-axial[:,None]*tangent,axis=1)
            angles=np.degrees(np.arctan2(transverse,axial))
            result.append(dict(hand=hand,index_step=j,min_unsigned_angle_deg=float(angles.min()),
                               max_unsigned_angle_deg=float(angles.max()),
                               index_zero_clock_zero_angle_deg=float(angles[0])))
    return dict(nbeads=nbeads,anchor=anchor,chain_major=rope.chain_major,phase_spacing_deg=.5,
                tangent_definition='Planar centerline tangent at midpoint major angle',rows=result)


def figure(result,path):
    fig,axes=plt.subplots(1,2,figsize=(10,4.4),constrained_layout=True)
    colors={1:'#2868b2',6:'#b35b16',7:'#138044'}
    for ax,hand in zip(axes,(1,-1)):
        ax.axhline(0,color='black',linewidth=1);ax.scatter(0,0,c='black',s=23)
        for row in result['rows']:
            if row['hand']!=hand:continue
            x,y=row['axial'],row['minor_arc'];j=row['index_step']
            ax.annotate('',xy=(x,y),xytext=(0,0),arrowprops=dict(arrowstyle='->',color=colors[j],lw=2))
            ax.text(x+.12,y,f"+{j}: {row['surface_angle_deg']:+.2f}°",color=colors[j],va='center')
            ax.annotate('',xy=(-x,-y),xytext=(0,0),arrowprops=dict(arrowstyle='->',color=colors[j],lw=1,alpha=.35))
        extent=max(abs(row['minor_arc']) for row in result['rows'])+.65
        ax.set_aspect('equal');ax.set_xlim(-3.6,5.4);ax.set_ylim(-extent,extent)
        ax.set_xlabel('Distance along centerline (model units)')
        ax.set_ylabel('Unrolled minor-circle distance (model units)')
        ax.set_title('Source winding h=+1' if hand==1 else 'Opposite winding h=−1')
        ax.grid(alpha=.15)
    fig.suptitle(f"Nominal 6.5 beads per turn — unrolled {result['anchor']} points, radius {result['observation_radius']:.4f}")
    fig.savefig(path,dpi=170);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nbeads',type=int,help='Supplied generator N; omitted means nominal 6.5 beads/turn')
    parser.add_argument('--anchor',choices=('outward','centers'),default='outward')
    parser.add_argument('--output',type=Path,default=ROOT/'photo2/review/r150')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    result=calculate(args.nbeads,args.anchor)
    report=dict(convention='Positive index advance defines positive centerline direction; h=+1 is source row-angle sign; h=-1 reverses row-angle sign',
        surface='Shortest minor arc on unrolled local straight reference tube; signed angles in degrees',
        chord='3D anchor-to-anchor inclination in local straight limit; sign denotes minor-circle side',
        camera='No camera projection or exposure guarantee; outward points need a visibility check',result=result,
        provenance={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'beads.pov',ROOT/'photo2/bead_placement.py',ROOT/'photo2/local_surface_fit.py',Path(__file__)]})
    if args.nbeads is None:
        report['independent_placement_check']=validate_nominal(result)
        figure(result,args.output/('directions.png' if args.anchor=='outward' else 'directions_centers.png'))
        stem='nominal'
    else:
        report['exact_torus_chord_ranges']=torus_ranges(args.nbeads,args.anchor)
        errors=[]
        if args.anchor=='outward':
            for hand in (1,-1):
                rope=Rope(args.nbeads,rclock=.37,helicity=hand)
                for i in (0,1,6,7,13):
                    expected=minor_outward_point(rope,i)
                    actual=torus_points(rope,*rope.coordinates(i),'outward')
                    errors.append(float(np.linalg.norm(expected-actual)))
            assert max(errors)<1e-10
            report['independent_outward_point_check']=dict(comparisons=len(errors),max_position_error=max(errors))
        stem=f'N{args.nbeads}'
    if args.anchor=='centers':stem+='_centers'
    (args.output/(stem+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
