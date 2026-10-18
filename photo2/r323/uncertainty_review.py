"""Show two retained local hypotheses for automatically selected ambiguities."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageDraw
from photo2.r323.tracker import ROOT,save
from photo2.r323.review import canvas,point,text,COLORS
OUT=ROOT/'photo2/r323/results'
def main():
    g=json.loads((OUT/'graph.json').read_text());op={o['id']:o for o in g['observations']};im=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');cards=[];records=[]
    for e in sorted(g['graph']['unresolved_edges'],key=lambda e:(-e['competing_windows'],-e['supporting_windows'],e['source'])):
        if e['competing_windows']==0:continue
        center=np.mean([op[e['source']]['xy'],op[e['target']]['xy']],axis=0)
        if any(np.linalg.norm(center-r['center'])<85 for r in records):continue
        options=sorted(e['alternatives'],key=lambda a:-len({x[0] for x in a['window_states']}))
        if len(options)<2:continue
        first,second=options[:2];common=set(x[0] for x in first['window_states'])&set(x[0] for x in second['window_states'])
        wi=min(common) if common else None
        refs=[next((x for x in o['window_states'] if x[0]==wi),o['window_states'][0]) for o in (first,second)]
        cx,cy=map(int,center);crop=(max(900,cx-70),max(0,cy-65),min(1900,cx+70),min(700,cy+65));scale=4;raw=canvas(im,crop,scale);panels=[raw]
        descriptions=['Original RGB']
        for oi,(w,h) in enumerate(refs):
            candidate=g['windows'][w]['hypotheses'][h];panel=canvas(im,crop,scale);d=ImageDraw.Draw(panel);a=candidate['assignments'];lookup={tuple(x['ab']):oid for oid,x in a.items()}
            for oid,x in a.items():
                for fi,delta in enumerate([(1,0),(0,1)]):
                    target=lookup.get(tuple(np.array(x['ab'])+delta))
                    if target:d.line([point(op[oid]['xy'],crop,scale),point(op[target]['xy'],crop,scale)],fill=COLORS[fi],width=2)
            for label,oid in zip(['P','Q'],[e['source'],e['target']]):
                p=point(op[oid]['xy'],crop,scale);d.ellipse((p[0]-8,p[1]-8,p[0]+8,p[1]+8),outline='#ffbd58',width=3);text(d,(p[0]+10,p[1]),label,'#ffbd58',18)
            # Display delta in P→Q orientation, regardless of lexicographic export.
            delta=(np.array(a[e['target']]['ab'])-a[e['source']]['ab']).tolist()
            descriptions.append(f'W{w}/H{h}: Δ(P,Q)={delta}; score {candidate["score"]:.3f}')
            panels.append(panel)
        width=sum(p.width for p in panels);row=Image.new('RGB',(width,raw.height+125),'#181818');d=ImageDraw.Draw(row)
        text(d,(8,8),f'{e["source"]} → {e["target"]}: unresolved; consensus {e["consensus"]:.2f} < 0.85',size=21)
        text(d,(8,38),f'{e["supporting_windows"]} supporting windows, {e["competing_windows"]} with a competing relative coordinate; local scores alone do not decide.',size=18)
        x=0
        for panel,desc in zip(panels,descriptions):row.paste(panel,(x,125));text(d,(x+8,82),desc,size=17);x+=panel.width
        cards.append(row);records.append(dict(center=center.tolist(),edge=e,displayed_window_hypotheses=refs,crop=crop))
        if len(cards)==3:break
    result=Image.new('RGB',(max(c.width for c in cards),sum(c.height for c in cards)),'#181818');y=0
    for card in cards:result.paste(card,(0,y));y+=card.height
    result.save(OUT/'uncertainty.png');save(OUT/'uncertainty-examples.json',records)
if __name__=='__main__':main()
