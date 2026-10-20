"""Separate red/yellow hue only, as requested; black remains completely hue-free."""
from common import *
from matplotlib.colors import rgb_to_hsv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
 _,obs,_,rgb,auth=load();variants=read(OUT/'alternatives.json.gz')['offset-core'];rows={}
 for o,m in variants.items():
  a=np.array(m['region_pixels']);h=rgb_to_hsv(rgb[a[:,1],a[:,0]]/255.)[:,0]*360;h=(h+180)%360-180
  # Circular red-origin representation; median tolerates a few bright pixels.
  rows[o]=dict(hue_degrees=float(np.median(h)),pixel_hue_range=[float(h.min()),float(h.max())],region_pixels=m['region_pixels'])
 ex=read(OUT/'experiment.json');truth={o:r['color'] for o,r in auth.items() if o in rows and r['color']!='black'};dev={o:c for o,c in ex['development'].items() if o in truth and c!='black'};held={o:c for o,c in ex['heldout'].items() if c!='black'}
 def limits(t):return dict(red_max=max(rows[o]['hue_degrees'] for o,c in t.items() if c=='red'),yellow_min=min(rows[o]['hue_degrees'] for o,c in t.items() if c=='yellow'))
 def evaluate(t,lim):
  low=min(lim.values());high=max(lim.values());rr=[]
  for o,c in t.items():
   q=rows[o]['hue_degrees'];d='red' if q<low else 'yellow' if q>high else 'unknown';rr.append(dict(id=o,color=c,hue=q,prediction=d,correct=d==c))
  return dict(counts=dict(Counter('abstain' if r['prediction']=='unknown' else 'correct' if r['correct'] else 'wrong' for r in rr)),records=rr)
 lim=limits(dev);full=limits(truth);save(OUT/'hue-measurements.json',rows);result=dict(feature='Circular median HSV hue in degrees, red at0, same fixed9x9 core. Pigment-only hue diagnostic never enters blackness.',development_limits=lim,development=evaluate(dev,lim),heldout=evaluate(held,lim),all_confirmed_limits=full,all_confirmed_diagnostic=evaluate(truth,full),single_threshold_separates=full['red_max']<full['yellow_min'],policy='Development/heldout partitions inherited unchanged. Full-maker envelope is retrospective; no automatic R/Y correction from a motif or hue majority. Uncertain glass ownership still requires abstention. Channel-ratio experiment archived after explicit maker steering; not used for decisions.')
 save(OUT/'hue-diagnostic.json',result);fig,ax=plt.subplots(figsize=(9,3.5))
 for j,c in enumerate(['red','yellow']):
  xs=[rows[o]['hue_degrees'] for o,t in truth.items() if t==c];ax.scatter(xs,[j]*len(xs),c=c,edgecolors='black',s=35);ax.text(min(xs),j+.12,f'{c}: {min(xs):.2f} to {max(xs):.2f} degrees')
 for o in ['R332-R-0147-0142','REC266-P074746','NEW-1519-2976','REC266-P144445']:
  j=['red','yellow'].index(truth[o]);ax.annotate(o,(rows[o]['hue_degrees'],j),xytext=(rows[o]['hue_degrees']-9,j+(.36 if o in ['NEW-1519-2976','R332-R-0147-0142'] else -.35)),fontsize=7,arrowprops=dict(arrowstyle='-',color='gray'))
 if full['red_max']>=full['yellow_min']:ax.axvspan(full['yellow_min'],full['red_max'],color='gray',alpha=.25)
 ax.set(yticks=[0,1],yticklabels=['red','yellow'],xlabel='Median native-pixel hue (degrees)',ylim=(-.6,1.6),title='Confirmed colored glass — hue diagnostic, independent of blackness');fig.tight_layout();fig.savefig(OUT/'red-yellow-hue.png',dpi=150);plt.close(fig);print('Hue',lim,full,'heldout',result['heldout']['counts']);print('New yellows',[(o,rows[o]['hue_degrees']) for o in MAKER if MAKER[o]=='yellow'])
 print('Remaining red observations',[(o,rows[o]['hue_degrees']) for o in ['NEW-1519-2976','R332-R-0037-0040','REC266-P035619','REC266-P100583','R332-R-0125-0118','R332-R-0197-0183']])
if __name__=='__main__':main()
