"""Whole-circuit curvature, observed neighbor proxies and apparent recovery plots."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from photo2.r297.common import ROOT,read,save
from .analysis import OUT,D,MODELS

def main():
    review=ROOT/'photo2/review/r310';c=read(OUT/'curvature.json.gz');rows=c['positions'];nv=read(OUT/'neighbor-vectors.json.gz')['rows'];rec=read(OUT/'recoveries.json')
    for name in list(MODELS)[:2]:
        r=[r for r in rows if r['model']==name];supported=[r for r in r if r['coherence'] is not None];fig,ax=plt.subplots(2,2,figsize=(12,8),layout='constrained')
        for inside,color in [(True,'#b25247'),(False,'#357baa')]:
            q=[x for x in supported if x['inside']==inside];ax[0,0].scatter([abs(x['curvature_per_unit'])*x['rope_width_units'] for x in q],[100*(1-x['coherence']) for x in q],s=10,c=color,label='inside' if inside else 'outside')
            q=[x for x in r if x['inside']==inside and x['reflection']['n']];ax[0,1].scatter([abs(x['curvature_per_unit'])*x['rope_width_units'] for x in q],[x['reflection']['rms_D'] for x in q],s=10,c=color)
        for step,col in [(1,'#b25247'),(6,'#357baa'),(7,'#298258')]:
            x=[];y=[]
            for q in r:
                n=next((n for n in q['neighbors'] if n['step']==step),None)
                if n:x.append(q['inside_signed_factor']);y.append(n['length_D'])
            ax[1,0].scatter(x,y,s=2,label=f'+{step}',color=col)
        ax[1,1].scatter([q['foreshortening'] for q in supported],[100*(1-q['coherence']) for q in supported],s=9)
        ax[0,0].set(xlabel='|curvature| × rope width',ylabel='Observed interior not on modal owner (%)');ax[0,0].legend();ax[0,1].set(xlabel='|curvature| × rope width',ylabel='Strong reflection RMS / D');ax[1,0].set(xlabel='rho × signed curvature × sin(phase), positive inside',ylabel='Projected model neighbor spacing / D');ax[1,0].legend();ax[1,1].set(xlabel='Axis tangent foreshortening',ylabel='Observed interior not on modal owner (%)')
        fig.suptitle(name+' · descriptive, conditional owners; no fitted correction');fig.savefig(review/f'{name}-curvature.png',dpi=140);plt.close(fig)
    # Directly measured centroid vectors versus full visible-body centroid proxies.
    fig,axs=plt.subplots(1,3,figsize=(14,5),layout='constrained')
    for ax,name in zip(axs,MODELS):
        d=read(OUT/f'{name}-partA.json.gz');ids={d['anchor']['id']}|{f['first_demonstrated_material_inconsistency']['id'] for f in d['findings'].values()};q=[r for r in nv if r['model']==name and set(r['ids'])&ids]
        for r in q:
            a=np.array(r['observed_interior_centroid_vector_px'])/D;b=np.array(r['predicted_visible_centroid_vector_px'])/D;ax.scatter(*a,color='#2a8a67',s=12);ax.plot([a[0],b[0]],[a[1],b[1]],color='#db803d',lw=.7);ax.scatter(*b,color='#496abb',s=12,marker='x')
        ax.set(title=name,xlabel='Image x vector / D',ylabel='Image y vector / D',aspect='equal');ax.grid(alpha=.2)
    fig.suptitle('Green: observed interior-centroid vectors; blue: predicted visible-centroid vectors\nOrange discrepancy is NOT physical center displacement; no verified crochet neighbor IDs');fig.savefig(review/'neighbor-vectors.png',dpi=140);plt.close(fig)
    axis=c['axis_comparison'];fig,axs=plt.subplots(2,1,figsize=(12,6),layout='constrained');axs[0].plot(np.array(axis['photo_parameter'])/D,np.array(axis['displacement_px'])/D);axs[0].set_ylabel('R309–R306 geometric axis distance / D');axs[1].plot(np.array(axis['photo_parameter'])/D,axis['tangent_difference_degrees']);axs[1].set(xlabel='Original stored photo arc / D',ylabel='Axis tangent difference (degrees)');fig.suptitle('Model-to-model differences, not measured photographic error');fig.savefig(review/'axis-comparison.png',dpi=140);plt.close(fig)
    # Add first later small optical displacement and high-coherence markers separately from identity.
    for d in [read(OUT/f'{name}-partA.json.gz') for name in MODELS]:
        for sign in [-1,1]:
            q=sorted([r for r in d['reflections'] if r['strong'] and r['error_px'] is not None and sign*r['distance_px']>0],key=lambda r:abs(r['distance_px']));f=d['findings'][str(sign)];record=next(r for r in rec if r['model']==d['model'] and r['direction']==sign);fig,ax=plt.subplots(figsize=(11,4),layout='constrained');ax.scatter([abs(r['distance_D']) for r in q],[r['error_D'] for r in q],s=10)
            for key,col in [('first_suspected','#d29b12'),('first_demonstrated_material_inconsistency','#c22332')]:
                r=f[key]
                if r:ax.axvline(abs(r['distance_D']),color=col,ls='--',label=key)
            r=record['first_small_strong_reflection_after_mismatch']
            if r:ax.scatter(abs(r['distance_D']),r['error_D'],marker='*',s=100,c='#32a273',label='first later strong error <0.1D; identity still unknown')
            ax.set(xlabel='Outward photographic arc / D',ylabel='Reliable reflection displacement / D',title=f"{d['model']} direction{sign:+d}: later apparent optical recovery");ax.legend(fontsize=7);fig.savefig(review/f"{d['model']}-{sign}-recoveries.png",dpi=130);plt.close(fig)
    extra=['R306-2405-curvature.png','R309-2733-curvature.png','neighbor-vectors.png','axis-comparison.png']+[f'{name}-{sign}-recoveries.png' for name in MODELS for sign in [-1,1]]
    page=review/'index.html';s=page.read_text();s=s.replace('<h2>Curvature and neighbor diagnostics</h2>'+s.split('<h2>Curvature and neighbor diagnostics</h2>')[-1].split('<script src="data.js">')[0],'') if '<h2>Curvature and neighbor diagnostics</h2>' in s else s
    s=s.replace('<script src="data.js">','<h2>Curvature and neighbor diagnostics</h2>'+''.join(f'<p><img src="{f}" alt="{f}" loading="lazy"></p>' for f in extra)+'<script src="data.js">');page.write_text(s)
if __name__=='__main__':main()
