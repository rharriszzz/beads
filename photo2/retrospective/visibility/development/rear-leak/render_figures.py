"""POV-Ray illustrations, not a new reconstruction or inference experiment.

Run from repository root: .venv/bin/python photo2/retrospective/visibility/render_figures.py
Every new diagram is rendered by POV-Ray. Pillow only reads verification pixels.
"""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from math import sin, cos, pi, sqrt
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from photo2.r344.graph_paper import pattern_layout

DATA = json.loads((HERE.parent/'visibility-example-checks.json').read_text())
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
COLORS = dict(R=(.66,.025,.045), Y=(1,.65,.025), B=(.018,.025,.035),
              ink=(.055,.11,.16), muted=(.29,.36,.42), teal=(.01,.40,.43),
              purple=(.38,.15,.59), blue=(.025,.30,.64), pale=(.91,.94,.95),
              white=(1,1,1), gray=(.68,.73,.76))
JOBS = []


def vec(v):
    return '<'+','.join(f'{a:.8f}' for a in v)+'>'


def rgb(color):
    return vec(COLORS.get(color, color))


def flat(color):
    return f'texture {{pigment {{color rgb {rgb(color)}}} finish {{ambient 1 diffuse 0}}}}'


class Scene:
    def __init__(self, name, width, height, pixels=2000):
        self.name, self.width, self.height, self.pixels = name, width, height, pixels
        source = (ROOT/'beads.pov').read_text()
        macro = source[source.index('#macro bead('):source.index('#macro shiny_opaque')]
        self.parts = [f'''#version 3.7;
global_settings {{assumed_gamma 1 max_trace_level 12 ambient_light rgb 1}}
background {{color rgb 1}}
camera {{orthographic location <0,0,200> look_at <0,0,0>
 right x*{width} up y*{height}}}
light_source {{<-120,170,250> color rgb .85}}
light_source {{<120,20,180> color rgb .35 shadowless}}
#declare bead_radius=.95;
#declare hole_size_per_bead_size=.14;
{macro}
''']
        for color in 'RYB':
            self.parts.append(f'''#declare Bead{color}=bead(material{{texture{{
 pigment{{color rgb {rgb(color)}}} finish{{ambient .20 diffuse .72 specular .13 roughness .055}}
}}}},.8,.55,1);
''')

    def add(self, value):
        self.parts.append(value)

    def text(self, content, x, y, size=.52, color='ink', align='left'):
        content = content.replace('\\', '\\\\').replace('"', '\\"')
        obj = f'text {{ttf "{FONT}" "{content}" .002,0 scale {size} {flat(color)}}}'
        self.add(f'#local T={obj};\n')
        shift = '-(min_extent(T).x+max_extent(T).x)/2' if align == 'center' else '-max_extent(T).x' if align == 'right' else '-min_extent(T).x'
        self.add(f'object{{T translate <{shift},0,0> translate <{x},{y},10>}}\n')

    def line(self, x1,y1,x2,y2, color='gray', radius=.018, z=3):
        self.add(f'cylinder{{<{x1},{y1},{z}>,<{x2},{y2},{z}>,{radius} {flat(color)}}}\n')

    def box(self, x1,y1,x2,y2,color='pale',z=-5):
        self.add(f'box{{<{x1},{y1},{z}>,<{x2},{y2},{z+.01}> {flat(color)}}}\n')

    def dot(self,x,y,color,r=.34,z=4,outline=None):
        if outline:
            self.add(f'sphere{{<0,0,0>,1 scale <{r+.07},{r+.07},.025> translate <{x},{y},{z-.03}> {flat(outline)}}}\n')
        self.add(f'sphere{{<0,0,0>,1 scale <{r},{r},.025> translate <{x},{y},{z}> {flat(color)}}}\n')

    def save(self, aa=True):
        scene = HERE/(self.name+'.pov')
        scene.write_text(''.join(self.parts))
        height = round(self.pixels*self.height/self.width)
        command = ['povray', '+I'+str(scene), '+O'+str(scene.with_suffix('.png')),
                   '+W'+str(self.pixels), '+H'+str(height), '+FN', '-D', '-J', '+WT2',
                   '+A0.12', '+AM2', '+R2'] if aa else [
                   'povray', '+I'+str(scene), '+O'+str(scene.with_suffix('.png')),
                   '+W'+str(self.pixels), '+H'+str(height), '+FN', '-D', '-J', '-A', '+WT2']
        JOBS.append((scene, command))


