"""Independent POV-Ray check and shared-light appearance of the fitted real-photo crop."""
import subprocess
import numpy as np
from PIL import Image,ImageDraw
from .common import ROOT,OUT,read,save,photo
from .geometry import Scene,R


def vec(v):return '<'+','.join(f'{x:.14g}' for x in v)+'>'


def main():
    p2=read(OUT/'phase2.json');native,_,_=photo();folder=OUT/'pov';folder.mkdir(exist_ok=True)
    text=(ROOT/'beads.pov').read_text();macro=text[text.index('#macro bead('):text.index('#macro shiny_opaque')]
    origin=np.array([483,1500]);w,h=240,200;summary=[]
    for name in (p2['selected_ids'][0],p2['selected_ids'][2]):
        model=read(OUT/(name+'-fit.json'));scene=Scene(p2['curve'],model['parameters'])
        rows=read(OUT/(name+'-inventory.json.gz'))['records'];light=read(OUT/(name+'-light.json'))['direction']
        center=origin+np.array([(w-1)/2,(h-1)/2]);base=((center-scene.offset)/scene.scale)@np.array([scene.right,scene.down])
        for identity in (True,False):
            kind='identity' if identity else 'appearance';stem=name+'-'+kind
            lines=['#version 3.7;','global_settings {assumed_gamma 1.0}',f'#declare bead_radius={R:.16g};',
                   '#declare hole_size_per_bead_size=.14;',macro,
                   f'camera {{orthographic location {vec(base+scene.eye*1000)} direction {vec(-scene.eye)} right {vec(scene.right*w/scene.scale)} up {vec(-scene.down*h/scene.scale)} }}',
                   'background {color rgb 0}' if identity else 'background {color rgb <.36,.18,.30>}',
                   f'light_source {{ {vec(np.array(light)*100000)} color rgb 1 parallel point_at <0,0,0> }}']
            for k,row in enumerate(rows):
                color=[((k+1)%256)/255,((k+1)//256)/255,0] if identity else dict(red=[.65,.015,.02],yellow=[.9,.52,.015],black=[.008,.008,.008],unknown=[.18,.18,.18])[row['color']]
                finish='ambient 1 diffuse 0' if identity else 'ambient .12 diffuse .65 phong .8 phong_size 50'
                matrix=np.r_[scene.g['surface_normal'][k],scene.g['surface_tangent'][k],-scene.g['surface_binormal'][k],scene.centers[k]]
                lines.append('#declare M=material {texture {pigment {color rgb '+vec(color)+'} finish {'+finish+'}}}; object {bead(M,.8,.7,1) matrix '+vec(matrix)+' }')
            path=folder/(stem+'.pov');path.write_text('\n'.join(lines)+'\n')
            command=['povray','+I'+str(path.resolve()),'+O'+str((folder/(stem+'.png')).resolve()),f'+W{w}',f'+H{h}','+FN','-D','-A','+WT2','File_Gamma=1.0']
            run=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(folder/(stem+'.log')).write_bytes(run.stdout)
            if run.returncode:raise RuntimeError(str(path))
        actual=np.array(Image.open(folder/(name+'-identity.png')).convert('RGB'),dtype=int)
        owner=actual[:,:,0]+256*actual[:,:,1]-1;yy,xx=np.indices((h,w));d=scene.trace(np.c_[xx.ravel()+origin[0],yy.ravel()+origin[1]])
        predicted=d['owner'].reshape(h,w);known=~d['unknown'].reshape(h,w)
        # Separately report boundary disagreement, never erase it from the total.
        stable=known.copy()
        for axis in (0,1):
            for delta in (-1,1):stable &= np.roll(owner,delta,axis)==owner
        stable[[0,-1],:]=False;stable[:,[0,-1]]=False
        row=dict(model=name,total_pixels=w*h,known=int(known.sum()),unknown=int((~known).sum()),
                 all_disagreements=int(((owner!=predicted)&known).sum()),interior_pixels=int(stable.sum()),
                 interior_disagreements=int(((owner!=predicted)&stable).sum()))
        summary.append(row)
        canvas=Image.new('RGB',(960,440),(24,29,36));draw=ImageDraw.Draw(canvas)
        raw=Image.fromarray(native).crop((*origin,*(origin+[w,h])))
        render=Image.open(folder/(name+'-appearance.png'))
        for i,(im,title) in enumerate(((raw,'Real photograph'),(render,'Conditional image colors; one shared light'))):
            canvas.paste(im.resize((480,400),Image.Resampling.NEAREST),(i*480,30));draw.text((i*480+8,8),title,fill='white')
        canvas.save(ROOT/'photo2/review/r282'/(name+'-pov.png'))
    save(folder/'validation.json',dict(cases=summary,claim='POV/Python numerical geometry check, not photographic model accuracy; appearance uses conditional colors and one shared light.'))
    print(summary)


if __name__=='__main__':main()
