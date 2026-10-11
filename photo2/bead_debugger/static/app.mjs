import {toSource,toScreen,zoomAt,fitView,resizeView,RequestGate} from '/viewport.mjs';
import {wrap,indexOf,generatorOf,triple,reviewedSet,nextUnchecked,nearest,labelAllowed} from '/logic.mjs';
const $=id=>document.getElementById(id),ctx=$('photoCanvas').getContext('2d');
const colors={red:'#ff5b68',yellow:'#ffe954','black?':'#c7d4eb',unknown:'#c1c7d2'};
const specs=[
 ['photo','A · Original photograph','#ffffff',true,'Unmodified native pixels; integer x/y locate pixel centers.'],
 ['inner','B · Inner spline','#79ed9c',true,'Regenerated historical HSV algorithm; possible shadow bias.'],
 ['outer','B · Outer spline','#ffa95c',true,'Regenerated historical HSV algorithm.'],
 ['centerline','B · Image-derived centerline','#43e7f1',true,'Boundary midpoint → periodic cubic, 2px smoothing target.'],
 ['midpoint','B · Raw boundary midpoints','#b7fafa',false,'Before the periodic cubic refinement.'],
 ['tangents','B · Tangents / normals / sections','#f0f3fa',false,'Image spline tangent and ±50px normal guides, not measured boundaries.'],
 ['registered','B · Registered model centerline','#7698ff',false,'Legacy geometry guide; distinct from image tracing.'],
 ['archived','B · Archived spline comparison','#ee75fa',false,'Regression reference only; never used by the new generator.'],
 ['interiors','C · Independent color interiors','#ffea60',true,'Separate positive interiors; not certified bead identities.'],
 ['ambiguous','C · Ambiguous / small patches','#ed99f2',true,'Dashed rings: uncertain split or small patch.'],
 ['rejected','C · Rejected tiny proposals','#8a91a0',false,'Crosses; retained for coverage and detector debugging.'],
 ['black','C · Reflection + dark body candidates','#d5e2f4',false,'Reflection coordinates; black identity unconfirmed.'],
 ['patches','C · Positive interior support pixels','#fcfa8d',false,'Colored pixels only; no dark seam ownership assigned.'],
 ['legacy','D · R200 / R252 & maker marks','#e69cff',false,'LEGACY-ASSISTED comparison, disabled by default.'],
 ['legacyWithheld','D · Historical withheld proposals','#b087bd',false,'R252 ambiguous/provisional/rejected records; disabled by default.'],
 ['centers','E · Computed bead centers','#82b6ff',true,'All string indices, including hidden geometry.'],
 ['outward','E · Coarse minor-outward points','#ffa769',false,'Geometric points, not photographed highlights.'],
 ['surfaces','E · Visible surface footprints','#75b2d8',false,'Exact rounded-annulus ray ownership on a 4px grid.'],
 ['centroids','E · Coarse 4px centroids','#a9c6f2',false,'Geometric visible-area centroid, not colored interior.'],
 ['nativeCenter','E2 · Selected physical center','#82b6ff',false,'Blue ring: projected physical 3D center, including hidden beads.'],
 ['nativeSurface','E2 · Native owned pixels','#73b9df',false,'Selected ±1/6/7 neighborhood, first hit at 1px. Each owner has a distinct tint.'],
 ['nativeOutward','E2 · Audited radial extremum','#ffa769',false,'Orange × visible; gray × occluded. Representative of the outer cylindrical band.'],
 ['nativeCentroid','E2 · Native visible area centroid','#68ff95',false,'Green dot: boundary-adaptive projected area centroid; absent without reliable pixels.'],
 ['highlightPoint','E2 · Predicted highlight location','#ff72e3',false,'Pink cross: intensity centroid, conditional global illumination; never an observed reflection.'],
 ['highlightRegion','E2 · Predicted highlight region','#ec5ae4',false,'Relative specular intensity at 1px on owned surfaces; global model and roughness.'],
 ['observedReflection','E2 · Observed photo reflections','#ffffff',false,'White rings: independent bright-on-dark photo candidates; larger ring for reliable candidates.'],
 ['shadowDiagnostic','E2 · Shadow diagnostics','#aa73ef',false,'Purple = modeled cast shadow; orange = observed paper darkness (ambiguous). Back-facing pixels are yellow.'],
 ['neighbors','F · ±1 / ±6 / ±7 vectors','#ffffff',true,'1 white, 6 cyan, 7 orange; conditional on selected model/hand.'],
 ['triples','G · Algebraic coordinate triples','#bbc8ff',false,'(n1,n6,n7), k ≡ n1+6n6+7n7 mod N; NOT observed walks.'],
 ['indices','H · Conditional string indices','#e4f2ff',true,'Dense labels only when zoomed; collision culled.'],
 ['generator','H · Generator indices','#a5c0d6',false,'Original source-loop index, separate from review origin.'],
 ['correspondence','I · Interior → surface owner','#79efd5',false,'Model-conditional links; alternatives in Inspect.'],
 ['fft','J · FFT frequency directions','#d294ff',false,'Saved R250 tangent-relative frequency axes, not bead-neighbor vectors.'],
 ['pattern','K · Rejected template residue colors','#e9a1fb',false,'Proposed R/Y, conflict !, unknown ?; never recolors the photograph.'],
 ['corrections','L · Stretch / twist displacement','#ffb668',false,'Model longitudinal correction vectors; full parameters in Diagnostics.']
];
const defaults=Object.fromEntries(specs.map(s=>[s[0],s[3]]));
let layers={...defaults},opacity=.85,boot,model,inventory,obsMap,reviews,legacy=[],fft=null,archived=null;
let view={x:0,y:0,scale:1},size={width:1,height:1},gi=0,oid=null,originId='legacy',clicked=null,ready=false,pendingFrame=false,renderStats={},modelGate=new RequestGate();
let detail=null,lightingDoc=null,lightID=null,detailToken=0,detailTimer;
let saveChain=Promise.resolve(),sessionTimer,photo=new Image(),drawCount=0;
const modelCache=new Map(),drafts=new Map();
const status=(s,error=false)=>{$('status').textContent=s;$('status').classList.toggle('error',error);};
async function api(path,body){const r=await fetch(path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok){let d=await r.json();throw new Error(d.error||r.statusText);}return r.headers.get('Content-Type').includes('zip')?r.blob():r.json();}
function guard(fn){return (...args)=>Promise.resolve().then(()=>fn(...args)).catch(e=>{status(e.message,true);console.error(e);});}
function origin(){return reviews?.origins.find(r=>r.id===originId&&r.model_version===model?.version)?.generator_index??model?.origin??0;}
function kOf(i){return indexOf(i,origin(),model.n);}
function selected(){return model.beads[gi];}
function selectedPoint(){const o=obsMap?.get(oid);return o?[o.x,o.y]:selected().center;}
function draftKey(){return `${boot.manifest.generation_id}:${model.version}:${gi}`;}
function currentDraft(){return {updated_at:Date.now(),note:$('note').value,action:$('action').value,alternative:$('alternative').value,clicked};}
function stashDraft(){if(!ready)return;drafts.set(draftKey(),currentDraft());try{localStorage.setItem('bead-debugger-drafts',JSON.stringify([...drafts]));}catch{status('Browser draft storage unavailable; use Save review.',true);}}
function restoreDraft(){const r=drafts.get(draftKey());$('note').value=r?.note||'';$('action').value=r?.action||'looks-correct';$('alternative').value=r?.alternative||'';clicked=r?.clicked||null;updateClick();}
function session(){return {updated_at:Date.now(),model_id:model.id,model_version:model.version,generation_id:boot.manifest.generation_id,gi,oid,origin_id:originId,view:{...view},layers:{...layers},opacity,autocenter:$('autocenter').checked,lighting_id:lightID,selected_only:$('selectedOnly').checked,drafts:[...drafts]};}
function mutation(kind,payload){const work=async()=>{const result=await api('/api/'+kind,{revision:reviews.revision,payload});reviews=result;$('saveStatus').textContent=`Saved · revision ${reviews.revision}`;updateProgress();return result;};const task=saveChain.then(work);saveChain=task.catch(e=>{status(e.message,true);$('saveStatus').textContent='SAVE FAILED — local draft retained';});return task;}
function scheduleSession(){if(!ready)return;clearTimeout(sessionTimer);$('saveStatus').textContent='Saving place…';sessionTimer=setTimeout(()=>mutation('session',session()).catch(()=>{}),450);}
function updateProgress(){if(!model)return;const done=reviewedSet(reviews.reviews,model,boot.manifest.generation_id);$('progress').textContent=`${done.size} / ${model.n} indexes reviewed`;$('saveStatus').title=`Reviews are separate files in photo2/output/debugger/reviews; ${reviews.reviews.length} historical review records retained.`;}
function dl(target,pairs){target.replaceChildren();const d=document.createElement('dl');for(const [key,value] of pairs){let dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=String(value??'unknown');d.append(dt,dd);}target.append(d);}
function paragraph(target,text,cls=''){let p=document.createElement('p');p.textContent=text;p.className=cls;target.append(p);}
function pointText(p){return p?p.map(x=>x.toFixed(2)).join(', '):'none';}
function btn(text,fn){const b=document.createElement('button');b.textContent=text;b.onclick=guard(fn);return b;}
function selectGI(i,{observation=null,center=$('autocenter').checked,save=true}={}){
 stashDraft();gi=wrap(i,model.n);oid=observation;
 if(!oid){const ids=selected().observations;oid=ids.find(id=>obsMap.get(id)?.evidence_class==='interior')||ids.find(id=>!['rejected','ambiguous-split'].includes(obsMap.get(id)?.evidence_class))||null;}
 restoreDraft();renderPanel();loadDetail();if(center)centerSelection();requestDraw();if(save)scheduleSession();
}
function centerSelection(zoom=false){const p=selectedPoint();if(zoom)view.scale=Math.max(view.scale,2.5);view.x=size.width/2-p[0]*view.scale;view.y=size.height/2-p[1]*view.scale;requestDraw();}
function step(d){selectGI(gi+d);}
function jumpK(k){selectGI(generatorOf(k,origin(),model.n));}
function chooseObservation(id){const o=obsMap.get(id);if(!o)throw new Error('Observation ID not found');const c=model.correspondences[id];selectGI(c.owner_generator_index??c.alternatives[0].generator_index,{observation:id});}
function fillOrigins(){const el=$('origin');el.replaceChildren(new Option('Legacy R255 origin (assisted)','legacy'));for(const r of reviews.origins.filter(r=>r.model_version===model.version&&r.generation_id===boot.manifest.generation_id))el.add(new Option(`Fresh origin: ${r.observation_id}`,r.id));if(![...el.options].some(o=>o.value===originId))originId='legacy';el.value=originId;}
async function switchModel(mid,initial=false){
 stashDraft();const prior=ready?selectedPoint():null;const oldOID=oid;const token=modelGate.invalidate();$('loading').style.display='flex';$('loading').textContent=`Loading ${mid}…`;
 if(!modelCache.has(mid))modelCache.set(mid,await api('/api/model?id='+encodeURIComponent(mid)));
 if(!modelGate.accepts(token))return;model=modelCache.get(mid);$('model').value=mid;fillOrigins();
 if(initial){const s=reviews.session;if(s.model_version===model.version&&s.generation_id===boot.manifest.generation_id){gi=wrap(s.gi||0,model.n);oid=obsMap.has(s.oid)?s.oid:null;originId=s.origin_id||'legacy';fillOrigins();}else{gi=model.origin;oid=null;}}
 else{originId='legacy';fillOrigins();gi=nearest(model.beads,prior,b=>b.center,1)[0].row.generator_index;if(oldOID&&obsMap.has(oldOID)){const c=model.correspondences[oldOID];gi=c.owner_generator_index??c.alternatives[0].generator_index;oid=oldOID;}else oid=null;}
 ready=true;restoreDraft();renderPanel();loadDetail();renderDiagnostics();requestDraw();$('loading').style.display='none';updateProgress();if(!initial)scheduleSession();
}
function patternRow(){const b=selected();return model.patterns.find(r=>Number(r.residue)===b.legacy_k%Number(r.P));}
function renderPanel(){
 const b=selected(),o=obsMap.get(oid),c=oid?model.correspondences[oid]:null,k=kOf(gi),t=triple(k,model.n),done=reviewedSet(reviews.reviews,model,boot.manifest.generation_id);
 $('selectedTitle').textContent=`Bead ${k} / ${model.n-1}`;$('selectionBadge').textContent=`${model.id} · k ${k} · h${model.h>0?'+1':'−1'} · ${b.area_px2?'visible geometry':'occluded / below sample grid'}${done.has(gi)?' · reviewed':''}`;
 const associated=b.observations.filter(id=>obsMap.get(id).evidence_class!=='rejected');
 dl($('details'),[['Model',model.id],['String index',`${k} (conditional; ${originId==='legacy'?'legacy':'confirmed review'} origin)`],['Generator',gi],['Triple',`(${t.join(', ')}) — algebraic, not observed topology`],['Helicity',model.h],['Modeled neighbors',[-1,1,-6,6,-7,7].map(d=>`${d>0?'+':''}${d}: k${kOf(wrap(gi+d,model.n))}`).join('; ')],['Predicted center',pointText(b.center)],['Minor-outward',pointText(b.outward)],['Visible centroid (coarse 4px)',pointText(b.visible_centroid)],['Geometry (coarse 4px)',`${b.visibility}; sampled area ${b.area_px2} px²`],['Photographic links',`${associated.length} candidate interiors/reflections owned conditionally; ${associated.length>1?'multiple candidates compete for this index':'identity unresolved'}`],['Selected observation',o?`${o.id} (${o.color})`:'none'],['Interior / reflection',o?pointText([o.x,o.y]):'none'],['Proposed template',`${patternRow()?.status??'?'} — rejected legacy hypothesis; not observed color`]]);
 $('observationDetails').replaceChildren();if(o){dl($('observationDetails'),[['Evidence',o.evidence_class],['Color',o.color],['Positive patch',`${o.patch_area} px; radius ${o.interior_radius_px?.toFixed(2)??'n/a'} px`],['Point ownership',c?.status],['Center residual',c?.center_residual_px==null?'no hit':`${c.center_residual_px.toFixed(2)} px (not center truth)`],['Patch ownership',c?.patch_support==null?'unavailable':`${(100*c.patch_support).toFixed(1)}% of ${c.patch_samples} sampled positive pixels`]]);paragraph($('observationDetails'),o.reason);}
 else paragraph($('observationDetails'),'No photographic observation selected. A modeled location is not a detected bead.');
 const p=selectedPoint();$('nearBeads').replaceChildren(...nearest(model.beads,p,b=>b.center).map(({row,distance})=>btn(`k${kOf(row.generator_index)} · ${distance.toFixed(0)}px`,()=>selectGI(row.generator_index))));
 $('nearObs').replaceChildren(...nearest(inventory.observations,p).map(({row,distance})=>btn(`${row.id} · ${row.evidence_class} · ${distance.toFixed(1)}px`,()=>chooseObservation(row.id))));
 $('fullEvidence').textContent=JSON.stringify({bead:{...b,footprint:`${b.footprint.length} ownership samples`},observation:o,correspondence:c},null,2);
 $('reviewContext').textContent=`${model.id}, k ${k}, generator ${gi}; model ${model.version.slice(0,10)}; ${oid||'no selected observation'}`;
 $('reviewHistory').replaceChildren();for(const r of reviews.reviews.filter(r=>r.model_version===model.version&&r.generator_index===gi).slice(-6).reverse())paragraph($('reviewHistory'),`${r.saved_at} [${r.surface_schema?'R257 '+r.lighting_id:'R256 coarse measurements'}]: ${r.action} — ${r.note||'(no note)'}${r.generation_id!==boot.manifest.generation_id?' [older detector version]':''}`);
 $('confirmOrigin').disabled=!o||o.kind!=='colored-interior'||o.evidence_class==='rejected';
 renderCrops();renderProfile();renderPattern();renderFFT();updateProgress();
}
function loadDetail(){
 const token=++detailToken;detail=null;clearTimeout(detailTimer);$('surfaceStatus').textContent='Tracing native pixels in background…';$('surfaceDetails').replaceChildren();$('surfaceJSON').textContent='';requestDraw();
 const path=`/api/surface?id=${encodeURIComponent(model.id)}&gi=${gi}&light=${encodeURIComponent(lightID)}`;
 const poll=async()=>{try{const data=await api(path);if(token!==detailToken)return;if(data.status!=='ready'){detailTimer=setTimeout(poll,600);return;}detail=data.result;renderSurface();renderCrops();requestDraw();}catch(e){if(token===detailToken)$('surfaceStatus').textContent='Surface calculation failed: '+e.message;}};
 detailTimer=setTimeout(poll,180);
}
function renderSurface(){
 if(!detail)return;const b=detail.beads.find(x=>x.generator_index===gi),h=b.highlight;
 $('surfaceStatus').textContent=`1px + boundary 2×2 · ${detail.native_rays} native rays · ${detail.unfinished_camera_pairs} unfinished pairs excluded · ${lightID}`;
 dl($('surfaceDetails'),[['Model / index',`${model.id} · k${kOf(gi)} · generator ${gi} · ${originId} origin`],['Physical center xy',pointText(b.center_xy)],['Outermost surface xy',pointText(b.outward.xy)],['Outward visibility',`${b.outward.visible?'visible':'occluded'}; first owner g${b.outward.first_owner}`],['Visible area centroid',pointText(b.centroid)],['Centroid 4 / 2 / 1 px',Object.entries(b.convergence).map(([k,v])=>`${k}: (${pointText(v.centroid)}); Δadaptive ${v.distance_to_adaptive_px?.toFixed(3)??'undefined'}px`).join('; ')],['Predicted highlight centroid',pointText(h?.centroid)],['Predicted highlight peak',pointText(h?.peak_xy)],['Highlight shape',h?`${h.area_px2}px² above 50% peak; σ ${h.sigma_major.toFixed(2)} × ${h.sigma_minor.toFixed(2)}px; ${h.orientation_deg.toFixed(1)}°`:'undefined / negligible'],['Observed candidates',b.observed_reflections.map(o=>`${o.id}: ${pointText(o.xy)}`).join('; ')||'none'],['Reflection discrepancy',b.reflection_error_px==null?'undefined: no unique reliable match':`${b.reflection_error_px.toFixed(2)}px (conditional owner)`],['Primary geometry heldout lighting test',JSON.stringify(detail.lighting.metrics?.test||{})],['Uncertainty',detail.uncertainty.lighting],['Geometry',b.visibility]]);
 $('surfaceJSON').textContent=JSON.stringify({...detail,footprint:`${detail.footprint.length} owned pixels (full data in ZIP)`,background_shadows:`${detail.background_shadows.length} plane samples`},null,2);
}
function drawDetail(c,project,scale){
 if(!detail)return;const pixel=(p,color,alpha,size=1)=>{const q=project([p[0]-.5,p[1]-.5]);c.globalAlpha=alpha*opacity;c.fillStyle=color;c.fillRect(q[0],q[1],size*scale,size*scale);};
 for(const p of detail.footprint){if($('selectedOnly').checked&&p[2]!==gi)continue;if(layers.nativeSurface)pixel(p,`hsl(${(p[2]*137.5)%360} 80% 65%)`,.35);if(layers.highlightRegion&&p[3]>.0001)pixel(p,'#ff68e0',Math.min(.85,p[3]));if(layers.shadowDiagnostic){if(p[4]>.01)pixel(p,'#a15aff',p[4]*.6);if(p[5]>.5)pixel(p,'#e7c650',.3);}}
 if(layers.shadowDiagnostic){for(const p of detail.background_shadows)if(p[2]>.01)pixel(p,'#9662ef',p[2]*.55,3);for(const p of detail.observed_background_deficit)pixel(p,'#ff8b36',p[2],8);}
 c.globalAlpha=opacity;const mark=(p,color,kind,r=4)=>{if(!p)return;const [x,y]=project(p);c.strokeStyle=color;c.fillStyle=color;c.lineWidth=1.5;c.beginPath();if(kind==='cross'){c.moveTo(x-r,y-r);c.lineTo(x+r,y+r);c.moveTo(x+r,y-r);c.lineTo(x-r,y+r);c.stroke();}else{c.arc(x,y,r,0,2*Math.PI);kind==='dot'?c.fill():c.stroke();}};
 for(const b of detail.beads){if($('selectedOnly').checked&&b.generator_index!==gi)continue;if(layers.nativeCenter)mark(b.center_xy,'#82b6ff','ring',5);if(layers.nativeOutward)mark(b.outward.xy,b.outward.visible?'#ffa769':'#777b86','cross');if(layers.nativeCentroid)mark(b.centroid,'#68ff95','dot',3);if(layers.highlightPoint&&b.highlight)mark(b.highlight.centroid,'#ff72e3','cross',5);}
 if(layers.observedReflection)for(const o of detail.observed_reflections)if(!$('selectedOnly').checked||o.local_owner===gi)mark(o.xy,'#ffffff','ring',o.reliable_candidate?6:3);
 c.globalAlpha=1;
}
$('selectedOnly').onchange=()=>{renderCrops();requestDraw();scheduleSession();};
function cleanPreset(points=false){layers=Object.fromEntries(specs.map(s=>[s[0],s[0]==='photo']));$('selectedOnly').checked=true;if(points){layers.nativeCenter=true;layers.nativeOutward=true;layers.nativeCentroid=true;layers.highlightPoint=true;}else layers.nativeSurface=true;syncLayerControls();renderCrops();requestDraw();scheduleSession();}
$('cleanFootprint').onclick=()=>cleanPreset(false);$('comparePoints').onclick=()=>cleanPreset(true);
$('lighting').onchange=()=>{lightID=$('lighting').value;loadDetail();scheduleSession();};
function renderCrops(){
 const p=selectedPoint(),half=65;
 for(const id of ['rawCrop','markedCrop']){const can=$(id),c=can.getContext('2d'),scale=can.height/(2*half);c.fillStyle='#0b1119';c.fillRect(0,0,can.width,can.height);c.save();c.translate(can.width/2-p[0]*scale,can.height/2-p[1]*scale);c.scale(scale,scale);c.imageSmoothingEnabled=false;c.drawImage(photo,-.5,-.5);
 if(id==='markedCrop'){
 const o=obsMap.get(oid);if(o&&(layers.patches||layers.interiors||layers.ambiguous)){c.fillStyle=colors[o.color];c.globalAlpha=.5;for(const [x,y] of o.patch)c.fillRect(x-.5,y-.5,1,1);c.globalAlpha=1;c.strokeStyle=colors[o.color];c.lineWidth=1/scale;c.beginPath();c.arc(o.x,o.y,5/scale,0,2*Math.PI);c.stroke();}
 if(layers.centers){c.strokeStyle='#6acfff';c.lineWidth=1/scale;for(const b of nearest(model.beads,p,b=>b.center,12).map(z=>z.row)){c.beginPath();c.arc(...b.center,2/scale,0,2*Math.PI);c.stroke();}const b=selected();c.strokeStyle='white';c.beginPath();c.arc(...b.center,6/scale,0,2*Math.PI);c.stroke();}
 if(layers.ambiguous&&o?.split_evidence.length){c.strokeStyle='#ffac65';for(const j of o.split_evidence.slice(0,5)){const ends=inventory.split_pairs[j].endpoints;c.beginPath();c.moveTo(...ends[0]);c.lineTo(...ends[1]);c.stroke();}}
 }c.restore();if(id==='markedCrop')drawDetail(c,q=>[(q[0]-p[0])*scale+can.width/2,(q[1]-p[1])*scale+can.height/2],scale);}
}
function renderProfile(){const c=$('profile').getContext('2d');c.fillStyle='#0b1119';c.fillRect(0,0,340,100);const o=obsMap.get(oid),pairs=(o?.split_evidence||[]).map(j=>inventory.split_pairs[j]);$('profileDetails').replaceChildren();if(!pairs.length){c.fillStyle='#aab8c8';c.fillText('No within-component split profile for this point',10,48);return;}
 const p=pairs[0];for(const [name,color] of [['value','#f1f6fb'],['chroma','#78ddea']]){c.strokeStyle=color;c.beginPath();p[name].forEach((v,i)=>{const x=8+324*i/(p[name].length-1),y=90-v*80;i?c.lineTo(x,y):c.moveTo(x,y);});c.stroke();}paragraph($('profileDetails'),`First orange crop route: V (white), chroma (cyan); valley ${(p.valley_fraction*100).toFixed(1)}%. ${p.credible_split_evidence?'Two positive interiors plus valley support a split hypothesis.':'Insufficient split evidence; retained as ambiguous.'} ${pairs.length} profiles available in export.`);}