def tube(s, word, x, y, view=0, start=0, count=None, selected=None, ids=False, core=True):
    """Radial-hole opaque beads on a straight ideal helix, neutral opaque interior.

    Tube centers R=2.5; axial step .34. Guard beads extend beyond cropped ends.
    The explicit interior is part of this constructed object, not a recovered pose.
    """
    count = count or len(word)
    bottom, top = y-count*.34/2, y+count*.34/2
    s.add('intersection{ union{\n')
    if core:
        s.add(f'cylinder{{<{x},{bottom-7},0>,<{x},{top+7},0>,1.85 {flat((.60,.53,.40))}}}\n')
    for k in range(start-13, start+count+13):
        theta = 4*pi*k/13-view*pi/180
        st, ct = sin(theta), cos(theta)
        cx, cy, cz = x+2.5*st, y-((k-start)-(count-1)/2)*.34, 2.5*ct
        matrix = [ct,0,-st, st,0,ct, 0,-1,0, cx,cy,cz]
        if ids:
            # Pure blue labels encode k-start+14, red labels encode selected set.
            index = k-start+14
            color = (1,0,0) if selected is not None and k in selected else (0,0,index/255)
            s.add(f'object{{bead(material{{{flat(color)}}},.8,.55,1) matrix {vec(matrix)}}}\n')
        else:
            s.add(f'object{{Bead{word[k % len(word)]} matrix {vec(matrix)}}}\n')
    s.add(f'}} box{{<{x-5},{bottom},-6>,<{x+5},{top},6>}} }}\n')


def legend(s, x, y, size=.45):
    for j,(color,label) in enumerate([('R','red'),('Y','yellow'),('B','black')]):
        s.dot(x+j*3.4,y+.14,color,.20)
        s.text(label,x+.4+j*3.4,y,size)


def adversary():
    s = Scene('01-hidden-patterns', 36, 23, 2400)
    s.text('SAME FRONT. DIFFERENT BACKS.',0,10.1,.82,align='center')
    s.text('Two distinct 26-bead patterns, with identical color totals',0,8.8,.46,'muted','center')
    words = [DATA['pattern_A'], DATA['pattern_B']]
    for j,(word,view,label) in enumerate([(words[0],0,'A - front'),(words[1],0,'B - front'),
                                         (words[0],180,'A - back'),(words[1],180,'B - back')]):
        x = -13.2+j*8.8
        s.box(x-4.15,-4.8,x+4.15,7.4,(.965,.974,.98))
        s.text(label,x,6.25,.63,align='center')
        tube(s,word,x,.8,view)
        s.text('0-25; index increases down',x,-4.1,.30,'muted','center')
    s.text('Front A and B: identical rendered pixels',-8.8,-6.2,.53,'teal','center')
    s.text('Backs reveal the swapped colors',8.8,-6.2,.53,'purple','center')
    s.text('Opaque beads + opaque thread interior; cropped tube continues beyond the frame.',0,-8,.40,'muted','center')
    legend(s,-4.5,-9.7)
    s.save()
    # Same cameras/geometry/lights as the illustration, without text or labels.
    for name,word in [('front-A',words[0]),('front-B',words[1]),('back-A',words[0]),('back-B',words[1])]:
        t = Scene('check-'+name, 8, 26*.34, 640)
        tube(t,word,0,0,180 if name.startswith('back') else 0)
        t.save(aa=False)
    t = Scene('check-hidden-ownership', 8, 26*.34, 640)
    tube(t,words[0],0,0,selected={4,17},ids=True)
    t.save(aa=False)


