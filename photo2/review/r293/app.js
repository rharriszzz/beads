'use strict';
const $=id=>document.getElementById(id);
const answerKeys=['A','B','partial','wrong-clear','insufficient','not-sure'];
const names={T1:'Coherent darkness',T2:'Illumination and bright continuity',T3:'Material color',T4:'Competing highlights',T5:'Internal darkness',T6:'Occlusion context',T7:'Boundary completeness',T8:'Measurement reliability'};
let manifest,state={cases:{},ownership:{}},history=[],filtered=[],index=0,entry,current,img;
let scale=4,pan=[0,0],drag=null,hidden=false,busy=false,loading=false;
const navigation=['prev','next','prevBottom','nextBottom','nextOpen','caseSelect','playlist','category','unreviewed'];
const pair=(a,b)=>[a,b].sort().join('|');
async function json(url,options){const r=await fetch(url,options),d=await r.json();if(!r.ok)throw Error(d.error||r.statusText);return d;}
function fail(e){$('error').textContent=e.message||String(e);}
function payload(){return structuredClone(state.cases[entry.case_id]?.payload||{answer:null,diagnostics:[],ownership:{}});}
function progress(){const first=manifest.cases.filter(c=>manifest.start_here.includes(c.case_id));$('progress').textContent=`Start Here: ${first.filter(c=>state.cases[c.case_id]?.payload.answer).length}/${first.length} · ${manifest.cases.filter(c=>c.historical_review).length} historical judgments retained · other cases optional`;}

