"""Compact native before/after review, intensity-first pixel audit and full viewer."""
import argparse,html,json,csv,time,copy
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
from .common import *
C={'red':'#e34248','yellow':'#efd34b','black':'#202833','?':'#a5b7c7'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);assets=out/'assets';assets.mkdir();t=time.perf_counter();g,obs,co,ids,ab,c,w,b,station=reviewed_dataset('relocated');_,rawobs,*_=raw_dataset();ledger=read(artifact('corrections/ledger.json'));audit=read(artifact('classification/audit.json.gz'));analysis=read(artifact('analysis/analysis.json.gz'));ranked=read(artifact('overlay/ranked-suspects.json.gz'));records={r['id']:r for r in audit['records']};photo=ImageOps.exif_transpose(Image.open(ROOT/'beads-photo-2.jpg')).convert('RGB');rgb=np.array(photo)/255.;changes={r['id']:r for r in ledger['ordinary_color_corrections']+[ledger['location_correction']]};oldcases=read(ROOT/'photo2/r333/review/cases.json');crops=[];panels=[];pixelmeta=[]
    def native(box,name):
        photo.crop(box).save(assets/f'{name}-native.png');crops.append(dict(file=f'assets/{name}-native.png',bbox=box));return photo.crop(box)
    def pixel_panel(o,name):
        r=records[o];sample=r['samples'][1];x,y=np.rint(r['xy']).astype(int);box=[max(0,x-24),max(0,y-24),min(photo.width,x+25),min(photo.height,y+25)];crop=native(box,name);factor=6;canvas=crop.resize((crop.width*factor,crop.height*factor),Image.Resampling.NEAREST);draw=ImageDraw.Draw(canvas)
        for key,color in [('highlight_pixels','#16d9f3'),('body_pixels','#4df95d')]:
            for xx,yy in sample[key]:
                u=(xx-box[0])*factor;v=(yy-box[1])*factor;draw.rectangle((u,v,u+factor-1,v+factor-1),outline=color,width=1)
        for xx,yy in sample['black_test'].get('ring_pixels',[]):
            u=(xx-box[0])*factor;v=(yy-box[1])*factor;draw.rectangle((u+1,v+1,u+factor-2,v+factor-2),outline='#ffc029',width=1)
        canvas.save(assets/f'{name}-pixels.png')
        # Actual native colors, without replacement markers, for both sampled
        # and excluded pixels. These are pixel evidence swatches, not fake photos.
        for key,suffix in [('body_pixels','body'),('highlight_pixels','reflection')]:
            points=np.array(sample[key],int);tile=Image.new('RGB',(240,120),'#f0f3f5');dd=ImageDraw.Draw(tile)
            for j,(xx,yy) in enumerate(points[:450]):
                a=(j%30)*8;bb=(j//30)*8;dd.rectangle((a,bb,a+7,bb+7),fill=photo.getpixel((int(xx),int(yy))))
            tile.save(assets/f'{name}-{suffix}-swatch.png')
        import matplotlib
        matplotlib.use('Agg');import matplotlib.pyplot as plt
        fig,axes=plt.subplots(1,2,figsize=(9,3.4));colors=[('#222c37',o)]
        references=r['lighting']['ids'][:3]
        # Prefer one red and one yellow in the same physical lighting context.
        for color in ['red','yellow']:
            ref=next((q for q in r['lighting']['ids'] if obs[q]['color']==color and q!=o),None)
            if ref:colors.append((C[color],ref))
        comparisons=[]
        for color,q in colors:
            qq=records[q]['samples'][1];pp=np.array(qq['black_test'].get('ring_pixels',[]),int)
            if len(pp):
                px=rgb[pp[:,1],pp[:,0]];value=px.max(1);axes[0].hist(value,bins=np.linspace(0,1,26),density=True,histtype='step',color=color,label=q)
            pp=np.array(qq['body_pixels'],int)
            if len(pp):
                px=rgb[pp[:,1],pp[:,0]];axes[1].scatter(px[:,0],px[:,1],s=4,color=color,alpha=.25,label=q)
            if q!=o:comparisons.append(dict(id=q,xy=obs[q]['xy'],color=obs[q]['color'],section=int(b[ids.index(q)]) if q in ids else None))
        axes[0].axvline(.35,color='#f59c00',linestyle='--',label='dark-fraction cutoff');axes[0].set(xlabel='Max RGB channel, outside reflection',ylabel='Density',title='Black-first intensity evidence');axes[1].set(xlabel='Red body channel',ylabel='Green body channel',title='Red/yellow calculation after not-black');axes[0].legend(fontsize=6);axes[1].legend(fontsize=6);fig.tight_layout();fig.savefig(assets/f'{name}-distribution.png',dpi=130);plt.close(fig)
        meta=dict(id=o,name=name,bbox=box,black_decision=r['black_test']['decision'],classifier_prediction=r['body_prediction'],body_count=sample.get('body_count',0),excluded_highlight_count=len(sample['highlight_pixels']),annulus=sample['black_test'],lighting=r['lighting'],comparisons=comparisons,abstention_reasons=r['abstention_reasons']);pixelmeta.append(meta);return meta
    # Every maker reference uses the EXACT historical asset and local-ID key.
    for j,change in enumerate(ledger['ordinary_color_corrections']+[ledger['location_correction']]):
        ref=change['references'][0];case=next(x for x in oldcases if x['name']==ref['case']);panel=case if ref['panel_type']=='target' else next(x for x in case['examples'] if x['asset']==ref['asset']);asset=ref['asset'];box=next(x['bbox'] for x in read(ROOT/'photo2/r333/review/native-crops.json') if x['file']==f'assets/{asset}-native.png');before=native(box,f'correction-{j+1:02}');scale=3;image=before.resize((before.width*scale,before.height*scale));draw=ImageDraw.Draw(image);font=ImageFont.truetype(FONT,17);key=copy.deepcopy(panel['key']);number={r['id']:r['number'] for r in key}
        if change['id']=='R332-R-0025-0023':
            yellow=ledger['location_correction']['yellow_body']['id'];number[yellow]=max(number.values())+1;key.append(dict(number=number[yellow],id=yellow,color='yellow',xy=obs[yellow]['xy'],ab=None))
        def point(xy):return tuple((xy[d]-box[d])*scale for d in range(2))
        for e in g['edges']:
            if e['source'] in number and e['target'] in number:draw.line([point(obs[e['source']]['xy']),point(obs[e['target']]['xy'])],fill='#8da8b3',width=1)
        for oid,num in number.items():
            xy=obs[oid]['xy'];xx,yy=point(xy);col=C[obs[oid]['color']];draw.ellipse((xx-7,yy-7,xx+7,yy+7),outline=col if obs[oid]['color']!='black' else '#d8f3ff',width=2);draw.text((xx+7,yy-20),str(num),font=font,fill='white',stroke_width=2,stroke_fill='#142332')
            if oid in changes:draw.rectangle((xx-10,yy-10,xx+10,yy+10),outline='#1ce3b1',width=2)
        xx,yy=point(change['corrected_xy']);draw.rectangle((xx-14,yy-14,xx+14,yy+14),outline='#18edb0',width=3)
        if change['id']=='R332-R-0025-0023':
            u,v=point(change['original_xy']);draw.line([(u-9,v-9),(u+9,v+9)],fill='#ff52d1',width=3);draw.line([(u+9,v-9),(u-9,v+9)],fill='#ff52d1',width=3);draw.line([(u,v),(xx,yy)],fill='#ff52d1',width=2);draw.text((u-35,v-30),'old 27',font=font,fill='white',stroke_width=2,stroke_fill='#142332')
        draw.text((8,8),f'{change["id"]}: maker-reviewed black',font=font,fill='white',stroke_width=2,stroke_fill='black');image.save(assets/f'correction-{j+1:02}-after.png')
        # Reuse the exact R333 diagram geometry/numbering, replace ONLY reviewed
        # colors; image-location change has no a/b effect. Yellow unindexed is
        # explicitly stated rather than drawn at a fabricated lattice site.
        import xml.etree.ElementTree as ET
        tree=ET.parse(ROOT/'photo2/r333/review/assets'/f'{asset}-lattice.svg');root=tree.getroot();ns={'s':'http://www.w3.org/2000/svg'}
        for circ in root.findall('s:circle',ns):
            title=circ.find('s:title',ns)
            if title is not None:
                oid=title.text.split(' ')[0]
                if oid in obs:circ.set('fill',C[obs[oid]['color']])
        for txt in root.findall('s:text',ns):
            if txt.get('y')=='20':txt.text='Maker-reviewed colors; same local numbers and lattice coordinates'
        tree.write(assets/f'correction-{j+1:02}-after-lattice.svg',encoding='unicode')
        pixel=pixel_panel(change['id'],f'pixel-maker-{j+1:02}');panels.append(dict(id=change['id'],reference=ref,name=f'correction-{j+1:02}',historical_asset=asset,key=key,mechanism=change['mechanism'],before_color=change['original_color'],after_color=change['corrected_color'],before_xy=change['original_xy'],after_xy=change['corrected_xy'],pixel=pixel))
    # A small ranked selection illustrates provisional errors without presenting
    # each automatic candidate as a required human decision.
    candidates=[r for r in ranked if r['status']=='recorded' and r['strong_provisional']][:6]
    for j,row in enumerate(candidates):pixel_panel(row['id'],f'pixel-candidate-{j+1:02}')
    # Include an explicit original-location sample for the misplaced yellow marker.
    from .classify import BodyAudit
    engine=BodyAudit(g,obs,co);old=ledger['location_correction'];oldsample=engine.sample(old['original_xy'],12,old['id']);save(out/'misplaced-old-sample.json',oldsample)
    # Full offline viewer data: original/maker layers, exact existing maps, body
    # samples and annular black test. Automatic corrections remain opt-in rings.
    rawviewer=json.loads((ROOT/'photo2/r333/review/data.js').read_text().split('=',1)[1].rstrip(';\n'));nodes=rawviewer['nodes'];lookup={r['id']:r for r in audit['records']}
    for node in nodes:
        o=node['id'];raw=rawobs.get(o);new=obs.get(o)
        if raw:node.update(raw_color=raw['color'],raw_xy=raw['xy'],color=(new or raw)['color'],xy=(new or raw)['xy'],maker_color=(new or raw)['color'],maker_xy=(new or raw)['xy'],maker_reference=changes.get(o))
        if o in lookup:
            row=lookup[o];node.update(body_audit={k:v for k,v in row.items() if k not in ['samples','votes']},body_sample=row['samples'][1],hypothesis=row['body_prediction'] if row['strong_provisional'] else None)
    layerdata={}
    for layer in ['raw','color','relocated','provisional']:
        gg,oo,*_=reviewed_dataset(layer);layerdata[layer]=dict(coverage=next(x['regular_coverage'] for x in analysis['layers'] if x['layer']==layer),colors={o:r['color'] for o,r in oo.items()},locations={o:r['xy'] for o,r in oo.items()},greedy=read(artifact(f'analysis/{layer}/spirals/spirals.json.gz'))['segments'],traces=read(artifact(f'analysis/{layer}/staircases/staircases.json.gz'))['traces'])
    rawviewer.update(nodes=nodes,layers=layerdata,traces=layerdata['relocated']['traces'],greedy=layerdata['relocated']['greedy'],gaps=[],endpoints=[],maker_panels=panels,summary=audit['counts'],spatial_coverage=next(x['regular_coverage'] for x in analysis['layers'] if x['layer']=='relocated'))
    (out/'data.js').write_text('window.R334='+json.dumps(rawviewer,separators=(',',':'))+';\n');save(out/'native-crops.json',crops);save(out/'panels.json',panels);save(out/'pixel-panels.json',pixelmeta)
    sections=[]
    for p in panels:
        ref=p['reference'];name=p['name'];a=p['historical_asset'];pixel=p['pixel'];key=' · '.join(f'{r["number"]}: {r["id"]} ({r["color"]}; {r["xy"]}; {r["ab"]})' for r in p['key']);special=' Yellow C-2058-0820 remains a separate unindexed observation; the magenta cross is old27 and the green box is its new black-body support.' if p['id']=='R332-R-0025-0023' else ' Measured support and lattice association stay fixed.'
        sections.append(f'<section id="{name}"><h2>{p["id"]}</h2><p><strong>{ref["photograph_identifier"]} / {ref["panel_type"]} panel / local feature {ref["local_number"]}</strong>. {p["before_color"]} → {p["after_color"]}. {html.escape(p["mechanism"])}.{special} <button class="jump" data-id="{p["id"]}">Inspect</button></p><div class="pair"><figure><img src="../../r333/review/assets/{a}-annotated.png" alt="Exact original R333 numbered photograph"><img src="../../r333/review/assets/{a}-lattice.svg" alt="Exact original R333 color adjacency diagram"><figcaption>Original R333 photo and its own local diagram/key.</figcaption></figure><figure><img src="assets/{name}-after.png" alt="Same native photograph with maker-reviewed overlay"><img src="assets/{name}-after-lattice.svg" alt="Same lattice coordinates with maker-reviewed colors"><figcaption>Maker overlay on identical native pixels. <a href="assets/{name}-native.png">Literal native crop</a>. Green boxes are reviewed corrections.</figcaption></figure></div><details><summary>Exact local-number / stable-ID / original-coordinate key</summary>{html.escape(key)}</details><div class="pair"><figure><img src="assets/{pixel["name"]}-pixels.png" alt="Specular exclusions, black-test annulus and later body samples"><figcaption>Cyan: excluded reflection; amber: immediately outside-reflection intensity test; green: later red/yellow body samples. Classifier: {pixel["classifier_prediction"]}; first test: {pixel["black_decision"]}. Maker correction stands independently.</figcaption></figure><figure><img src="assets/{pixel["name"]}-distribution.png" alt="Native intensity distributions and nearby colored controls"><figcaption>Left: hue-free intensity outside the reflection. Right: separate body chromatic evidence for red/yellow only. Nearby comparison IDs: {html.escape(str(pixel["comparisons"]))}.</figcaption></figure></div><details><summary>Used/excluded pixel counts and black-first test</summary>{html.escape(str(pixel))}</details></section>')
    candidatehtml=[]
    for j,row in enumerate(candidates):
        name=f'pixel-candidate-{j+1:02}';candidatehtml.append(f'<figure><h3>{row["id"]} — provisional</h3><img src="assets/{name}-pixels.png" alt="Additional candidate pixel samples"><p>Recorded {row["overlay_color"]}; body test {row["body_prediction"]}. Working degree {row["working_degree"]}; separate spatial expectation {row["R333_spatial_expectation"]}. <button class="jump" data-id="{row["id"]}">Inspect</button></p></figure>')
    # Compact before/after summary anchors every claim to a machine-readable layer.
    table=''.join(f'<tr><td>{r["layer"]}</td><td>{len(r["breaks"])}</td><td>{len(r["resolved_R333_breaks"])}</td><td>{r["regular_coverage"]["repeated_supported_segments"]}</td><td>{r["regular_coverage"]["repeated_supported_observations"]}</td></tr>' for r in analysis['layers'])
    shell=(ROOT/'photo2/r333/review/index.html').read_text().split('<main>')[0];shell=shell.replace('R333','R334').replace('Spirals on graph paper','Maker review and body evidence').replace('Measured colors and links, repeated staircase structures, reversible error hypotheses.','Seven confirmed color corrections, one corrected body association, and an intensity-first black test.')
    start=shell.index('<p><a href="../../R334_REPORT.md">');end=shell.index('</p>',start)
    shell=shell[:start]+'<p><a href="../../R334_REPORT.md">Report</a> · <a href="../../R334_REPRODUCE.md">Reproduce</a> · <a href="../overlay/maker-corrections.csv">Exact maker mappings</a> · <a href="../overlay/ranked-suspects.csv">Ranked provisional suspects</a> · <a href="../verification.json">Independent checks</a> · <a href="#corrections">Before/after corrections</a> · <a href="#classification">Pixel audit</a></p>'+shell[end+4:]
    start=shell.index('<p class="notice">');end=shell.index('</p>',start);shell=shell[:start]+'<p class="notice">Black is tested FIRST from very dark intensity immediately outside the reflection. No hue enters that decision. Only a not-black decision opens the red/yellow calculation. Maker corrections are authoritative; automatic suggestions remain provisional. All markers are measured supports, never bead centers.</p>'+shell[end+4:]
    shell=shell.replace('<label><input id="hypotheses" type="checkbox">Color hypotheses (rings)</label>','<label><input id="hypotheses" type="checkbox">Provisional color rings</label><label><input id="body-pixels" type="checkbox">Selected body samples</label><label><input id="reflection-pixels" type="checkbox">Excluded reflection</label><label><input id="annulus-pixels" type="checkbox">Black-test annulus</label>')
    shell=shell.replace('<label>Map <select id="map"></select></label>', '<label>Layer <select id="layer"><option value="raw">Original R333</option><option value="color">Seven color corrections only</option><option value="relocated" selected>Maker corrections + relocation</option><option value="provisional">Provisional auto experiment</option></select></label><label>Map <select id="map"></select></label>')
    body='<main><div id="views"><div><h2>Native photograph</h2><canvas id="photo"></canvas></div><div><h2>Corrected lattice <span id="axis-label"></span></h2><canvas id="lattice"></canvas></div></div><p id="status"></p><aside id="info">Select a stable ID to inspect maker provenance and exact used/excluded pixels.</aside><section><h2>Matched spiral comparison</h2><table><thead><tr><th>Layer</th><th>Relearned breaks</th><th>Original19 resolved</th><th>Repeated traces</th><th>Repeated-support observations</th></tr></thead><tbody>'+table+'</tbody></table><p>All layers share1041 IDs,2285 links, lattice coordinates, R333 weights and geographic folds. The relocation moves one image support and changes its body association; no lattice index changes.</p></section><section id="corrections"><h2>Maker-reviewed corrections and exact panel references</h2>'+''.join(sections)+'</section><section id="classification"><h2>Additional classification candidates — unconfirmed</h2><p>All1600 recorded/provisional/native candidate supports were scanned, including65 provisional black groups. Intensity-only darkness can still confuse shaded red or a seam with black glass. These examples are hypotheses, not accepted edits. The full ranking and abstentions are exported.</p><div class="pair">'+''.join(candidatehtml)+'</div></section><section><h2>Remaining structural ambiguity</h2><p>Use the layer selector to compare resolved and remaining breaks. The report tests every200–399 repeat, both A/B conventions, saved coherent maps and repeat-derived stripe changes. A stripe compression can improve a maker-compatible periodic fit while violating measured links; rejected transformations remain separate diagnostics.</p></section></main><script src="data.js"></script><script src="viewer.js"></script></html>'
    (out/'index.html').write_text(shell+body);(out/'style.css').write_text((ROOT/'photo2/r333/review/style.css').read_text()+'\ntable{border-collapse:collapse;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #bdd0de}#info canvas{max-width:100%}\n')
    js=(ROOT/'photo2/r333/review/viewer.js').read_text().replace('window.R333','window.R334').replace('R333_STATE','R334_STATE').replace('R333_VIEW','R334_VIEW')
    # Viewer data map is named R332 because its unchanged lattice is R332's;
    # data namespace is R334. Retain map identity to preserve source semantics.
    hook="if(on('breaks')&&$('map').value==='R332')for(const g of D.gaps)"
    pixeljs="""if(v.id==='photo'&&selected){const sample=selected.body_sample;if(sample){for(const [toggle,key,col] of [['body-pixels','body_pixels','#38ff6caa'],['reflection-pixels','highlight_pixels','#16dff0aa'],['annulus-pixels',null,'#ffae27bb']]){if(!on(toggle))continue;const pixels=key?sample[key]:(sample.black_test?.ring_pixels??[]);ctx.fillStyle=col;for(const [x,y] of pixels??[])ctx.fillRect(x,y,1,1)}}}
 """
    assert hook in js;js=js.replace(hook,pixeljs+hook)
    js=js.replace("reasons:n.reasons},null,2)", "reasons:n.reasons,maker_review:n.maker_reference,body_classifier:n.body_audit},null,2)")
    js=js.replace("window.R334_VIEW={select", "$('layer').onchange=()=>{const layer=D.layers[$('layer').value];for(const n of D.nodes){if(layer.colors[n.id])n.color=layer.colors[n.id];if(layer.locations[n.id])n.xy=layer.locations[n.id]}D.traces=layer.traces;D.greedy=layer.greedy;D.spatial_coverage=layer.coverage;if(selected)select(selected,false);else update()};window.R334_VIEW={select")
    (out/'viewer.js').write_text(js);save(out/'generation.json',dict(seconds=time.perf_counter()-t,literal_crops=len(crops),maker_panels=len(panels),pixel_panels=len(pixelmeta)));print('REVIEW',len(panels),'maker panels',len(pixelmeta),'pixel panels',flush=True)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);a=ap.parse_args();run(a.output)