def phase_shift():
    # End-on sections isolate material-frame phase without showing inaccessible
    # pigments as observations. Solid black target disk, ring for the tube outline.
    s = Scene('02-phase-shift', 36, 20, 2400)
    s.text('ONE EXTRA BEAD CHANGES THE ALIGNMENT',0,8.45,.73,align='center')
    s.text('Track the same black pattern position: p = 3',0,7.25,.48,'muted','center')
    for row,(L,cy) in enumerate([(26,2.9),(27,-3.65)]):
        s.text(f'L = {L}',-17,cy+1.8,.65,'teal' if L==27 else 'ink')
        for j in range(4):
            x=-10.3+j*7.8
            # Cross-section: front up; x/sin, y/cos, observer above diagram.
            s.add(f'torus{{2,.027 rotate <90,0,0> translate <{x},{cy},3> {flat("gray")}}}\n')
            for r in range(13):
                th=4*pi*r/13
                s.dot(x+2*sin(th),cy+2*cos(th),'pale',.13)
            r=(3+j*L)%13;th=4*pi*r/13
            s.dot(x+2*sin(th),cy+2*cos(th),'B',.30,outline='teal' if r in DATA['readable_phases'] else 'muted')
            s.text(f'copy {j}: phase {r}',x,cy-2.95,.40,align='center')
            status='READ' if r in DATA['readable_phases'] else 'edge: skip' if r==5 else 'rear: skip'
            s.text(status,x,cy+2.75,.42,'teal' if status=='READ' else 'muted','center')
    s.text('Front is at the TOP of each end-on diagram. The black disk is a known target,',0,-8.15,.39,'muted','center')
    s.text('not a color measurement through the tube. Phase arithmetic; not an optical image.',0,-9.05,.39,'muted','center')
    s.save()
    # Real ray-traced front visibility of the selected target in successive copies.
    t = Scene('03-phase-shift-tubes',36,22,2400)
    t.text('THE SAME POSITION EVENTUALLY REACHES THE FRONT',0,9.4,.69,align='center')
    t.text('27-bead word; four windows in one continuous, straight ideal tube',0,8.15,.45,'muted','center')
    word=DATA['pattern_27']
    for j in range(4):
        x=-13.2+j*8.8
        t.box(x-4.15,-4.6,x+4.15,6.7,(.965,.974,.98))
        # Window centered on the selected bead; preserve global k/phase.
        tube(t,word,x,.7,start=3+j*27-13,count=27)
        phase=(3+j*27)%13
        t.text(f'copy {j}; phase {phase}',x,5.75,.47,align='center')
        t.line(x-3.85,.7,x-3.15,.7,'teal',.045,z=9)
        t.line(x+3.15,.7,x+3.85,.7,'teal',.045,z=9)
        t.text('clear front' if j==3 else 'not used for color',x,-5.5,.42,'teal' if j==3 else 'muted','center')
    t.text('Teal marks locate the longitudinal level of p=3; they do not point to a visible body.',0,-7,.40,'muted','center')
    t.text('The fourth window exposes the black target without reading an ambiguous edge.',0,-8.25,.44,'teal','center')
    legend(t,-4.5,-9.6)
    t.save()