function selectEntries(){
  const set=$('playlist').value;
  let rows=set==='start'?manifest.start_here.map(id=>manifest.cases.find(c=>c.case_id===id)):manifest.cases.filter(c=>set==='all'||c.split===set);
  return rows.filter(c=>(!$('category').value||c.categories.includes($('category').value))&&(!$('unreviewed').checked||(!c.historical_review&&!state.cases[c.case_id]?.payload.answer)));
}
async function refresh(keep){
  filtered=selectEntries();$('caseSelect').replaceChildren(...filtered.map((c,i)=>new Option(`${i+1}/${filtered.length} · ${c.case_id}${state.cases[c.case_id]?.payload.answer?' ✓':''}`,c.case_id)));progress();
  if(!filtered.length){$('message').textContent='No unanswered cases match this set. Your saved answers remain available.';return;}
  index=Math.max(0,filtered.findIndex(c=>c.case_id===keep));await load(index);
}
async function load(i){
  if(busy||loading||!filtered.length)return;loading=true;document.body.dataset.loaded='';controls();
  try{
    index=Math.max(0,Math.min(i,filtered.length-1));entry=filtered[index];current=await json(`data/${entry.case_id}.json`);$('caseSelect').value=entry.case_id;
    $('title').textContent=entry.case_id;$('identity').textContent=`Target ${current.feature.id} · original (${current.feature.point.join(', ')}) · ${entry.split}`;
    $('priority').textContent=entry.priority_reason?`Why Start Here: ${entry.priority_reason}`:`Situation: ${entry.categories.join(', ')}`;
    $('proposal').value='A';$('proposal').options[1].disabled=!current.B;$('differences').disabled=!current.B;$('old').disabled=!current.baseline;
    $('ownershipView').checked=false;$('ownership').hidden=true;$('internal').checked=false;$('seamsOnly').checked=false;hidden=false;$('hide').textContent='Hide all marks · H';
    $('raw').src=`crops/${entry.case_id}.png`;$('nativeLink').href=$('raw').src;$('dataLink').href=`data/${entry.case_id}.json`;
    $('rawInfo').textContent=`Exact native crop (${current.box.join(', ')}), exclusive upper endpoints. Original image ${current.photo.photo_sha256.slice(0,16)}…`;
    img=new Image();img.src=$('raw').src;await img.decode();fit();renderEvidence();renderKnown();$('error').textContent='';$('message').textContent='';
    document.body.dataset.loaded=entry.case_id;location.hash=entry.case_id;if(window.r293ReviewLoaded)$('reviewAnchor').scrollIntoView({block:'start'});else{window.r293ReviewLoaded=true;window.scrollTo(0,0);}
  }finally{loading=false;controls();if(current)renderAnswers();}
}
function controls(){for(const id of navigation)$(id).disabled=busy||loading;document.querySelectorAll('[data-answer]').forEach(b=>b.disabled=busy||loading||current?.read_only_historical||(b.dataset.answer==='B'&&!current?.B));document.querySelectorAll('#diagnostics input,#ownership select').forEach(e=>e.disabled=busy||loading);}
function visible(p){return p[0]>=current.box[0]&&p[0]<current.box[2]&&p[1]>=current.box[1]&&p[1]<current.box[3];}
function point(p){return [(p[0]-current.box[0]+.5)*scale+pan[0],(p[1]-current.box[1]+.5)*scale+pan[1]];}
function stroke(c,s,color,dashed=false,width=1.3){const a=point(s.endpoints[0]),b=point(s.endpoints[1]);c.beginPath();c.strokeStyle=color;c.lineWidth=width;c.setLineDash(dashed?[3,3]:[]);c.moveTo(...a);c.lineTo(...b);c.stroke();}
function draw(){
  if(!img||!current)return;const canvas=$('canvas'),v=$('viewport');canvas.width=v.clientWidth;canvas.height=v.clientHeight;const c=canvas.getContext('2d');c.imageSmoothingEnabled=false;c.drawImage(img,pan[0],pan[1],img.width*scale,img.height*scale);
  if(hidden)return;
  const selected=current[$('proposal').value];
  if($('old').checked&&current.baseline)for(const s of current.baseline.A.segments)stroke(c,s,'#d9dcde',true,1);
  if($('internal').checked)for(const s of current.internal_edges)stroke(c,s,'#ea5c67',false,1);
  if(!$('seamsOnly').checked)for(const s of selected.segments)stroke(c,s,s.supported?'#27e6ed':'#ffb342',!s.supported);
  if($('seams').checked||$('seamsOnly').checked)for(const arc of current.separator_arcs){c.beginPath();c.setLineDash(arc.enforced?[]:[3,3]);c.strokeStyle=arc.enforced?'#85fa76':'#f395dd';c.lineWidth=1.2;arc.path.forEach((p,i)=>{const q=point(p);if(i)c.lineTo(...q);else c.moveTo(...q);});c.stroke();c.setLineDash([]);for(const p of [arc.path[0],arc.path.at(-1)]){const q=point(p);c.beginPath();c.arc(...q,2.5,0,Math.PI*2);c.stroke();}}
  if($('differences').checked&&current.B){
    const other=current[$('proposal').value==='A'?'B':'A'];
    for(const s of other.segments){const midpoint=s.endpoints[0].map((x,i)=>(x+s.endpoints[1][i])/2);const shared=selected.segments.some(q=>Math.hypot((q.endpoints[0][0]+q.endpoints[1][0])/2-midpoint[0],(q.endpoints[0][1]+q.endpoints[1][1])/2-midpoint[1])<=1);if(!shared)stroke(c,s,'#d487ff',true,1.5);}
  }
  c.setLineDash([]);const [x,y]=point(current.feature.point);c.strokeStyle='white';c.lineWidth=1.5;c.beginPath();c.arc(x,y,5,0,Math.PI*2);c.stroke();c.shadowColor='black';c.shadowBlur=3;c.font='bold 12px system-ui';c.fillStyle='white';c.fillText('TARGET',x+9,y-8);c.shadowBlur=0;
  if($('ownershipView').checked)current.neighboring_features.forEach((q,i)=>{if(!visible(q.point))return;const [x,y]=point(q.point);c.beginPath();c.arc(x,y,4,0,Math.PI*2);c.stroke();c.font='12px system-ui';c.fillText(String(i+1),x+5,y-5);});
}
function fit(){if(!img)return;const v=$('viewport');scale=.95*Math.min(v.clientWidth/img.width,v.clientHeight/img.height);pan=[(v.clientWidth-img.width*scale)/2,(v.clientHeight-img.height*scale)/2];draw();}
function zoom(f,x=$('viewport').clientWidth/2,y=$('viewport').clientHeight/2){const old=scale;scale=Math.max(.5,Math.min(40,scale*f));pan=[x-(x-pan[0])*scale/old,y-(y-pan[1])*scale/old];draw();}
function summary(k,e){
  switch(k){
    case'T1':return`${e.dark_supported_sides} dark-edge sides; ${e.tracked_separator_arcs} tracked arcs; ${e.enforced_arcs} constrained`;
    case'T2':return`${e.multiscale_sides} tracked illumination edges; ${e.continuity_conflict_sides} continuity conflicts`;
    case'T3':return`${e.material_transition_sides} material-color edges`;
    case'T4':return`${e.other_features_inside.length} other features inside; ownership remains open`;
    case'T5':return`${e.internal_dark_pixels} dark interior pixels; holes/shadows are not automatically filled`;
    case'T6':return`${e.junction_sides} sides near junctions; ${e.termination_sides} near terminating edges`;
    case'T7':return`${Math.round(e.supported_fraction*100)}% locally supported; ${e.mechanism_agreement_sides} sides reinforced by multiple methods`;
    case'T8':return`${Math.round(Math.min(...e.perturbation_IoU)*100)}% minimum overlap under parameter/context changes; all complementary analyses attempted`;
  }
}
function renderEvidence(){
  const p=current[$('proposal').value];$('status').textContent=`${$('proposal').value} · ${p.status}`;$('reasons').textContent=p.reasons.join(' ')+(current.analysis_limit_reached?' The analysis limit was reached; the image-window frame is not a discovered edge.':'');
  $('alternative').textContent=current.B?current.alternative_explanation:'No meaningfully different B contour arose from the complementary evidence.';
  $('evidence').replaceChildren(...Object.entries(p.evidence).map(([k,e])=>{const d=document.createElement('details'),s=document.createElement('summary'),pre=document.createElement('pre');s.textContent=`${k} · ${names[k]} — ${summary(k,e)}`;pre.textContent=JSON.stringify(e,null,2);d.append(s,pre);return d;}));
  const q=current.comparison;
  $('comparison').textContent=q?`R291 ${q.old_pixels} → R293 ${q.new_pixels} candidate pixels. ${q.crossings_before} → ${q.crossings_after} measured valley straddles; ${q.routed_around_after} remaining paired banks in the source-connected region. Other-feature inclusions removed ${q.other_feature_inclusions_removed.length}, added ${q.other_feature_inclusions_added.length}. These are diagnostic, not known ownership or accuracy.`:'No detector revision in R293. New targets assess unchanged R292 on the frozen central population; old judgments remain read-only.';
  const arcs=current.separator_arcs;$('separatorInfo').textContent=`${arcs.length} observed arcs; ${arcs.filter(a=>a.enforced).length} constrained. Endings stay unresolved. Separators only hides the proposed outer contour so you can judge the photographic measurement separately.`;
  const prior=current.historical_reviews||[];$('previousReview').textContent=prior.length?`Read-only historical judgments: ${prior.map(h=>h.experiment+' '+h.answer).join('; ')}. The proposal is unchanged from the previously delivered inference; no repeat answer is requested.`:'New frozen well-observed centerline target. Judge visible material/reflection only; a complete physical silhouette is not required.';
  const p0=current.position_measurements;$('positionInfo').textContent=`Independent unweighted patch location (${p0.independent_bright_patch.map(v=>v.toFixed(2)).join(', ')}); original weighted alternative (${p0.weighted_patch_alternative.map(v=>v.toFixed(2)).join(', ')}) · threshold sensitivity ${p0.patch_threshold_sensitivity_px.toFixed(2)}px (not a confidence interval). Candidate region centroid (${p0.candidate_visible_region_centroid.map(v=>v.toFixed(2)).join(', ')}) remains a hypothesis. Physical center and identity unknown.`;
  draw();
}
function renderKnown(){
  $('knownEvidence').replaceChildren();for(const e of current.prior_user_evidence){const p=document.createElement('p');p.textContent=`Preserved user evidence: ${e.statement} (${e.id}). This is not a new boundary judgment.`;$('knownEvidence').append(p);}
}
function renderOwnership(){
  const container=$('ownership');container.hidden=!$('ownershipView').checked;container.replaceChildren();if(container.hidden)return;
  const h=document.createElement('h3');h.textContent='Optional: do these bright points belong to the target bead?';container.append(h);
  const help=document.createElement('p');help.className='muted compact';help.textContent='Only visible points are listed. A recorded pair is reused across cases; change it only if you want to revise that judgment.';container.append(help);
  current.neighboring_features.forEach((q,i)=>{
    if(!visible(q.point))return;const row=document.createElement('label');row.className='bar compact';const key=pair(current.feature.id,q.feature_id),known=state.ownership[key];row.textContent=`Point ${i+1} · ${q.feature_id} (${q.point.join(', ')})${known?' · already recorded':''} `;
    const s=document.createElement('select');s.setAttribute('aria-label',`Ownership ${q.feature_id}`);s.append(new Option('Unanswered',''));for(const [v,t] of [['same','Same physical bead'],['different','Different beads'],['insufficient','Insufficient photograph'],['not-sure','Not sure']])s.append(new Option(t,v));s.value=known?.value||'';s.disabled=busy||current?.read_only_historical;
    s.onchange=()=>{const v=payload();if(s.value)v.ownership[q.feature_id]=s.value;else delete v.ownership[q.feature_id];save(v).catch(fail);};row.append(s);container.append(row);
  });
}
function renderAnswers(){
  controls();const p=payload();document.querySelectorAll('[data-answer]').forEach(b=>b.setAttribute('aria-pressed',String(p.answer===b.dataset.answer)));
  document.querySelectorAll('#diagnostics input').forEach(e=>{e.checked=(p.diagnostics||[]).includes(e.value);e.disabled=busy||current?.read_only_historical;});
  $('diagnosticsPanel').open=['partial','wrong-clear'].includes(p.answer);$('undo').disabled=busy||!state.cases[entry.case_id]?.revision;renderOwnership();
  $('history').replaceChildren(...history.filter(e=>e.case_id===entry.case_id).map(e=>{const p=document.createElement('p');p.className='compact';p.textContent=`Revision ${e.revision} · ${e.utc} · ${e.action}: ${JSON.stringify(e.payload)}`;return p;}));progress();
}
async function save(value,action='assessment'){
  if(busy||loading||current?.read_only_historical)return;busy=true;controls();$('undo').disabled=true;$('message').textContent='Saving…';const id=entry.case_id;
  try{state=await json('/api/judgment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({case_id:id,candidate_digest:entry.candidate_digest,expected_revision:state.cases[id]?.revision||0,payload:value,action})});history=await json('/api/history');$('message').textContent=`Saved revision ${state.cases[id].revision}. You can move on.`;}
  finally{busy=false;renderAnswers();}
}
for(const id of ['playlist','category','unreviewed'])$(id).onchange=()=>refresh(entry?.case_id).catch(fail);
$('caseSelect').onchange=()=>load(filtered.findIndex(c=>c.case_id===$('caseSelect').value)).catch(fail);
$('prev').onclick=()=>load(index-1).catch(fail);$('next').onclick=()=>load(index+1).catch(fail);
$('prevBottom').onclick=()=>$('prev').click();$('nextBottom').onclick=()=>$('next').click();
$('nextOpen').onclick=()=>{const list=selectEntries(),after=list.findIndex(c=>c.case_id===entry.case_id);const q=list.find((c,i)=>i>after&&!c.historical_review&&!state.cases[c.case_id]?.payload.answer)||list.find(c=>!c.historical_review&&!state.cases[c.case_id]?.payload.answer);if(q)load(filtered.findIndex(c=>c.case_id===q.case_id)).catch(fail);else $('message').textContent='This review set is finished. The remaining cases are optional.';};
document.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{const p=payload();p.answer=b.dataset.answer;save(p).catch(fail);});
document.querySelectorAll('#diagnostics input').forEach(e=>e.onchange=()=>{const p=payload();p.diagnostics=[...document.querySelectorAll('#diagnostics input:checked')].map(e=>e.value);save(p).catch(fail);});
$('undo').onclick=()=>save(payload(),'undo').catch(fail);
$('reload').onclick=async()=>{try{state=await json('/api/state');history=await json('/api/history');renderAnswers();$('message').textContent='Saved answers reloaded.';}catch(e){fail(e);}};
$('export').onclick=async()=>{try{const data=await json('/api/export'),url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'})),a=document.createElement('a');a.href=url;a.download='r293-feedback-history.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){fail(e);}};
$('hide').onclick=()=>{hidden=!hidden;$('hide').textContent=hidden?'Restore marks · H':'Hide all marks · H';draw();};
$('locate').onclick=()=>{hidden=false;$('hide').textContent='Hide all marks · H';fit();};
$('proposal').onchange=renderEvidence;for(const id of ['differences','old','internal','seams','seamsOnly'])$(id).onchange=draw;
$('ownershipView').onchange=()=>{renderOwnership();draw();};$('zoomIn').onclick=()=>zoom(1.4);$('zoomOut').onclick=()=>zoom(1/1.4);$('reset').onclick=fit;
$('native').onclick=()=>{scale=1;pan=[($('viewport').clientWidth-img.width)/2,($('viewport').clientHeight-img.height)/2];draw();};
$('viewport').onwheel=e=>{e.preventDefault();const r=$('viewport').getBoundingClientRect();zoom(e.deltaY<0?1.15:1/1.15,e.clientX-r.left,e.clientY-r.top);};
$('viewport').onpointerdown=e=>{drag=[e.clientX,e.clientY,...pan];$('viewport').setPointerCapture(e.pointerId);};
$('viewport').onpointerup=$('viewport').onpointercancel=()=>drag=null;
$('viewport').onpointermove=e=>{
  if(drag){pan=[drag[2]+e.clientX-drag[0],drag[3]+e.clientY-drag[1]];draw();return;}
  if(!current||hidden)return;const r=$('viewport').getBoundingClientRect(),x=(e.clientX-r.left-pan[0])/scale+current.box[0]-.5,y=(e.clientY-r.top-pan[1])/scale+current.box[1]-.5;
  let nearest=null,distance=2;for(const s of current[$('proposal').value].segments){const d=Math.hypot((s.endpoints[0][0]+s.endpoints[1][0])/2-x,(s.endpoints[0][1]+s.endpoints[1][1])/2-y);if(d<distance){distance=d;nearest=s;}}
  $('edgeDetail').textContent=nearest?`${nearest.supported?'Locally supported':'Uncertain'} · ${nearest.methods.join('; ')}${nearest.stable?'':' · position changes under perturbation'}`:'Photographic evidence for the pointed edge appears here.';
};
window.onresize=fit;window.onkeydown=e=>{if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight')$('next').click();if(e.key==='ArrowLeft')$('prev').click();if(/^[1-6]$/.test(e.key))document.querySelector(`[data-answer="${answerKeys[Number(e.key)-1]}"]`).click();if(e.key.toLowerCase()==='h')$('hide').click();};
(async()=>{
  manifest=await json('manifest.json');$('playlist').querySelector('[value="start"]').textContent=`Start Here · ${manifest.start_here.length} cases`;state=await json('/api/state');history=await json('/api/history');
  [...new Set(manifest.cases.flatMap(c=>c.categories))].sort().forEach(c=>$('category').append(new Option(c,c)));
  $('batch').replaceChildren(...manifest.cases.map(c=>{const b=document.createElement('button');b.textContent=c.case_id;b.onclick=()=>{$('playlist').value='all';$('category').value='';$('unreviewed').checked=false;refresh(c.case_id).catch(fail);};return b;}));
  $('preservedReferences').replaceChildren(...manifest.cases.filter(c=>c.historical_review).map(c=>{const p=document.createElement('p');p.className='compact';p.textContent=`${c.case_id}: latest historical answer ${c.historical_answer} · unchanged inference; no repeat question`;return p;}));
  const id=decodeURIComponent(location.hash.slice(1));if(id&&!manifest.start_here.includes(id))$('playlist').value='all';await refresh(id||manifest.start_here[0]);
})().catch(e=>fail(Error(`Launch the local R293 server with launch.sh. ${e.message}`)));

window.openCoverageCase=async cid=>{$('playlist').value='all';$('category').value='';$('unreviewed').checked=false;await refresh(cid);$('title').scrollIntoView({behavior:'smooth',block:'start'});};

$('jumpReview').onclick=()=>$('reviewAnchor').scrollIntoView({behavior:'smooth',block:'start'});$('jumpOverview').onclick=()=>window.scrollTo({top:0,behavior:'smooth'});
