"""Independent artifact, support-plane, POV-Ray surface and legacy-mode checks."""
import argparse, gzip, hashlib, json, re, subprocess, tempfile
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import label, center_of_mass
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent

def load(p): return json.loads(Path(p).read_text())
def vector(a): return '<'+','.join(str(float(x)) for x in a)+'>'

def pov(scene,out,width=160,height=120,extra=()):
    cmd=['povray','+I'+str(scene),'+O'+str(out),'+L'+str(ROOT),'+L'+str(HERE/'output'),f'+W{width}',f'+H{height}','+FN','-D','-A','-J','+WT2']+list(extra)
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
    return dict(command=cmd,parsed_and_rendered=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=HERE/'output');args=ap.parse_args();out=args.output.resolve()
    config=load(HERE/'config.json');rows=load(out/'beads.json');p=load(ROOT/'photo2/r344/pattern208.json');n=2704;r=config['bead_radius'];h=config['height_ratio']
    text=(out/'beads.inc').read_text();instances=re.findall(r'object \{ GlassBeads\[(\d)\] matrix <([^>]+)> \}',text)
    assert len(rows)==len(instances)==n
    centers=np.array([q['center'] for q in rows]);frames=[]
    for k,(row,instance) in enumerate(zip(rows,instances)):
        matrix=np.array([float(x) for x in instance[1].split(',')]);frame=matrix[:9].reshape(3,3)
        assert row['k']==k and row['residue']==k%208
        assert row['color']==p['provisional_sequence'][k%208] and row['strict']==p['strict_sequence'][k%208]
        assert int(instance[0])=={'R':0,'Y':1,'B':2}[row['color']]
        assert np.max(abs(matrix-np.array(row['matrix'])))<1e-8
        assert np.max(abs(frame@frame.T-np.eye(3)))<1e-10 and abs(np.linalg.det(frame)-1)<1e-10
        assert np.linalg.norm(frame[1]-row['hole_axis'])<1e-10
        frames.append(frame)
    frames=np.array(frames)
    pairs=set(cKDTree(centers).query_pairs(2*r*np.sqrt(1+h*h)))
    contact=load(out/'contacts.json');certs=contact['certificates']
    assert {(x['a'],x['b']) for x in certs}==pairs
    assert contact['nonseparated_pairs']==[]
    minimum=1e9
    for q in certs:
        a,b=q['a'],q['b'];normal=np.array(q['normal']);assert abs(np.linalg.norm(normal)-1)<1e-12
        # Independent support of the convex filled annulus profile: true glass is
        # a subset. Positive separation therefore suffices even across its bore.
        def support(j):
            axial=abs(normal@frames[j,1]);transverse=np.sqrt(max(0,1-axial*axial))
            return r*(.656*transverse+.086*h/.43*axial+.344*np.hypot(transverse,h/.43*axial))
        margin=(centers[b]-centers[a])@normal-support(a)-support(b)
        # Serialized matrix coefficients have 12 significant digits; nearly
        # axial support normals magnify that rounding through a square root.
        assert margin>1e-6 and abs(margin-q['margin'])<1e-5
        minimum=min(minimum,margin)
    # Independent arc integration, sign, closure and camera inverse checks use
    # the public geometry API, never its precomputed validation summaries.
    from photo2.r345.render import Model
    for hand in [-1,1]:
        c=dict(config,helicity=hand);m=Model(c);g=m.geometry(np.arange(n+1));offset=g['centers']-g['line']
        angle=np.unwrap(np.arctan2(np.sum(offset*g['normal'],axis=1),offset[:,2]))
        assert abs((angle[-1]-angle[0])/(2*np.pi)-hand*416)<1e-10
        assert np.linalg.norm(g['centers'][0]-g['centers'][-1])<1e-8
        assert np.linalg.norm(g['axis'][0]-g['axis'][-1])<1e-8
    m=Model(config);projected=m.project(m.inverse(m.image,m.height));assert np.max(abs(projected-m.image))<1e-10
    # Independent dense numerical integration versus the producer's arc table.
    samples=m.raw(np.linspace(0,m.parameters[-1],131073));independent_length=np.linalg.norm(np.diff(samples,axis=0),axis=1).sum()
    assert abs(independent_length-m.length)<1e-5
    u=np.linspace(0,m.parameters[-1],65537);first=m.raw(u,1);second=m.raw(u,2)
    curvature=np.linalg.norm(np.cross(first,second),axis=1)/np.linalg.norm(first,axis=1)**3
    # One near-reference native pair of each recovered A lattice direction.
    graph=json.loads(gzip.open(ROOT/'photo2/r344/graph.json.gz','rt').read());observations={x['id']:x for x in graph['observations']};lookup={tuple(x['ab']):observations[x['id']]['xy'] for x in graph['coordinates']}
    native={0:lookup[(0,0)],6:lookup[(0,1)],7:lookup[(1,0)]};pred=m.project(m.geometry([0,1,6,7])['centers']);v6=pred[2]-pred[0];v7=pred[3]-pred[0]
    assert np.sign(np.linalg.det(np.array([v6,v7])))==np.sign(np.linalg.det(np.array([np.array(native[6])-native[0],np.array(native[7])-native[0]])))
    legacy=[]
    with tempfile.TemporaryDirectory(prefix='r345-verify-') as temp:
        tmp=Path(temp)
        # Actual POV-Ray trace() through the original macro verifies rounded walls
        # and the open axial bore, independently of rendered color/lighting.
        trace=tmp/'shape.csv';scene=tmp/'shape.pov'
        scene.write_text('''#version 3.7;
#declare bead_radius='''+str(r)+''';
#declare hole_size_per_bead_size=.14;
#include "shape.inc"
#declare M=material{texture{pigment{rgb 1}}};
#declare B=bead(M,.8,'''+str(h)+''',1);
#fopen F "'''+str(trace)+'''" write
#for (I,0,100)
 #local X=I*bead_radius/100;
 #local N=<0,0,0>;
 #local Q=trace(B,<X,10,0>,<0,-1,0>,N);
 #write(F,I,",",vstr(3,Q,",",0,14),",",vlength(N),"\\n")
#end
#fclose F
camera{location <0,0,-10> look_at 0}
object{B pigment{rgb 1}}
''')
        pov(scene,tmp/'shape.png',16,16,extra=['+L'+str(out)])
        traced=np.loadtxt(trace,delimiter=',');assert np.all(traced[:14,4]==0) # actual unobstructed bore
        hit=traced[:,4]>0;q=traced[hit,1:4];rr=np.abs(np.hypot(q[:,0],q[:,2])-.57*r)-.086*r;aa=np.abs(q[:,1])/(h/.43)-.086*r
        implicit=np.hypot(np.maximum(rr,0),np.maximum(aa,0))+np.minimum(np.maximum(rr,aa),0)-.344*r
        assert np.max(abs(implicit))<1e-8
        # Rendered marker centroids check actual POV camera coordinates.
        index=np.array([0,208,416,624,832,1040,1248,1456,1664,1872,2080,2288,2496])
        points=centers[index]
        marker=tmp/'markers.pov';marker.write_text('#version 3.7;\nglobal_settings{assumed_gamma 1}\nbackground{rgb 0}\ncamera{orthographic location '+vector(m.eye*10000)+' direction '+vector(-m.eye)+' right '+vector(m.right*2540/m.scale)+' up '+vector(-m.down*3182/m.scale)+'}\n'+''.join('sphere{'+vector(q)+',.55 pigment{rgb 1} finish{ambient 1 diffuse 0}}\n' for q in points))
        pov(marker,tmp/'markers.png',1270,1591)
        im=np.array(Image.open(tmp/'markers.png').convert('RGB'));components,count=label(im[:,:,0]>200);actual=np.array(center_of_mass(im[:,:,0],components,np.arange(1,count+1)))[:,::-1]
        predicted=(m.project(points)+.5)/2-.5;dist=cKDTree(actual).query(predicted)[0];assert count==len(index) and dist.max()<.8
        # Every legacy palette rendered, for both corrected and literal radii.
        montage=Image.new('RGB',(640,240))
        for mode in range(1,9):
            for old in [0,1]:
                png=tmp/f'legacy-{mode}-{old}.png'
                receipt=pov(ROOT/'beads.pov',png,160,120,extra=[f'Declare=bead_pattern={mode}',f'Declare=LegacyRadius={old}'])
                legacy.append(dict(mode=mode,LegacyRadius=old,parsed_and_rendered=receipt['parsed_and_rendered']))
                if not old:
                    small=Image.open(png).convert('RGB');ImageDraw.Draw(small).text((5,5),str(mode),fill='black');montage.paste(small,(((mode-1)%4)*160,((mode-1)//4)*120))
        montage.save(out/'legacy-examples.jpg',quality=95)
    # Preserve former science byte-for-byte: no historical file is read from a
    # recomputed product. Compare all tracked R344 inputs to source commit.
    source=config['source_commit'];paths=subprocess.check_output(['git','ls-tree','-r','--name-only',source,'photo2/r344'],cwd=ROOT,text=True).splitlines()
    for path in paths:
        original=subprocess.check_output(['git','show',source+':'+path],cwd=ROOT)
        assert hashlib.sha256(original).digest()==hashlib.sha256((ROOT/path).read_bytes()).digest()
    result=dict(physical_beads=n,color_repeats=13,matrices=n,filled_support_separation_certificates=len(certs),minimum_margin=minimum,
                independently_integrated_arc_length=independent_length,maximum_axis_curvature=float(curvature.max()),minimum_axis_bending_radius=float(1/curvature.max()),both_helicity_signs_closed_416_turns=True,camera_marker_count=len(index),camera_marker_max_error_render_pixels=float(dist.max()),
                actual_pov_bore_miss_rays=14,actual_pov_surface_hit_rays=int(hit.sum()),maximum_surface_implicit_error=float(abs(implicit).max()),
                legacy_examples=legacy,historical_R344_files_byte_preserved=len(paths),all_checks_passed=True)
    (out/'independent-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