def middle():
    s=Scene('04-complementary-views',42,32,2520)
    s.text('52 BEADS. THREE VIEWS. NO GUESSED BACK.',0,14.4,.79,align='center')
    s.text('The repeat is a multiple of 13; complementary readings still cover every position.',0,13.05,.45,'muted','center')
    word=DATA['middle_example']['word']
    viewcolors=['teal','purple','blue']
    for j,v in enumerate(DATA['middle_example']['views']):
        x=-14+j*14
        s.box(x-6.1,-8.5,x+6.1,11.8,(.965,.974,.98))
        s.text(f'View {j+1}: {v["view_degrees"]} degrees',x,10.7,.58,viewcolors[j],'center')
        tube(s,word,x,1,view=v['view_degrees'])
        s.text('0',x-3.8,9.2,.40,viewcolors[j])
        s.text('51',x-3.8,-7.7,.40,viewcolors[j])
        # 52-row measurement strip visibly beside tube; only clear mask readings.
        for p in range(52):
            yy=1-((p)-(51)/2)*.34
            if p in v['positions']:
                s.dot(x+4.5,yy,word[p],.13,outline=None)
            else:
                s.dot(x+4.5,yy,'gray',.045)
        s.text(f'{v["count"]} selected readings',x,-9.7,.46,viewcolors[j],'center')
    s.text('Combined indexed word: each color has a source view',0,-11.2,.51,align='center')
    for p,color in enumerate(word):
        x=-19.1+(p%26)*1.53; y=-12.6-(p//26)*1.6
        view=next(j for j,v in enumerate(DATA['middle_example']['views']) if p in v['positions'])
        s.dot(x,y,color,.38,outline=viewcolors[view])
        s.text(str(p),x,y-.93,.32,'muted','center')
    s.save()
    # Flat owner-ID render verifies every phase admitted by each reading mask.
    for j,v in enumerate(DATA['middle_example']['views']):
        t=Scene(f'check-middle-view-{j+1}',8,52*.34,800)
        tube(t,word,0,0,view=v['view_degrees'],ids=True)
        t.save(aa=False)


def graphpaper():
    s=Scene('05-full-pattern',34,49,2040)
    s.text('THE COMPLETE 208-POSITION CANDIDATE',0,22.8,.72,align='center')
    s.text('Alternating 6 / 7 rows; positions 0-207 each shown once',0,21.4,.43,'muted','center')
    s.text('201 supported colors; 7 outlined provisional blacks',0,20.3,.45,'teal','center')
    paper=pattern_layout(DATA['actual_current_strict_sequence'],DATA['actual_candidate_sequence'],
                         extension_rows=0,minimum_rows=32,side_beads=0)
    assert len(paper['points'])==208
    s.box(-12.7,-18.9,12.7,19,(.968,.976,.98))
    for p in paper['points']:
        k=p['k'];x=(p['x']-5)*1.50;y=18-p['y']*1.15
        # Elliptical graph-paper symbols, not a view of physical beads.
        col=DATA['actual_candidate_sequence'][k]
        s.add(f'sphere{{<0,0,0>,1 scale <1.04,.46,.025> translate <{x},{y},4> {flat("blue" if p["tentative"] else "gray")}}}\n')
        s.add(f'sphere{{<0,0,0>,1 scale <.94,.38,.025> translate <{x},{y},4.04> {flat(col)}}}\n')
        s.text(str(k),x,y-.115,.30,'ink' if col=='Y' else 'white','center')
    for row in range(32):
        y=18-row*1.15
        s.text(str(row),-13.5,y-.14,.36,'muted','right')
    # Rows increase upward in mathematical lattice, downward in this readable chart.
    # Up in the chart below means toward increasing row number (page down).
    s.line(-11.5,18.62,11.5,18.62,'teal',.047)
    s.line(-11.5,18-31*1.15-.62,11.5,18-31*1.15-.62,'purple',.047)
    s.text('START 0',12.6,18.5,.34,'teal')
    s.text('END 207',12.6,-18.25,.30,'purple')
    legend(s,-4.5,-20)
    s.text('Blue outline: 43, 75, 82, 89, 140, 147, 186. All seven have observations.',0,-21.7,.35,'muted','center')
    s.text('Page-down row direction; +1 right, +6 down-left, +7 down-right.',0,-22.7,.37,'muted','center')
    s.text('Display convention only. Authentic chart, count and physical topology unverified.',0,-23.7,.35,'muted','center')
    s.save()
    return paper


def coverage():
    s=Scene('06-observation-coverage',108,55,3240)
    s.text('WHY THE 208-BEAD CANDIDATE IS RECOVERABLE IN THIS MAPPING',0,25,.95,align='center')
    s.text('Colored cell = at least one retained observation. Blank = no color observation.',0,22.8,.69,'muted','center')
    s.text('Thirteen occurrence addresses; two panels show positions 0-103 and 104-207.',0,20.9,.65,'muted','center')
    coverage=DATA['actual_coverage'];target=DATA['actual_candidate_sequence']; weak=set(DATA['actual_insufficient_positions'])
    occupied=0
    for panel in range(2):
        ytop=16.8-panel*18
        for row in range(13):
            s.text(str(row),-48.7,ytop-row*.9-.18,.47,'muted','right')
        for i in range(104):
            p=panel*104+i;x=-47.1+i*.91
            if i%13==0:
                s.text(str(p),x,ytop+1.8,.51,'ink','center')
                s.line(x-.44,ytop+.7,x-.44,ytop-11.4,'gray',.012)
            if p in weak:
                s.box(x-.44,ytop-13.55,x+.44,ytop+1.1,(.89,.93,1),z=-4)
            occurrences={o['occurrence'] for o in coverage[str(p)]}
            for row in range(13):
                y=ytop-row*.9
                if row in occurrences:
                    occupied+=1
                    s.box(x-.34,y-.33,x+.34,y+.33,target[p],z=3)
                else:
                    s.box(x-.34,y-.33,x+.34,y+.33,(.96,.97,.975),z=3)
            s.box(x-.34,ytop-12.6-.33,x+.34,ytop-12.6+.33,target[p],z=3)
        s.text('union',-48.7,ytop-12.78,.47,'teal','right')
        s.text(f'positions {panel*104}-{panel*104+103}',49.6,ytop-12.78,.45,'muted','right')
    s.text('All 208 columns have evidence. Blue bands: seven positions with insufficient strict corroboration.',0,-20.3,.63,'muted','center')
    s.text('1040 retained observations; 201 supported / 0 conflicting / 7 insufficient.',0,-22.2,.73,'teal','center')
    s.text('Q1 pigment omitted. Two maker photo-based yellow corrections included. Cells do not count duplicate render copies.',0,-24.05,.58,'muted','center')
    s.text('Conditional indexing; these are source addresses, not thirteen independently photographed complete necklaces.',0,-25.7,.56,'muted','center')
    s.save()
    return occupied


def run(job):
    path,command=job
    with path.with_suffix('.log').open('w') as log:
        subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(path.name,flush=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(paper, occupied):
    a=np.array(Image.open(HERE/'check-front-A.png'))
    b=np.array(Image.open(HERE/'check-front-B.png'))
    backa=np.array(Image.open(HERE/'check-back-A.png'))
    backb=np.array(Image.open(HERE/'check-back-B.png'))
    owner=np.array(Image.open(HERE/'check-hidden-ownership.png'))
    red=(owner[:,:,0]>250)&(owner[:,:,1]<3)&(owner[:,:,2]<3)
    assert np.array_equal(a,b), 'Adversarial colors leak into front image'
    assert not red.any(), 'Changed rear beads have visible front surfaces'
    assert not np.array_equal(backa,backb), 'Backs must distinguish the words'
    views=[]
    for j,v in enumerate(DATA['middle_example']['views']):
        im=np.array(Image.open(HERE/f'check-middle-view-{j+1}.png'))
        counts={p:int(np.sum((im[:,:,0]==0)&(im[:,:,1]==0)&(im[:,:,2]==p+14))) for p in range(52)}
        readable={p:counts[p] for p in v['positions']}
        assert min(readable.values())>30, readable
        views.append(dict(view_degrees=v['view_degrees'],selected_positions=v['positions'],
                          visible_surface_pixels_for_each_selected_body=readable))
    # A conservative enclosing-sphere separation for all beads in this illustrative helix.
    distances=[sqrt((5*sin(2*pi*d/13))**2+(.34*d)**2) for d in range(1,50)]
    bound=.95*sqrt(1+.55**2)
    assert min(distances)>2*bound
    assert sorted(p['k'] for p in paper['points'])==list(range(208))
    assert [p['k'] for p in paper['points'] if p['tentative']]==DATA['actual_insufficient_positions']
    sources={p:sha(ROOT/p) for p in DATA['actual_necklace_input_sha256']}
    assert sources==DATA['actual_necklace_input_sha256']
    result=dict(scope='Constructed illustrations and saved-observation display only; no reconstruction fit.',
                front_render_pixels_compared=int(a.shape[0]*a.shape[1]),front_A_equals_B=True,
                changed_body_front_surface_pixels=int(red.sum()),
                back_differing_pixels=int(np.any(backa!=backb,axis=2).sum()),
                illustrative_helix=dict(radius=2.5,axial_step=.34,bead_radius=.95,bead_height_ratio=.55,
                    opaque_core_radius=1.85,matte_opaque=True,guard_beads_each_end=13,
                    minimum_center_distance=min(distances),enclosing_sphere_diameter=2*bound),
                middle_view_checks=views,graph_paper_positions=208,graph_paper_rows=32,
                graph_paper_row_counts=[sum(p['y']==y for p in paper['points']) for y in range(32)],
                graph_paper_page_down_row_convention=True,
                seven_tentative_positions=DATA['actual_insufficient_positions'],
                occupied_occurrence_position_cells=occupied,retained_observations=1040,
                actual_source_sha256=sources,bead_macro_source_sha256=sha(ROOT/'beads.pov'),
                render_commands=[dict(scene=str(p.relative_to(ROOT)),command=c) for p,c in JOBS],
                figures=[dict(path=str((HERE/f'{i}.png').relative_to(ROOT)),sha256=sha(HERE/f'{i}.png'))
                         for i in ['01-hidden-patterns','02-phase-shift','03-phase-shift-tubes',
                                   '04-complementary-views','05-full-pattern','06-observation-coverage']])
    (HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['middle_view_checks','render_commands','figures']},indent=2))


def main():
    adversary();phase_shift();middle();paper=graphpaper();occupied=coverage()
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(run,JOBS))
    verify(paper,occupied)


if __name__=='__main__':
    main()
