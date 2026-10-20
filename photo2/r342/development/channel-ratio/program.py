"""Separate illumination-tolerant G/R diagnostic; never changes photographic colors."""
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 _,obs,_,_,auth=load();v=read(OUT/'relative-color.json');ex=read(OUT/'experiment.json');truth={o:r['color'] for o,r in auth.items() if o in v and r['color']!='black'};dev={o:c for o,c in ex['development'].items() if c!='black' and o in truth};held={o:c for o,c in ex['heldout'].items() if c!='black'}
 def limits(t):return dict(red_max=max(v[o]['ratio'] for o,c in t.items() if c=='red'),yellow_min=min(v[o]['ratio'] for o,c in t.items() if c=='yellow'))
 def evaluate(t,lim):
  low=min(lim.values());high=max(lim.values());rows=[]
  for o,c in t.items():
   q=v[o]['ratio'];d='red' if q<low else 'yellow' if q>high else 'unknown';rows.append(dict(id=o,color=c,ratio=q,prediction=d,correct=d==c))
  return dict(counts=dict(Counter('abstain' if r['prediction']=='unknown' else 'correct' if r['correct'] else 'wrong' for r in rows)),records=rows)
 lim=limits(dev);full=limits(truth);result=dict(feature='Median of per-pixel green/red ratios in the same fixed9x9 core. Separate from blackness. No color application.',development_limits=lim,development=evaluate(dev,lim),heldout=evaluate(held,lim),all_confirmed_limits=full,all_confirmed_diagnostic=evaluate(truth,full),single_threshold_separates_confirmed=full['red_max']<full['yellow_min'],policy='Overlap defeats a single complete R/Y threshold. No global red/yellow classifier adopted; shadowed examples in overlap abstain. All-maker limits are retrospective diagnostic, not heldout training.')
 save(OUT/'color-diagnostic.json',result)
 fig,ax=plt.subplots(figsize=(9,3.5));
 for j,c in enumerate(['red','yellow']):
  xs=[v[o]['ratio'] for o,t in truth.items() if t==c];ax.scatter(xs,[j]*len(xs),c=c,edgecolors='black',s=35)
  ax.text(min(xs),j+.12,f'{c}: {min(xs):.3f} to {max(xs):.3f}')
 for o in ['R332-R-0147-0142','REC266-P074746','NEW-1519-2976','REC266-P144445']:
  j=['red','yellow'].index(truth[o]);ax.annotate(o,(v[o]['ratio'],j),xytext=(v[o]['ratio']-.13,j+(.36 if o in ['NEW-1519-2976','R332-R-0147-0142'] else -.35)),fontsize=7,arrowprops=dict(arrowstyle='-',color='gray'))
 ax.axvspan(full['yellow_min'],full['red_max'],color='gray',alpha=.25);ax.set(yticks=[0,1],yticklabels=['red','yellow'],xlabel='Median pixel G/R in fixed core',ylim=(-.6,1.6),title='Confirmed colored glass: shadow-tolerant ratio still overlaps');fig.tight_layout();fig.savefig(OUT/'red-yellow-ratios.png',dpi=150);plt.close(fig);print(full,result['heldout']['counts'])
if __name__=='__main__':main()