function renderPattern(){const p=patternRow(),target=$('patternDetails');target.replaceChildren();if(!p){paragraph(target,'No saved template for this hypothesis. Proposed color remains unknown.');}else{paragraph(target,`P=${p.P}; legacy k mod P=${p.residue}; template=${p.status}. This template is rejected. R/Y are conditional proposals; ! contradicts; ? unknown.`,'warn');paragraph(target,`Legacy red: ${p.red_observations||'none'}; yellow: ${p.yellow_observations||'none'}`);const o=obsMap.get(oid);if(o)paragraph(target,`Selected fresh observed color: ${o.color}. ${(['R','Y'].includes(p.status)&&({red:'R',yellow:'Y'}[o.color]!==p.status))?'Contradiction with this selected candidate; do not recolor the observation.':''}`);}
 const c=$('pattern').getContext('2d');c.clearRect(0,0,340,140);const pc={R:colors.red,Y:colors.yellow,'!':'#d069ed','?':'#56616f'};for(const r of model.patterns){const i=+r.residue,x=(i%34)*10,y=Math.floor(i/34)*11;c.fillStyle=pc[r.status];c.fillRect(x+1,y+1,8,9);if(p===r){c.strokeStyle='white';c.strokeRect(x,y,10,11);}}}
function renderDiagnostics(){
 dl($('modelDetails'),[['Model',model.id],['Status',model.provenance],['Count / turns',`${model.n} / ${model.turns}`],['Helicity',model.h],['Camera',JSON.stringify(model.fitted_camera)],['Registration',`${model.parameters.dx_px.toFixed(3)}, ${model.parameters.dy_px.toFixed(3)} px`],['Independent fit','Staged; not performed'],['Origin',model.origin_label],['Surface sampling',`4px grid, ${model.unfinished_rays} unfinished rays excluded`]]);
 const c=$('corrections').getContext('2d');c.fillStyle='#0b1119';c.fillRect(0,0,340,140);for(const [key,color,unit] of [['stretch','#62e3ef','relative'],['twist_deg','#ffad69','deg']]){const max=Math.max(...model.beads.map(b=>Math.abs(b[key])),1e-8);c.strokeStyle=color;c.beginPath();for(let i=0;i<model.n;i++){const x=8+324*i/(model.n-1),y=80-45*model.beads[i][key]/max;i?c.lineTo(x,y):c.moveTo(x,y);}c.stroke();c.fillStyle=color;c.fillText(`${key}: ±${max.toPrecision(3)} ${unit}`,8,key==='stretch'?14:29);}
 dl($('provenance'),[['Image SHA-256',boot.manifest.image_sha256],['Generation',boot.manifest.generation_id],['Detector',inventory.version],['Fresh candidates',inventory.observations.length],['Learned hue modes',inventory.palette.groups.map(g=>`${g.color}: ${g.hue_deg}° ±${g.radius_deg}°`).join('; ')],['Spline provenance',boot.splines.provenance],['Legacy labels used','None in fresh generation'],['Dark areas','Never converted to beads without positive reflection evidence']]);
}
function renderFFT(){if(!fft||!ready)return;const near=nearest(fft.candidates.filter(r=>r.channel==='Y'),selectedPoint(),r=>[r.x,r.y],8);$('fftDetails').replaceChildren();paragraph($('fftDetails'),fft.source);for(const {row:r} of near.slice(0,4))paragraph($('fftDetails'),`${r.observation}: tangent-relative ${r.relative_angle.toFixed(2)}°, wavelength ${r.wavelength.toFixed(2)} px; prominence ${r.prominence.toFixed(1)}; track ${r.track}; ambiguous ${r.ambiguous}.`);}
async function loadFFT(){if(!fft){status('Loading 32,000 preserved FFT candidates…');fft=await api('/api/fft');status('FFT candidates loaded. Frequency-vector angles are not direct neighbor directions.');}renderFFT();requestDraw();}
function requestDraw(){if(pendingFrame)return;pendingFrame=true;requestAnimationFrame(()=>{pendingFrame=false;draw();});}
function screen(p){return [p[0]*view.scale+view.x,p[1]*view.scale+view.y];}
function onScreen(p,pad=40){const [x,y]=screen(p);return x>-pad&&x<size.width+pad&&y>-pad&&y<size.height+pad;}
function line(points,color,width=1,dash=[]){if(!points.length)return;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.setLineDash(dash);ctx.beginPath();points.forEach((p,i)=>{const q=screen(p);i?ctx.lineTo(...q):ctx.moveTo(...q);});ctx.stroke();ctx.setLineDash([]);}
function marker(p,color,r=3,shape='ring'){if(!onScreen(p))return;const [x,y]=screen(p);ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=1.3;ctx.beginPath();if(shape==='cross'){ctx.moveTo(x-r,y-r);ctx.lineTo(x+r,y+r);ctx.moveTo(x+r,y-r);ctx.lineTo(x-r,y+r);ctx.stroke();}else{ctx.arc(x,y,r,0,2*Math.PI);shape==='dot'?ctx.fill():ctx.stroke();}drawCount++;}
function textLabel(p,text,color,occupied,force=false){const [x,y]=screen(p);ctx.font='12px system-ui';const w=ctx.measureText(text).width+6,rect=[x+5,y-17,x+5+w,y-1];if(!force&&!labelAllowed(rect,occupied))return;ctx.fillStyle='#101820e8';ctx.fillRect(rect[0],rect[1],w,16);ctx.fillStyle=color;ctx.fillText(text,x+8,y-5);renderStats.labels++;}
function obsVisible(o){return o.evidence_class==='rejected'?layers.rejected:o.evidence_class==='black-candidate'?layers.black:['small-patch','ambiguous-split'].includes(o.evidence_class)?layers.ambiguous:layers.interiors;}
function draw(){const start=performance.now();const dpr=window.devicePixelRatio||1;ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,size.width,size.height);if(!ready)return;drawCount=0;renderStats={labels:0};
 if(layers.photo){ctx.save();ctx.translate(view.x,view.y);ctx.scale(view.scale,view.scale);ctx.imageSmoothingEnabled=view.scale<2;ctx.drawImage(photo,-.5,-.5);ctx.restore();}
 ctx.globalAlpha=opacity;
 for(const [key,color] of [['inner','#79ed9c'],['outer','#ffa95c']])if(layers[key])line(boot.splines.raw[key+'_spline'],color,1.5);
 if(layers.centerline)line(boot.splines.centerline,'#43e7f1',1.5);
 if(layers.midpoint)line(boot.splines.raw.centerline_spline,'#b7fafa',1,[4,3]);
 if(layers.registered)line(model.centerline,'#7698ff',2,[6,4]);
 if(layers.archived&&archived)for(const key of ['inner','outer','centerline'])line(archived[key+'_spline'],'#ee75fa',1,[3,4]);
 if(layers.tangents)for(let i=0;i<boot.splines.centerline.length;i+=32){const p=boot.splines.centerline[i],t=boot.splines.tangents[i];if(!onScreen(p,100))continue;line([[p[0]-t[0]*30,p[1]-t[1]*30],[p[0]+t[0]*30,p[1]+t[1]*30]],'#f0f3fa');line([[p[0]+t[1]*50,p[1]-t[0]*50],[p[0]-t[1]*50,p[1]+t[0]*50]],'#c0cfde',1,[2,3]);}
 const visible=model.beads.filter(b=>onScreen(b.center,60));
 if(layers.surfaces){ctx.fillStyle='#75b2d8';ctx.globalAlpha=opacity*.25;for(const b of visible)for(const p of b.footprint){const q=screen([p[0]-2,p[1]-2]);ctx.fillRect(...q,4*view.scale,4*view.scale);}ctx.globalAlpha=opacity;}
 for(const b of visible){if(layers.centers)marker(b.center,b.area_px2?'#82b6ff':'#68758b',b.generator_index===gi?4:Math.max(.8,Math.min(2,view.scale*1.5)),b.area_px2?'ring':'cross');if(layers.outward)marker(b.outward,'#ffa769',2,'cross');if(layers.centroids&&b.visible_centroid)marker(b.visible_centroid,'#a9c6f2',2,'dot');
 if(layers.corrections&&b.generator_index%8===0){const c=model.centerline[Math.floor(b.generator_index/3)%model.centerline.length],next=model.centerline[(Math.floor(b.generator_index/3)+1)%model.centerline.length],len=Math.hypot(next[0]-c[0],next[1]-c[1])||1;line([c,[c[0]+(next[0]-c[0])/len*b.longitudinal_shift_px,c[1]+(next[1]-c[1])/len*b.longitudinal_shift_px]],'#ffb668',2);}
 }
 const occupied=[];{const [x,y]=screen(selected().center);ctx.font='12px system-ui';occupied.push([x+5,y-17,x+11+ctx.measureText(`SELECTED k${kOf(gi)}`).width,y-1]);}
 const b=selected();if(layers.neighbors)for(const d of [-1,1,-6,6,-7,7]){const nb=model.beads[wrap(gi+d,model.n)],color=Math.abs(d)===1?'#ffffff':Math.abs(d)===6?'#6df0fa':'#ffad62';line([b.center,nb.center],color,2,d<0?[4,3]:[]);marker(nb.center,color,Math.min(5,view.scale*3));if(view.scale>=1.5)textLabel(nb.center,`${d>0?'+':''}${d} → k${kOf(nb.generator_index)}`,color,occupied);}
 if(layers.indices||layers.triples||layers.generator||layers.pattern){for(const b of visible){if(view.scale<1.5||b.generator_index===gi)continue;const k=kOf(b.generator_index);let s=[];if(layers.indices)s.push(`k${k}`);if(layers.generator)s.push(`g${b.generator_index}`);if(layers.triples)s.push(`(${triple(k,model.n).join(',')})`);let color=b.area_px2?'#e4f2ff':'#9ca9b9';if(layers.pattern){const P=Number(model.patterns[0]?.P);if(P){const r=model.patterns[b.legacy_k%P];s.push(`r${b.legacy_k%P}:${r.status}`);color={R:colors.red,Y:colors.yellow,'!':'#e9a1fb','?':'#a9b5c8'}[r.status];}}textLabel(b.center,s.join(' '),color,occupied);}}
 for(const o of inventory.observations){if(!obsVisible(o)||!onScreen([o.x,o.y]))continue;const p=[o.x,o.y],col=colors[o.color]||'#e6d474';if(layers.patches&&view.scale>=1){ctx.fillStyle=col;ctx.globalAlpha=.4*opacity;for(const p of o.patch||[]){const q=screen([p[0]-.5,p[1]-.5]);ctx.fillRect(...q,view.scale,view.scale);}ctx.globalAlpha=opacity;}
 ctx.setLineDash(o.evidence_class==='ambiguous-split'?[2,2]:[]);marker(p,col,o.id===oid?7:Math.max(1.2,Math.min(4,view.scale*2.5)),o.evidence_class==='rejected'?'cross':'ring');ctx.setLineDash([]);
 if(layers.correspondence){const c=model.correspondences[o.id];if(c.owner_generator_index!=null)line([p,model.beads[c.owner_generator_index].center],'#79efd5',.8);else marker(p,'#fa86d9',6,'cross');}
 if(view.scale>=3&&o.id!==oid)textLabel(p,o.id.split('-').slice(-3).join('-'),col,occupied);
 }
 if(layers.legacy||layers.legacyWithheld)for(const o of legacy)if((o.withheld?layers.legacyWithheld:layers.legacy)&&onScreen([o.x,o.y])){marker([o.x,o.y],'#e69cff',5,'cross');if(view.scale>=2)textLabel([o.x,o.y],`legacy ${o.observation_id}`,'#e69cff',occupied);}
 if(layers.fft&&fft){const stride=view.scale<1?80:view.scale<2?20:5;for(const r of fft.candidates){if(r.channel!=='Y'||r.index%stride||r.candidate!=='1'||!onScreen([r.x,r.y]))continue;const a=r.angle*Math.PI/180,L=25;line([[r.x-Math.cos(a)*L,r.y-Math.sin(a)*L],[r.x+Math.cos(a)*L,r.y+Math.sin(a)*L]],'#d294ff',1.2);}}

 drawDetail(ctx,screen,view.scale);
 // Selection is an explicit UI locator, independent of overlay choices.
 ctx.globalAlpha=1;if(Object.entries(layers).some(([key,on])=>!['photo','nativeCenter','nativeSurface','nativeOutward','nativeCentroid','highlightPoint','highlightRegion','observedReflection','shadowDiagnostic'].includes(key)&&on)){marker(b.center,'#ffffff',8);textLabel(b.center,`SELECTED k${kOf(gi)}`,'#ffffff',occupied,true);
 if(oid){const o=obsMap.get(oid);marker([o.x,o.y],colors[o.color],9);}
 }
 if(clicked){marker(clicked,'#fa71ec',9,'cross');textLabel(clicked,'Review correction','#fa71ec',occupied,true);}
 renderStats={...renderStats,markers:drawCount,ms:performance.now()-start,scale:view.scale};$('drawStats').textContent=`${view.scale.toFixed(2)}× · ${renderStats.markers} visible markers · ${renderStats.labels} labels · ${renderStats.ms.toFixed(1)}ms last draw`;
}
function resize(){const rect=$('viewport').getBoundingClientRect(),next={width:rect.width,height:rect.height};view=resizeView(view,size,next);size=next;const d=window.devicePixelRatio||1;$('photoCanvas').width=Math.round(size.width*d);$('photoCanvas').height=Math.round(size.height*d);requestDraw();}
function updateClick(){$('clicked').textContent=clicked?`Correction position: ${pointText(clicked)} in original pixels.`:'Shift-click the photograph to attach a correction position.';}
function reviewRecord(){return {model_id:model.id,model_version:model.version,generation_id:boot.manifest.generation_id,generator_index:gi,bead_index:kOf(gi),origin_id:originId,origin_generator_index:origin(),lighting_id:lightID,lighting_parameters:lightingDoc.lights.find(l=>l.id===lightID),surface_cache_key:detail?.cache_key??null,surface_schema:1,selected_only:$('selectedOnly').checked,observation_id:oid,source_position:selectedPoint(),clicked_position:clicked,action:$('action').value,note:$('note').value,alternative:$('alternative').value,enabled_layers:Object.entries(layers).filter(([,v])=>v).map(([k])=>k),overlay_opacity:opacity,view:{...view}};}
async function saveReview(next=false){stashDraft();const rec=reviewRecord();await mutation('review',rec);status(`Saved ${rec.action} for k${rec.bead_index}. Geometry and detections were not changed.`);if(next&&gi===rec.generator_index&&model.version===rec.model_version)step(1);else renderPanel();scheduleSession();}
async function exportDebug(){stashDraft();const blob=await api('/api/debug-export',reviewRecord());download(blob,`${model.id}-k${kOf(gi)}-debug.zip`);status('Debugging ZIP downloaded with original crop and numerical provenance.');}
function download(blob,name){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
function makeLayers(){for(const [id,title,color,,help] of specs){const div=document.createElement('div');div.className='layer';const label=document.createElement('label'),input=document.createElement('input'),swatch=document.createElement('span'),small=document.createElement('small');input.type='checkbox';input.id='layer-'+id;input.checked=layers[id];swatch.className='swatch';swatch.style.background=color;label.append(input,swatch,document.createTextNode(title));small.textContent=help;div.append(label,small);$('layerList').append(div);input.onchange=guard(async()=>{layers[id]=input.checked;if(['legacy','legacyWithheld'].includes(id)&&layers[id]&&!legacy.length)legacy=await api('/api/legacy');if(id==='archived'&&layers[id]&&!archived)archived=await api('/api/legacy-splines');if(id==='fft'&&layers[id])await loadFFT();requestDraw();scheduleSession();});}}
function syncLayerControls(){for(const [id] of specs)$('layer-'+id).checked=layers[id];$('opacity').value=opacity;}
function setTab(id){for(const e of document.querySelectorAll('.tab'))e.classList.toggle('active',e.id===id);for(const b of document.querySelectorAll('[data-tab]'))b.classList.toggle('active',b.dataset.tab===id);if(id==='diagnostics')renderDiagnostics();}
for(const b of document.querySelectorAll('[data-tab]'))b.onclick=()=>setTab(b.dataset.tab);
for(const b of document.querySelectorAll('[data-step]'))b.onclick=()=>{if(ready)step(Number(b.dataset.step));};
$('fit').onclick=()=>{if(!ready)return;view=fitView(size.width,size.height,[-.5,-.5,photo.width-.5,photo.height-.5]);requestDraw();scheduleSession();};$('reset').onclick=()=>$('fit').click();
$('center').onclick=()=>{if(ready){centerSelection(true);scheduleSession();}};
$('zero').onclick=()=>{if(ready){jumpK(0);centerSelection(true);scheduleSession();}};
$('unchecked').onclick=()=>{if(!ready)return;const j=nextUnchecked(gi,origin(),model.n,reviewedSet(reviews.reviews,model,boot.manifest.generation_id));if(j===null)status('Every index in this model/detector version has a review.');else selectGI(j);};
$('model').onchange=guard(()=>switchModel($('model').value));$('autocenter').onchange=scheduleSession;
$('searchForm').onsubmit=guard(e=>{e.preventDefault();if(!ready)return;const s=$('search').value.trim();if(/^-?\d+$/.test(s)){const k=Number(s);if(!Number.isSafeInteger(k))throw new Error('Enter a safe whole-number index');jumpK(k);}else{const ids=[...obsMap.keys()].filter(id=>id.toLowerCase().includes(s.toLowerCase()));if(ids.length!==1)throw new Error(`Found ${ids.length} observations. Choose a full ID from the suggestions.`);chooseObservation(ids[0]);}centerSelection(true);scheduleSession();});
// Prevent form navigation synchronously, before the async guard starts.
$('searchForm').addEventListener('submit',e=>e.preventDefault());
$('search').oninput=()=>{if(!ready)return;const value=$('search').value.toLowerCase();$('searchOptions').replaceChildren(...[...obsMap.keys()].filter(id=>value&&id.toLowerCase().includes(value)).slice(0,20).map(id=>new Option(id,id)));};
$('photoOnly').onclick=()=>{layers=Object.fromEntries(specs.map(s=>[s[0],s[0]==='photo']));syncLayerControls();requestDraw();scheduleSession();};$('defaultLayers').onclick=()=>{layers={...defaults};syncLayerControls();requestDraw();scheduleSession();};
$('opacity').oninput=()=>{opacity=Number($('opacity').value);requestDraw();scheduleSession();};
$('saveReview').onclick=guard(()=>saveReview());$('saveNext').onclick=guard(()=>saveReview(true));$('export').onclick=guard(exportDebug);
for(const id of ['note','action','alternative'])$(id).oninput=()=>{stashDraft();scheduleSession();};$('clearClick').onclick=()=>{clicked=null;stashDraft();updateClick();requestDraw();scheduleSession();};
$('origin').onchange=()=>{originId=$('origin').value;renderPanel();requestDraw();scheduleSession();};
$('confirmOrigin').onclick=guard(async()=>{const o=obsMap.get(oid);if(!o)throw new Error('Select a fresh observation first');const rec=reviewRecord();rec.source_position=[o.x,o.y];rec.confirmation='User explicitly selected this fresh observation as numbering reference; model fit unchanged';const result=await mutation('origin',rec);originId=result.origins.at(-1).id;fillOrigins();renderPanel();requestDraw();scheduleSession();status('Fresh observation confirmed as review index 0. This changes numbering, not the legacy-assisted fit.');});
const backupLink=document.querySelector('a[href="/api/backup"]');
backupLink.addEventListener('click',e=>{e.preventDefault();guard(async()=>{stashDraft();clearTimeout(sessionTimer);await mutation('session',session());const doc=await api('/api/backup');download(new Blob([JSON.stringify(doc,null,2)],{type:'application/json'}),'bead-reviews-backup.json');status('Backup downloaded after saving your current place and drafts.');})();});
$('import').onchange=guard(async()=>{const file=$('import').files[0];if(!file)return;const doc=JSON.parse(await file.text());await mutation('import',doc);status('Backup merged; review histories retained. Restoring saved session.');await restoreSession();});
$('reloadState').onclick=guard(async()=>{stashDraft();await saveChain;reviews=await api('/api/reviews');await restoreSession();status('Reloaded saved server state. Local drafts remain available.');});
$('loadFFT').onclick=guard(loadFFT);
async function restoreSession(){const s=reviews.session;lightID=lightingDoc.lights.some(l=>l.id===s.lighting_id)?s.lighting_id:lightingDoc.selected;$('lighting').value=lightID;$('selectedOnly').checked=s.selected_only??true;for(const [k,v] of s.drafts||[])if(!drafts.has(k)||(v.updated_at||0)>(drafts.get(k).updated_at||0))drafts.set(k,v);if(s.view)view=s.view;layers={...defaults,...s.layers};opacity=s.opacity??.85;$('autocenter').checked=s.autocenter??true;syncLayerControls();await switchModel(boot.model_ids.includes(s.model_id)?s.model_id:boot.model_ids[0],true);if((layers.legacy||layers.legacyWithheld)&&!legacy.length)legacy=await api('/api/legacy');if(layers.archived&&!archived)archived=await api('/api/legacy-splines');if(layers.fft)await loadFFT();requestDraw();}
let drag=null;
const canvas=$('photoCanvas');const eventPoint=e=>{const r=canvas.getBoundingClientRect();return {x:e.clientX-r.left,y:e.clientY-r.top};};
canvas.addEventListener('wheel',e=>{e.preventDefault();if(!ready)return;const delta=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?size.height:1);view=zoomAt(view,eventPoint(e),Math.exp(-delta*.0015));requestDraw();scheduleSession();},{passive:false});
canvas.onpointerdown=e=>{if(!ready||e.button!==0)return;canvas.focus();canvas.setPointerCapture(e.pointerId);drag={start:eventPoint(e),view:{...view},moved:false};};
canvas.onpointermove=e=>{if(!ready)return;const p=eventPoint(e),s=toSource(p,view);$('cursor').textContent=`x ${s.x.toFixed(2)}, y ${s.y.toFixed(2)} · ${view.scale.toFixed(2)}×`;if(drag){const dx=p.x-drag.start.x,dy=p.y-drag.start.y;if(Math.hypot(dx,dy)>3)drag.moved=true;if(drag.moved){view={...drag.view,x:drag.view.x+dx,y:drag.view.y+dy};requestDraw();}}};
canvas.onpointerup=e=>{if(!drag)return;const moved=drag.moved;drag=null;if(moved){scheduleSession();return;}const p=toSource(eventPoint(e),view),xy=[p.x,p.y];if(p.x<0||p.y<0||p.x>=photo.width||p.y>=photo.height)return;if(e.shiftKey){clicked=xy;stashDraft();updateClick();requestDraw();scheduleSession();status('Correction point attached to current review draft.');return;}
 const obs=nearest(inventory.observations.filter(obsVisible),xy,r=>[r.x,r.y],1)[0];if(obs&&obs.distance*view.scale<=11){chooseObservation(obs.row.id);return;}
 if(layers.centers||layers.surfaces||layers.outward||layers.centroids){const near=nearest(model.beads,xy,b=>b.center,1)[0];if(near.distance*view.scale<18||layers.surfaces&&near.distance<22)selectGI(near.row.generator_index,{center:false});}
};canvas.onpointercancel=()=>{drag=null;};
document.addEventListener('keydown',e=>{if(!ready||e.ctrlKey||e.metaKey||e.altKey||['INPUT','TEXTAREA','SELECT','BUTTON'].includes(document.activeElement.tagName))return;const map={ArrowRight:1,ArrowLeft:-1,q:-6,e:6,a:-7,d:7};if(e.key in map){e.preventDefault();step(map[e.key]);}else if(e.key==='Home'){e.preventDefault();$('zero').click();}else if(e.key==='n')$('unchecked').click();else if(e.key==='f')$('fit').click();else if(e.key==='c')$('center').click();else if(e.key==='/'){e.preventDefault();$('search').focus();}});
window.addEventListener('beforeunload',()=>{if(!ready)return;stashDraft();try{localStorage.setItem('bead-debugger-session',JSON.stringify(session()));}catch{}});
new ResizeObserver(resize).observe($('viewport'));
async function start(){
 lightingDoc=await api('/api/lighting');for(const l of lightingDoc.lights)$('lighting').add(new Option(l.id,l.id));lightID=lightingDoc.selected;
 boot=await api('/api/bootstrap');inventory=boot.inventory;obsMap=new Map(inventory.observations.map(r=>[r.id,r]));reviews=boot.reviews;
 try{for(const [k,v] of JSON.parse(localStorage.getItem('bead-debugger-drafts')||'[]'))drafts.set(k,v);}catch{}
 for(const mid of boot.model_ids)$('model').add(new Option(mid,mid));
 await new Promise((resolve,reject)=>{photo.onload=resolve;photo.onerror=()=>reject(new Error('Original photograph failed to load'));photo.src='/photo.png';});resize();view=fitView(size.width,size.height,[-.5,-.5,photo.width-.5,photo.height-.5]);makeLayers();await restoreSession();
 // An interrupted page close can precede server debounce; recover same-version local position.
 try{const s=JSON.parse(localStorage.getItem('bead-debugger-session')||'null');if(s&&(s.updated_at||0)>(reviews.session.updated_at||0)&&s.model_version===model.version&&s.generation_id===boot.manifest.generation_id){view=s.view;originId=s.origin_id;fillOrigins();selectGI(s.gi,{observation:obsMap.has(s.oid)?s.oid:null,center:false,save:false});}}catch{}
 status('Ready. Geometry is a diagnostic hypothesis; fresh observations are independent candidates.');$('saveStatus').textContent=`Saved · revision ${reviews.revision}`;
 window.debuggerTest={get state(){return {ready,model:model.id,version:model.version,n:model.n,h:model.h,gi,k:kOf(gi),oid,view:{...view},layers:{...layers},origin:origin(),stats:renderStats,size,revision:reviews.revision,detailReady:!!detail,lightID};},get detail(){return detail;},toSource:p=>toSource(p,view),toScreen:p=>toScreen(p,view),selectGI,chooseObservation,switchModel,jumpK,draw,inventory,models:modelCache,selectedPoint,session,flush:async()=>{clearTimeout(sessionTimer);await mutation('session',session());await saveChain;}};
}
start().catch(e=>{$('loading').textContent='Startup failed: '+e.message;status(e.message,true);console.error(e);});
