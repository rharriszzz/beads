'use strict';
const $=id=>document.getElementById(id), answers=['A','B','neither','insufficient','not-sure'];
let manifest,states={},events=[],filtered=[],index=0,current,entry,img,scale=5,pan=[0,0],drag=null,saving=false,loading=false;
const names={T1:'Coherent darkness',T2:'Brightness continuity',T3:'Color continuity',T4:'Competing highlights',T5:'Internal darkness',T6:'Occlusion evidence',T7:'Boundary completeness',T8:'Measurement reliability'};
async function json(url,options){const r=await fetch(url,options);const d=await r.json();if(!r.ok)throw Error(d.error||r.statusText);return d;}
function fail(e){$('error').textContent=e.message||String(e);}
function payload(){return structuredClone(states[entry.case_id]?.payload||{answer:null,ownership:{}});}
function filteredEntries(){return manifest.cases.filter(c=>(!$('split').value||c.split===$('split').value)&&(!$('category').value||c.categories.includes($('category').value))&&(!$('unreviewed').checked||!states[c.case_id]?.payload.answer));}
function refreshList(keep){filtered=filteredEntries();$('caseSelect').replaceChildren(...filtered.map((c,i)=>new Option(`${i+1}/${filtered.length} · ${c.case_id}${states[c.case_id]?.payload.answer?' ✓':''}`,c.case_id)));index=Math.max(0,filtered.findIndex(c=>c.case_id===keep));if(filtered.length)load(index).catch(fail);else{$('message').textContent='No cases match this filter.';}$('progress').textContent=`${Object.values(states).filter(s=>s.payload.answer).length} / ${manifest.cases.length} answered`;}
async function load(i) {
  if (saving || loading) return;
  loading = true;
  document.body.dataset.loaded = '';
  const controls = ['prev','next','caseSelect','nextOpen','split','category','unreviewed'];
  controls.forEach(id => $(id).disabled = true);
  document.querySelectorAll('[data-answer]').forEach(b => b.disabled = true);
  try {
    index = Math.max(0, Math.min(i, filtered.length - 1));
    entry = filtered[index];
    if (!entry) return;
    $('caseSelect').value = entry.case_id;
    current = await json(`data/${entry.case_id}.json`);
    $('title').textContent = entry.case_id;
    $('identity').textContent = `${current.feature.id} · native (${current.feature.point.join(', ')}) · ${entry.split} · ${current.algorithm}`;
    const correction = current.provenance_correction;
    $('selection').textContent = `Historical selection anchor (${current.selection_anchor.join(', ')}), ${current.selection_anchor_distance_px.toFixed(2)}px from the chosen independent feature. This association is unverified. Categories: ${entry.categories.join(', ')}.` + (correction ? ` Provenance correction: ${correction.explanation}` : '');
    $('proposal').options[1].disabled = !current.B;
    $('proposal').value = 'A';
    $('raw').src = `crops/${entry.case_id}.png`;
    $('nativeLink').href = $('raw').src;
    $('dataLink').href = `data/${entry.case_id}.json`;
    $('rawInfo').textContent = `Exact decoded native crop ${current.box.join(', ')} (x1/y1 exclusive). Image SHA256 ${current.photo.photo_sha256.slice(0,16)}…`;
    img = new Image(); img.src = $('raw').src; await img.decode();
    fit(); renderInfo();
    $('error').textContent = ''; $('message').textContent = '';
    location.hash = entry.case_id;
    document.body.dataset.loaded = entry.case_id;
  } finally {
    loading = false;
    controls.forEach(id => $(id).disabled = false);
    if (current) renderAnswers();
  }
}
function fit(){const v=$('viewport');scale=Math.min(v.clientWidth/img.width,v.clientHeight/img.height)*.95;pan=[(v.clientWidth-img.width*scale)/2,(v.clientHeight-img.height*scale)/2];draw();}
function visiblePoint(p){return p[0]>=current.box[0] && p[0]<current.box[2] && p[1]>=current.box[1] && p[1]<current.box[3];}
function point(p){return [(p[0]-current.box[0]+.5)*scale+pan[0],(p[1]-current.box[1]+.5)*scale+pan[1]];}
function draw(){if(!img||!current)return;const cv=$('canvas'),v=$('viewport');cv.width=v.clientWidth;cv.height=v.clientHeight;const c=cv.getContext('2d');c.imageSmoothingEnabled=false;c.drawImage(img,pan[0],pan[1],img.width*scale,img.height*scale);const candidate=current[$('proposal').value];if($('overlay').checked){for(const s of candidate.segments){c.beginPath();c.strokeStyle=s.supported?'#27e6ed':'#ffb342';c.lineWidth=1.25;c.setLineDash(s.supported?[]:[3,3]);const a=point(s.endpoints[0]),b=point(s.endpoints[1]);c.moveTo(...a);c.lineTo(...b);c.stroke();}}c.setLineDash([]);if($('features').checked){c.strokeStyle='white';c.lineWidth=1.5;const [x,y]=point(current.feature.point);c.beginPath();c.moveTo(x-6,y);c.lineTo(x+6,y);c.moveTo(x,y-6);c.lineTo(x,y+6);c.stroke();current.neighboring_features.forEach((q,i)=>{if(!visiblePoint(q.point))return;const [x,y]=point(q.point);c.beginPath();c.arc(x,y,5,0,Math.PI*2);c.stroke();c.font='12px system-ui';c.fillStyle='white';c.fillText(i+1,x+6,y-6);});const p=point(current.selection_anchor);c.strokeStyle='#aaa';c.strokeRect(p[0]-4,p[1]-4,8,8);}}
function evidenceSummary(key, e, total) {
  switch(key) {
    case 'T1': return `${e.sustained_dark_sides}/${total} sides have sustained darkness`;
    case 'T2': return `${e.recovering_valley_sides} recovering valleys; ${e.continuous_material_cut_sides} sides cut bright continuity`;
    case 'T3': return `${e.chromatic_sides} coherent color-transition sides`;
    case 'T4': return `${e.other_features_inside.length} other bright features inside; ownership unresolved`;
    case 'T5': return `${e.internal_dark_pixels} dark interior pixels; hole/shadow/separation unresolved`;
    case 'T6': return `${e.color_or_step_sides} possible occlusion-edge sides; occluder unknown`;
    case 'T7': return `${Math.round(e.supported_fraction*100)}% supported; ${e.supported_arcs} supported arcs, ${e.unresolved_arcs} unresolved groups`;
    case 'T8': return `${Math.round(Math.min(...e.perturbation_IoU)*100)}% minimum overlap under parameter/context changes; ${e.reflection_edge_ambiguous?'reflection-edge ambiguity':'material evidence available'}`;
  }
}
function renderInfo() {
  const p = current[$('proposal').value];
  $('status').textContent = `${$('proposal').value}: ${p.status}`;
  $('reasons').textContent = p.reasons.join(' ').replace('Unsupported contour sides remain unresolved; optimizer closure is not accepted.', 'Some contour segments lack sufficient photographic edge evidence and remain unresolved.');
  $('evidence').replaceChildren(...Object.entries(p.evidence).map(([k,v]) => {
    const d = document.createElement('details'), summary = document.createElement('summary');
    summary.textContent = `${k} · ${names[k]} — ${evidenceSummary(k,v,p.evidence.T7.total_sides)}`;
    const pre = document.createElement('pre'); pre.textContent = JSON.stringify(v,null,2);
    d.append(summary,pre); return d;
  }));
  draw();
}
function renderAnswers(){['prev','next','caseSelect','nextOpen','split','category','unreviewed'].forEach(id=>$(id).disabled=saving||loading);const p=payload();document.querySelectorAll('[data-answer]').forEach(b=>{b.setAttribute('aria-pressed',String(p.answer===b.dataset.answer));b.disabled=saving||(b.dataset.answer==='B'&&!current.B);});$('ownership').replaceChildren();if(current.neighboring_features.length){const h=document.createElement('h3');h.textContent='Bright-point ownership (optional; independent of contour answer)';$('ownership').append(h);current.neighboring_features.forEach((q,i)=>{if(!visiblePoint(q.point))return;const row=document.createElement('label');row.className='bar';row.textContent=`Point ${i+1}: ${q.feature_id} (${q.point.join(', ')}) versus target `;const s=document.createElement('select');s.setAttribute('aria-label',`Ownership ${q.feature_id}`);s.append(new Option('Unanswered',''));for(const [v,t] of [['same','Same physical bead'],['different','Different beads'],['insufficient','Insufficient photograph'],['not-sure','Not sure']])s.append(new Option(t,v));s.value=p.ownership[q.feature_id]||'';s.disabled=saving;s.onchange=()=>{const v=payload();if(s.value)v.ownership[q.feature_id]=s.value;else delete v.ownership[q.feature_id];save(v).catch(fail);};row.append(s);$('ownership').append(row);});}$('undo').disabled=saving||!states[entry.case_id]?.revision;const es=events.filter(e=>e.case_id===entry.case_id);$('history').replaceChildren(...es.map(e=>{const p=document.createElement('p');p.textContent=`Revision ${e.revision} · ${e.utc} · ${e.action}: ${JSON.stringify(e.payload)}`;return p;}));}
async function save(value,action='answer'){if(saving||loading)return;saving=true;renderAnswers();const id=entry.case_id;try{const state=await json('/api/judgment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({case_id:id,candidate_digest:entry.candidate_digest,expected_revision:states[id]?.revision||0,payload:value,action})});states[id]=state;const exported=await json('/api/export');events=exported.events;$('message').textContent=`Saved revision ${state.revision} to disk.`;$('progress').textContent=`${Object.values(states).filter(s=>s.payload.answer).length} / ${manifest.cases.length} answered`;}finally{saving=false;renderAnswers();}}
function zoom(factor,x=$('viewport').clientWidth/2,y=$('viewport').clientHeight/2){const old=scale;scale=Math.max(.5,Math.min(40,scale*factor));pan=[x-(x-pan[0])*scale/old,y-(y-pan[1])*scale/old];draw();}
$('prev').onclick=()=>load(index-1).catch(fail);$('next').onclick=()=>load(index+1).catch(fail);$('caseSelect').onchange=()=>load(filtered.findIndex(c=>c.case_id===$('caseSelect').value)).catch(fail);for(const id of ['split','category','unreviewed'])$(id).onchange=()=>refreshList(entry?.case_id);
$('nextOpen').onclick=()=>{const c=manifest.cases.find((c,i)=>i>manifest.cases.findIndex(c=>c.case_id===entry.case_id)&&!states[c.case_id]?.payload.answer)||manifest.cases.find(c=>!states[c.case_id]?.payload.answer);if(c){$('split').value='';$('category').value='';$('unreviewed').checked=false;refreshList(c.case_id);}};
document.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{const p=payload();p.answer=b.dataset.answer;save(p).catch(fail);});$('undo').onclick=()=>save(payload(),'undo').catch(fail);$('reload').onclick=async()=>{try{states=await json('/api/state');events=(await json('/api/export')).events;renderAnswers();$('message').textContent='Saved answers reloaded.';}catch(e){fail(e);}};
$('export').onclick=async()=>{try{const d=await json('/api/export');const url=URL.createObjectURL(new Blob([JSON.stringify(d,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='r290-feedback-history.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(e){fail(e);}};
$('proposal').onchange=renderInfo;for(const id of ['overlay','features'])$(id).onchange=draw;$('zoomIn').onclick=()=>zoom(1.4);$('zoomOut').onclick=()=>zoom(1/1.4);$('reset').onclick=fit;$('native').onclick=()=>{scale=1;pan=[($('viewport').clientWidth-img.width)/2,($('viewport').clientHeight-img.height)/2];draw();};
$('viewport').onwheel=e=>{e.preventDefault();const r=$('viewport').getBoundingClientRect();zoom(e.deltaY<0?1.15:1/1.15,e.clientX-r.left,e.clientY-r.top);};$('viewport').onpointerdown=e=>{drag=[e.clientX,e.clientY,...pan];$('viewport').setPointerCapture(e.pointerId);};$('viewport').onpointerup=()=>drag=null;$('viewport').onpointermove=e=>{if(drag){pan=[drag[2]+e.clientX-drag[0],drag[3]+e.clientY-drag[1]];draw();}else if(current){const rect=$('viewport').getBoundingClientRect(),x=(e.clientX-rect.left-pan[0])/scale+current.box[0]-.5,y=(e.clientY-rect.top-pan[1])/scale+current.box[1]-.5;let nearest=null,dist=2;for(const s of current[$('proposal').value].segments){const a=s.endpoints[0],b=s.endpoints[1],d=Math.hypot((a[0]+b[0])/2-x,(a[1]+b[1])/2-y);if(d<dist){dist=d;nearest=s;}}$('edgeDetail').textContent=nearest?`${nearest.supported?'Supported photographic edge':'Unresolved segment'}: ${nearest.reasons.join('; ')}\n${JSON.stringify(nearest.evidence)}`:'';}};
window.onresize=draw;window.onkeydown=e=>{if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName))return;if(e.key==='ArrowRight')$('next').click();if(e.key==='ArrowLeft')$('prev').click();if(/^[1-5]$/.test(e.key))document.querySelector(`[data-answer="${answers[Number(e.key)-1]}"]`).click();};
(async()=>{manifest=await json('manifest.json');states=await json('/api/state');events=(await json('/api/export')).events;const cats=[...new Set(manifest.cases.flatMap(c=>c.categories))].sort();cats.forEach(c=>$('category').append(new Option(c,c)));$('batch').replaceChildren(...manifest.cases.map(c=>{const b=document.createElement('button');b.textContent=c.case_id;b.onclick=()=>{$('split').value='';$('category').value='';$('unreviewed').checked=false;refreshList(c.case_id);};return b;}));refreshList(decodeURIComponent(location.hash.slice(1))||manifest.cases[0].case_id);})().catch(e=>fail(Error(`Start the local review server using launch.sh. ${e.message}`)));
