"""Build complete human-readable numerical tables and R266 decision ledger."""
import csv,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from .audit_r267 import OUT,ROOT,METRICS,save,csvsave,inside,photo,map_image,FONT
from .compare_r267 import rows_for

def main():
    manifest=json.loads((OUT/'manifest.json').read_text());statuses=json.loads((OUT/'r266-statuses.json').read_text());rgb=photo();ledger=[];checks=[]
    for name,summary in manifest['summaries'].items():
        rows=rows_for(name);byid={r['plateau_id']:r for r in rows};box=summary['box']
        lines=[f'# {name}: every native maximum pixel','', 'Numbers identify pixels, P IDs identify equal-V maximum plateaus; neither identifies a bead. H is degrees, S is 0–1, brightness/prominence are 8-bit DN. Means use all pixels, including any background in the window. Rankings, six saved statuses and unrounded measurements are in the CSV/JSON files.','',f'[Photograph](./{name}-original.png) · [All numbered maxima, 7×7](./{name}-all-square7.png) · [Complete CSV](./{name}-all-maximum-pixels.csv)','', '| # | Plateau | (x,y) | V | Prom. | H | S | 5×5 | 7×7 | 9×9 | r2 | r3 | r4 | selected12 status / reason |','|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
        for r in rows:
            reason=r['old12_status']+': '+r['old12_reason']
            if r['old12_suppressed_by']:reason+=' → '+r['old12_suppressed_by']
            if r.get('old12_stale_reason')=='True':reason+=' [stale reason; actually retained]'
            lines.append('| '+ ' | '.join([str(r['number']),r['plateau_id'],f"({r['x']},{r['y']})",str(r['peak_v']),str(r['prominence_dn']),f"{float(r['h_deg']):.1f}",f"{float(r['s']):.3f}"]+[f'{r[k]:.2f}' for k in METRICS]+[reason])+' |')
        (OUT/f'{name}-TABLE.md').write_text('\n'.join(lines)+'\n')
        for run,snaps in statuses.items():
            threshold=int(run.split('selected')[-1])
            for pid,r in byid.items():
                s=snaps[pid]
                assert (r['prominence_dn']>=threshold)==s['meaningful'],(pid,run,r['prominence_dn'],s)
                checks.append((name,run,pid))
                if s['status']!='retained' or not inside(*s['peak'],box):continue
                q=s['score'];terms=[.04*q['brightness_dn'],.08*min(q['prominence_lower_bound_dn'],60),.20*q['neighborhood_median_dn'],.25*q['neighborhood_p25_dn'],.04*min(s['pixel_count'],150),60*q['compactness']]
                assert abs(sum(terms)-q['score'])<1e-9
                losers=[(i,t) for i,t in snaps.items() if t['suppressed_by']==pid]
                ledger.append(dict(crop=name,run=run,id=pid,seed=s['peak'],display_location=s['location'],score=q['score'],peak_term=terms[0],prominence_term=terms[1],median7_term=terms[2],p25_7_term=terms[3],area_term=terms[4],compactness_term=terms[5],suppressed_ids=[i for i,t in losers],suppressed_scores=[t['score']['score'] for i,t in losers],source_reason=s['reason'],source_reason_stale='inferior' in s['reason'],explanation='Passed prominence, seed/background, support/paper and recovery gates; survived greedy descending mixed-score competition. Suppression only against already chosen eligible winner with accepted direct broad-bright/color bridge; see original associations.'))
            if run in ('straight-0-selected6','straight-0-selected3'):
                pts={tuple(s['peak']) for s in snaps.values() if s['status']=='retained'};display=[r for r in rows if (r['x'],r['y']) in pts]
                map_image(rgb,box,display,'square7',OUT/f'{name}-{run}-seeds.png',f'{name} | R266 {run} seeds',rank_population=len(rows))
    csvsave(OUT/'selected-decision-ledger.csv',ledger);save(OUT/'selected-decision-ledger.json',ledger)
    lines=['# Why each R266 maximum survived','', 'This ledger covers all six saved straight/annular × 12/6/3-DN variants in the two crops. Seeds differ from displayed support coordinates. “Suppressed” IDs are maximum plateaus, not bead identities. Scores are sums of the six terms saved in the CSV. A survivor was eligible and no earlier selected compatible winner suppressed it; eligibility is not proof that its coordinate is good.','', '[Exact score terms and preserved reason strings](selected-decision-ledger.csv) · [All statuses and background evidence](r266-statuses.json) · [Original selected12 association measurements](r266-local-associations.json)','', '| Crop / run | Selected maximum | Seed | Displayed coordinate | Score | Suppressed alternatives (score) |','|---|---|---|---|---:|---|']
    for r in ledger:lines.append(f"| {r['crop']} / {r['run']} | {r['id']} | {r['seed']} | {r['display_location']} | {r['score']:.3f} | "+', '.join(f'{i} ({s:.3f})' for i,s in zip(r['suppressed_ids'],r['suppressed_scores']))+' |')
    (OUT/'SELECTION_EXPLANATIONS.md').write_text('\n'.join(lines)+'\n')
    # Diagnostic photograph of an unsafe cross-neighbor relocation; automatic
    # points copied from pair-control results, never assigned manual identities.
    cs=json.loads((OUT/'coordinate-comparisons.json').read_text());c=next(c for c in cs if c['old_id']=='P129034' and c['metric']=='square7')
    box=manifest['summaries']['R01284']['box'];x0,y0,x1,y1=box;scale=12
    im=Image.new('RGB',((x1-x0)*scale,(y1-y0)*scale+95),'#172028');im.paste(Image.fromarray(rgb[y0:y1,x0:x1]).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.NEAREST),(0,95));draw=ImageDraw.Draw(im);font=ImageFont.truetype(FONT,18)
    draw.text((10,8),'Unsafe direct-compatible relocation: #83 / P129034 -> #67 / P128549',fill='white',font=font)
    draw.text((10,36),'Mean7: 156.80 -> 234.49 DN; 14.87 px; bridge min 158 DN passes old rule.',fill='white',font=font)
    draw.text((10,64),'Both locations remain in evidence. Do not adopt this relocation or merge.',fill='white',font=font)
    points=[]
    for x,y,col in [(c['old_x'],c['old_y'],'#ffffff'),(c['best_x'],c['best_y'],'#00ffff')]:
        xx=(x-x0+.5)*scale;yy=95+(y-y0+.5)*scale;points.append((xx,yy));draw.ellipse((xx-7,yy-7,xx+7,yy+7),outline=col,width=3)
    draw.line((*points[0],*points[1]),fill='#00ffff',width=2);im.save(OUT/'R01284-neighbor-failure.png')
    save(OUT/'table-validation.json',dict(prominence_gate_checks=len(checks),selected_score_checks=len(ledger),stale_retained_reasons=[{k:r[k] for k in ('crop','run','id','source_reason')} for r in ledger if r['source_reason_stale']]))

if __name__=='__main__':main()
