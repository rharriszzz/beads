import {toSource, toScreen, zoomAt, fitView, resizeView, guideEdges, RequestGate} from './viewport.mjs';
import {Marks, hitMark, isClick} from './marks.mjs';
import {scoreBounds, constrainScoreView, zoomScore, panScore, fitScoreY, nearestScore} from './score_view.mjs';

const $ = id => document.getElementById(id);
const canvas = $('canvas'), ctx = canvas.getContext('2d');
for (const element of document.querySelectorAll('button,input,select')) element.disabled=true;
const gate = new RequestGate();
let config, image, frame, view, width = 0, height = 0, drag = null, timer, controller;
let requestedCount, requestedHand, saving = false;
let widthPercent=107;
let marks, centerDoc, selected=null, moving=false, savedVersion=0, savingCenters=null;
let matches=null, matchRequest=0, score=null, scoreJob=null, plotting=false;
let scoreView=null, graphDrag=null;
const angles = Array.from({length: 49}, (_, i) => [Math.cos(i*Math.PI/24), Math.sin(i*Math.PI/24)]);
function status(message, error=false) {
  $('status').textContent = message; $('status').classList.toggle('error', error);
}
function current() { return frame && frame.count === requestedCount && frame.hand === requestedHand; }
function buttons() {
  $('save').disabled = !current() || saving;
  $('png').disabled = $('json').disabled = !current();
}
function drawCircles(context, circles, transform, alpha=1) {
  context.save(); context.globalAlpha = alpha; context.strokeStyle = '#00ffff'; context.lineWidth = 1;
  context.beginPath();
  for (const [cx,cy,ax,ay,bx,by] of circles) {
    for (let i=0; i<angles.length; i++) {
      const [c,s] = angles[i];
      const x = (cx+ax*c+bx*s)*transform.scale+transform.x;
      const y = (cy+ay*c+by*s)*transform.scale+transform.y;
      if (i===0) context.moveTo(x,y); else context.lineTo(x,y);
    }
  }
  context.stroke(); context.restore();
}
function guideSettings() {
  return {width_percent:widthPercent,show_edges:$('edges').checked,show_centerline:$('centerline').checked};
}
function drawGuides(context, guides, transform, settings, alpha=1) {
  context.save();context.globalAlpha=alpha;context.lineWidth=1;
  function lines(paths,color,dashes=[]) {
    context.strokeStyle=color;context.setLineDash(dashes);context.beginPath();
    for(const path of paths) for(let i=0;i<path.length;i++) {
      const [x,y]=path[i],sx=x*transform.scale+transform.x,sy=y*transform.scale+transform.y;
      if(i===0)context.moveTo(sx,sy);else context.lineTo(sx,sy);
    }
    context.stroke();
  }
  if(settings.show_centerline)lines([guides.centerline],'#ffffff',[5,5]);
  if(settings.show_edges) {
    lines(guideEdges(guides,100),'#ffb347',[7,3]);
    if(settings.width_percent!==100)lines(guideEdges(guides,settings.width_percent),'#80ff80');
  }
  context.restore();
}
function render() {
  if (!image || !view) return;
  const dpr = window.devicePixelRatio || 1;
  ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,width,height);
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(image,view.x,view.y,image.naturalWidth*view.scale,image.naturalHeight*view.scale);
  if(frame)drawGuides(ctx,frame.guides,view,guideSettings(),current()?1:.3);
  if (frame && $('show').checked) drawCircles(ctx,frame.circles,view,current()?1:.3);
  if($('show-matches').checked && matches && current())drawMatches(ctx,matches,view);
  if(marks && $('show-marks').checked)drawMarks(ctx,marks.points,view);
  $('zoom').textContent = `${Math.round(view.scale*100)}%`;
}
function resize() {
  const oldSize = {width,height};
  width = $('stage').clientWidth; height = $('stage').clientHeight;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = Math.round(width*dpr); canvas.height = Math.round(height*dpr);
  if (view) view = resizeView(view,oldSize,{width,height});
  else if (image) view = config.initial_view || fitView(width,height,[0,0,...config.source.oriented_size]);
  render();
}
function point(event) {
  const rect = canvas.getBoundingClientRect();
  return {x:event.clientX-rect.left,y:event.clientY-rect.top};
}
function zoom(factor,pivot={x:width/2,y:height/2}) { if(view) { view=zoomAt(view,pivot,factor); render(); } }
function schedule(count, hand=requestedHand) {
  if (!Number.isInteger(count) || count < config.allowed_range[0] || count > config.allowed_range[1]) {
    status(`Choose a whole count from ${config.allowed_range[0]} to ${config.allowed_range[1]}.`,true); return;
  }
  requestedCount=count; requestedHand=hand;
  if (count < +$('slider').min) $('slider').min=$('minimum').value=count;
  if (count > +$('slider').max) $('slider').max=$('maximum').value=count;
  $('count').value=$('slider').value=count; $('hand').value=hand;
  const generation=gate.invalidate(); controller?.abort(); clearTimeout(timer);
  buttons(); render();
  status(`Calculating ${count.toLocaleString()} beads, helicity ${hand>0?'+1':'−1'}…${frame?' Previous circles are dimmed.':''}`);
  timer=setTimeout(()=>loadFrame(generation,count,hand),160);
}
async function loadFrame(generation,count,hand) {
  const activeController=new AbortController(); controller=activeController;
  try {
    const response=await fetch(`/api/frame?count=${count}&hand=${hand}`,{signal:activeController.signal});
    const result=await response.json(); if (!response.ok) throw new Error(result.error || 'Could not calculate circles.');
    if(!result.guides)throw new Error('Restart the Python viewer to enable width guides, then reload this page.');
    if (!gate.accepts(generation)) return;
    frame=result; matches=null; buttons(); render();refreshMatches();
    status(`Showing ${count.toLocaleString()} beads · helicity ${hand>0?'+1':'−1'} · ${result.visible_anchors.toLocaleString()} cyan circles`);
  } catch(error) {
    if(error.name!=='AbortError' && gate.accepts(generation)) status(error.message,true);
  }
}
function download(blob, filename) {
  const url=URL.createObjectURL(blob), link=document.createElement('a');
  link.href=url; link.download=filename; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('slider').addEventListener('input',()=>schedule(+$('slider').value));
$('count').addEventListener('change',()=>schedule(+$('count').value));
$('count').addEventListener('keydown',event=>{if(event.key==='Enter') {event.preventDefault();schedule(+$('count').value);}});
$('hand').addEventListener('change',()=>schedule(requestedCount,+$('hand').value));
$('original').onclick=()=>schedule(2698); $('increased').onclick=()=>schedule(2833);
$('range').onclick=()=>{
  const min=+$('minimum').value,max=+$('maximum').value;
  if(!Number.isInteger(min)||!Number.isInteger(max)||min>=max||min<config.allowed_range[0]||max>config.allowed_range[1]) {
    status(`Use a range within ${config.allowed_range[0]}–${config.allowed_range[1]}, with From smaller than To.`,true); return;
  }
  $('slider').min=min; $('slider').max=max;
  schedule(Math.max(min,Math.min(max,requestedCount)));
};
$('fit').onclick=()=>{view=fitView(width,height,[0,0,...config.source.oriented_size]);render();};
$('patch').onclick=()=>{view=fitView(width,height,config.starting_patch);render();};
$('one').onclick=()=>zoom(1/view.scale); $('in').onclick=()=>zoom(1.25); $('out').onclick=()=>zoom(.8);
$('show').onchange=render;
$('edges').onchange=$('centerline').onchange=render;
function changeWidth(value) {
  if(!Number.isFinite(value) || value<config.width_range[0] || value>config.width_range[1]) {
    status('Choose a guide width between 80% and 130%.',true);return;
  }
  widthPercent=value;$('width').value=$('width-slider').value=value;render();
}
$('width-slider').oninput=()=>changeWidth(+$('width-slider').value);
$('width').onchange=()=>changeWidth(+$('width').value);
$('width').onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();changeWidth(+$('width').value);}};
$('width-original').onclick=()=>changeWidth(100);$('width-seven').onclick=()=>changeWidth(107);
canvas.addEventListener('wheel',event=>{
  event.preventDefault();
  const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?height:1);
  zoom(Math.exp(-Math.max(-600,Math.min(600,delta))*.0015),point(event));
},{passive:false});
canvas.addEventListener('pointerdown',event=>{
  if(event.button!==0 || !view) return;
  const p=point(event); drag={id:event.pointerId,x:p.x,y:p.y,start:{...view},travel:0};
  canvas.setPointerCapture(event.pointerId); canvas.classList.add('dragging');
});
canvas.addEventListener('pointermove',event=>{
  if(!drag || drag.id!==event.pointerId) return;
  const p=point(event);drag.travel=Math.max(drag.travel,Math.hypot(p.x-drag.x,p.y-drag.y));
  if(!isClick(drag.travel))view={...drag.start,x:drag.start.x+p.x-drag.x,y:drag.start.y+p.y-drag.y};render();
});
function stopDrag(event) { if(drag?.id===event.pointerId) {drag=null;canvas.classList.remove('dragging');} }
canvas.addEventListener('pointerup',event=>{
  if(drag?.id===event.pointerId && isClick(Math.max(drag.travel,Math.hypot(point(event).x-drag.x,point(event).y-drag.y))))markClick(point(event));
  stopDrag(event);
});canvas.addEventListener('pointercancel',stopDrag);
canvas.addEventListener('lostpointercapture',stopDrag);
$('save').onclick=async()=>{
  if(!current() || saving) return;
  saving=true;buttons();
  const choice={count:frame.count,hand:frame.hand,view:{...view},guides:guideSettings()};
  try {
    const response=await fetch('/api/choice',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(choice)});
    const result=await response.json();if(!response.ok)throw new Error(result.error || 'Could not save choice.');
    $('saved').textContent=`Saved ${choice.count.toLocaleString()}, helicity ${choice.hand>0?'+1':'−1'}, width guide ${choice.guides.width_percent}% → ${result.path}`;
  } catch(error) { $('saved').textContent=`Save failed: ${error.message}`; }
  finally {saving=false;buttons();}
};
$('json').onclick=()=>{
  if(!current())return;
  download(new Blob([JSON.stringify({...frame.parameters,viewer_guides:guideSettings()},null,2)+'\n'],{type:'application/json'}),`beads-${frame.hand>0?'plus':'minus'}-${frame.count}.json`);
};
$('png').onclick=()=>{
  if(!current())return;
  const selected=frame, output=document.createElement('canvas');
  [output.width,output.height]=config.source.oriented_size;
  const context=output.getContext('2d');context.drawImage(image,0,0);
  drawGuides(context,selected.guides,{x:0,y:0,scale:1},guideSettings());
  if($('show').checked)drawCircles(context,selected.circles,{x:0,y:0,scale:1});
  if($('show-matches').checked && matches)drawMatches(context,matches,{x:0,y:0,scale:1});
  if($('show-marks').checked)drawMarks(context,marks.points,{x:0,y:0,scale:1});
  output.toBlob(blob=>{if(blob)download(blob,`beads-${selected.hand>0?'plus':'minus'}-${selected.count}.png`);},'image/png');
};
new ResizeObserver(resize).observe($('stage'));
async function start() {
  try {
    const response=await fetch('/api/config');config=await response.json();
    if(!response.ok)throw new Error(config.error || 'Could not load viewer.');
    config.width_range ||= [80,130];
    if(!config.centers)throw new Error('Restart the Python viewer for center marking, then reload this page.');
    centerDoc=config.centers;marks=new Marks(centerDoc.points);
    $('score-low').value=config.min_count;$('score-high').value=config.max_count;
    for(const id of ['count','minimum','maximum']) {$(id).min=config.allowed_range[0];$(id).max=config.allowed_range[1];}
    $('minimum').value=$('slider').min=config.min_count;$('maximum').value=$('slider').max=config.max_count;
    const initial=config.initial_guides || {width_percent:107,show_edges:true,show_centerline:true};
    widthPercent=initial.width_percent;$('width').value=$('width-slider').value=widthPercent;
    $('edges').checked=initial.show_edges;$('centerline').checked=initial.show_centerline;
    const loaded=new Image();loaded.src=config.image_url;await loaded.decode();image=loaded;
    for (const element of document.querySelectorAll('button,input,select')) element.disabled=false;
    if(config.saved_score) {
      score=config.saved_score;resetScoreView(true);
      $('score-low').value=score.counts[0];$('score-high').value=score.counts.at(-1);
      $('score-step').value=score.counts[1]-score.counts[0];
      scoreSummary('Restored saved graph.');
    }else $('score-status').textContent=config.score_restore_message || 'Save & plot to calculate the graph.';
    markControls();drawGraph();
    resize();schedule(config.initial_count,config.initial_hand);
  } catch(error) {status(error.message,true);}
}
start();

function drawMarks(context,points,transform) {
  context.save();context.font='bold 13px system-ui';context.lineWidth=3;
  for(const p of points) {
    const {x,y}=toScreen(p,transform);
    context.strokeStyle='#101820';context.strokeText(String(p.number),x+7,y-7);
    context.fillStyle=p.id===selected?'#ffdf40':'#ff944d';context.fillText(String(p.number),x+7,y-7);
    context.beginPath();context.moveTo(x-5,y);context.lineTo(x+5,y);context.moveTo(x,y-5);context.lineTo(x,y+5);
    context.strokeStyle='#101820';context.stroke();context.lineWidth=1.5;
    context.strokeStyle=p.id===selected?'#ffdf40':'#ff944d';context.stroke();context.lineWidth=3;
  }
  context.restore();
}
function drawMatches(context,result,transform) {
  context.save();context.strokeStyle='#ff87d4';context.lineWidth=1;context.setLineDash([3,3]);context.beginPath();
  for(const match of result.matches) {
    const p=marks.points.find(p=>p.id===match.observation_id);if(!p)continue;
    const a=toScreen(p,transform),b=toScreen({x:match.predicted_xy[0],y:match.predicted_xy[1]},transform);
    context.moveTo(a.x,a.y);context.lineTo(b.x,b.y);
  }
  context.stroke();context.restore();
}
function dirty() { return marks && marks.version!==savedVersion; }
function markControls() {
  if(!marks)return;
  const p=marks.points.find(p=>p.id===selected);
  if(!p){selected=null;moving=false;}
  $('mark-number').value=p?.number || '';
  for(const id of ['mark-number','move-mark','delete-mark'])$(id).disabled=!p;
  $('undo-mark').disabled=!marks.history.length;
  $('save-centers').disabled=!!savingCenters;
  $('plot').disabled=plotting || marks.points.length<3;
  $('cancel-score').disabled=!scoreJob;
  $('download-score').disabled=$('download-graph').disabled=!score;
  for(const id of ['fit-graph','fit-scores','best-window','graph-in','graph-out','graph-low','graph-high','graph-range'])$(id).disabled=!score;
  $('move-mark').textContent=moving?'Click new center…':'Move';
  $('mark-status').textContent=`${marks.points.length} center marks · ${dirty()?'unsaved changes':centerDoc.revision?'saved':'not saved yet'}`;
  $('mark-list').replaceChildren();
  for(const point of marks.points) {
    const b=document.createElement('button');b.textContent=point.number;b.classList.toggle('selected',point.id===selected);
    b.title=`Center ${point.number}: ${point.x.toFixed(1)}, ${point.y.toFixed(1)} px`;
    b.onclick=()=>{selected=point.id;moving=false;markControls();render();};$('mark-list').append(b);
  }
  canvas.classList.toggle('marking',$('mark-mode').checked || moving);
}
function marksChanged() {
  matches=null;score=null;scoreView=null;graphDrag=null;drawGraph();markControls();render();refreshMatches();
  $('score-status').textContent=scoreJob?'Centers changed during the scan; its result will belong to the earlier marks.':'Centers changed. Save & plot to update the graph.';
}
function markClick(screen) {
  if(!marks)return;
  const source=toSource(screen,view),hit=hitMark(marks.points,source,view.scale);
  if(!moving && hit){selected=hit;markControls();render();return;}
  if(!moving && !$('mark-mode').checked)return;
  const [w,h]=config.source.oriented_size;
  if(source.x<0||source.y<0||source.x>=w||source.y>=h)return;
  try {
    if(moving){marks.move(selected,source);moving=false;}else selected=marks.add(source);
    marksChanged();
  }catch(error){status(error.message,true);}
}
$('mark-mode').onchange=markControls;$('show-marks').onchange=render;
$('show-matches').onchange=()=>{matches=null;render();refreshMatches();};
$('move-mark').onclick=()=>{moving=!moving;markControls();};
$('delete-mark').onclick=()=>{marks.remove(selected);selected=null;marksChanged();};
$('undo-mark').onclick=()=>{marks.undo();moving=false;marksChanged();};
$('mark-number').onchange=()=>{try{marks.renumber(selected,+$('mark-number').value);marksChanged();}catch(error){status(error.message,true);markControls();}};
$('tools').onclick=()=>{$('center-tools').hidden=!$('center-tools').hidden;$('tools').textContent=$('center-tools').hidden?'Show center tools':'Hide center tools';};
async function api(path,payload) {
  const response=await fetch(path,payload===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
  const result=await response.json();if(!response.ok)throw new Error(result.error || 'Request failed.');return result;
}
async function saveCenters() {
  if(savingCenters){await savingCenters;return dirty()?saveCenters():centerDoc;}
  const version=marks.version;
  const payload={points:structuredClone(marks.points),revision:centerDoc.revision,
    count:requestedCount,hand:requestedHand,guides:guideSettings()};
  savingCenters=api('/api/centers',payload).then(result=>{
    centerDoc=result.document;savedVersion=version;
    $('saved').textContent=`Saved ${centerDoc.points.length} centers → ${result.path}`;return centerDoc;
  });markControls();
  try{return await savingCenters;}finally{savingCenters=null;markControls();}
}
$('save-centers').onclick=()=>saveCenters().catch(error=>{status(`Centers not saved: ${error.message}`,true);});
$('download-centers').onclick=()=>{
  const doc={...centerDoc,revision:centerDoc.revision||1,based_on_revision:centerDoc.revision,
    points:structuredClone(marks.points),draft:dirty(),viewer_reference:{count:requestedCount,hand:requestedHand,guides:guideSettings()}};
  download(new Blob([JSON.stringify(doc,null,2)+'\n'],{type:'application/json'}),'bead-centers.json');
};
window.addEventListener('beforeunload',event=>{if(dirty()){event.preventDefault();event.returnValue='';}});
async function refreshMatches() {
  const request=++matchRequest;
  if(!current()||!marks?.points.length||!$('show-matches').checked)return;
  const version=marks.version,count=frame.count,hand=frame.hand;
  try {
    const result=await api('/api/matches',{points:marks.points,count,hand});
    if(request!==matchRequest||version!==marks.version||!current()||frame.count!==count||frame.hand!==hand)return;
    matches=result;render();
  }catch(error){if(request===matchRequest)status(`Could not match centers: ${error.message}`,true);}
}
function graphViewKey() {return `beads-score-view:${config.source.sha256}:${score.saved_at}`;}
function resetScoreView(restore=false) {
  if(!score)return;
  scoreView=scoreBounds(score.rows);
  if(restore)try {const saved=JSON.parse(localStorage.getItem(graphViewKey()));if(saved)scoreView=constrainScoreView(saved,scoreView);}catch{ /* use full view */ }
}
function setScoreView(next) {
  if(!score)return;
  scoreView=constrainScoreView(next,scoreBounds(score.rows));
  try{localStorage.setItem(graphViewKey(),JSON.stringify(scoreView));}catch{ /* graph still works without storage */ }
  drawGraph();
}
function scoreSummary(prefix='') {
  $('score-status').textContent=`${prefix} ${score.centers.points.length} centers · hand ${score.hand>0?'+1':'−1'} · best sampled count ${score.best.count}: sum ${score.best.sse.toFixed(2)} px², RMS ${score.best.rms_pixels.toFixed(2)} px. This is a fixed-model proxy fit.`;
}
function drawGraph() {
  const graph=$('graph'),context=graph.getContext('2d'),w=graph.clientWidth||306,h=graph.clientHeight||220,dpr=window.devicePixelRatio||1;
  graph.width=Math.round(w*dpr);graph.height=h*dpr;context.setTransform(dpr,0,0,dpr,0,0);
  context.fillStyle='#16212b';context.fillRect(0,0,w,h);context.font='11px system-ui';context.fillStyle='#eef4fa';
  if(!score){context.fillText('No current error graph',45,100);graph.plot=null;return;}
  scoreView ||= scoreBounds(score.rows);
  const rows=score.rows,{xMin:x0,xMax:x1,yMin:y0,yMax:y1}=scoreView;
  const bottom=h-40,left=65,right=w-12,top=40,span=y1-y0;
  const xy=row=>[left+(right-left)*(row.count-x0)/(x1-x0),bottom-(bottom-top)*(row.sse-y0)/span];
  context.fillText(`Σ distance² (px²) · ${score.centers.points.length} marks · hand ${score.hand>0?'+1':'−1'}`,5,15);
  context.fillText(`Best sampled N=${score.best.count} · fixed phase / centerline`,5,29);
  context.strokeStyle='#61788b';context.beginPath();context.moveTo(left,top);context.lineTo(left,bottom);context.lineTo(right,bottom);context.stroke();
  const decimals=Math.max(0,Math.min(7,Math.ceil(-Math.log10(span/4))+1));
  for(let i=0;i<=4;i++) {const v=y0+(y1-y0)*i/4,y=bottom-(bottom-top)*i/4;
    context.fillText(v.toFixed(decimals),3,y+4);
    context.strokeStyle='#61788b55';context.beginPath();context.moveTo(left,y);context.lineTo(right,y);context.stroke();
  }
  for(let i=0;i<=4;i++) {const x=left+(right-left)*i/4,n=x0+(x1-x0)*i/4;context.textAlign=i===0?'left':i===4?'right':'center';context.fillText(n.toFixed(x1-x0<10?1:0),x,bottom+17);}
  context.textAlign='center';context.fillText('Total bead count',(left+right)/2,h-7);context.textAlign='left';
  context.save();context.beginPath();context.rect(left,top,right-left,bottom-top);context.clip();
  context.strokeStyle='#51e9f2';context.beginPath();rows.forEach((r,i)=>{const [x,y]=xy(r);if(i)context.lineTo(x,y);else context.moveTo(x,y);});context.stroke();
  const [x,y]=xy(score.best);context.fillStyle='#ffdf40';context.beginPath();context.arc(x,y,4,0,Math.PI*2);context.fill();
  if(x1-x0<100)for(const row of rows)if(row.count>=x0&&row.count<=x1){const [x,y]=xy(row);context.fillStyle='#51e9f2';context.beginPath();context.arc(x,y,2,0,Math.PI*2);context.fill();}
  context.restore();
  $('graph-low').value=Number(x0.toFixed(2));$('graph-high').value=Number(x1.toFixed(2));
  graph.plot={left,right,top,bottom,x0,x1,y0,y1};
}
function graphRow(event) {
  if(!score)return null;
  const graph=$('graph');if(!graph.plot)return null;
  const {left,right,x0,x1}=graph.plot,x=event.clientX-graph.getBoundingClientRect().left;
  const count=x0+Math.max(0,Math.min(1,(x-left)/(right-left)))*(x1-x0);
  return nearestScore(score.rows,count);
}
function graphPivot(event) {
  const graph=$('graph'),rect=graph.getBoundingClientRect(),p=graph.plot;
  return {x:(event.clientX-rect.left-p.left)/(p.right-p.left),y:(p.bottom-event.clientY+rect.top)/(p.bottom-p.top)};
}
function zoomGraph(factor,pivot={x:.5,y:.5},axes='both') {
  if(score)setScoreView(zoomScore(scoreView,scoreBounds(score.rows),pivot,factor,axes));
}
$('graph').addEventListener('wheel',event=>{
  if(!score)return;event.preventDefault();
  const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?$('graph').clientHeight:1);
  zoomGraph(Math.exp(-Math.max(-600,Math.min(600,delta))*.0015),graphPivot(event),event.shiftKey?'y':event.ctrlKey?'x':'both');
},{passive:false});
$('graph').addEventListener('pointerdown',event=>{
  if(!score||event.button!==0)return;
  graphDrag={id:event.pointerId,x:event.clientX,y:event.clientY,view:{...scoreView},plot:{...$('graph').plot},travel:0};
  $('graph').setPointerCapture(event.pointerId);
});
$('graph').addEventListener('pointermove',event=>{
  if(graphDrag?.id===event.pointerId) {
    const d=graphDrag,p=d.plot,dx=event.clientX-d.x,dy=event.clientY-d.y;
    d.travel=Math.max(d.travel,Math.hypot(dx,dy));
    if(!isClick(d.travel))setScoreView(panScore(d.view,scoreBounds(score.rows),-dx*(p.x1-p.x0)/(p.right-p.left),dy*(p.y1-p.y0)/(p.bottom-p.top)));
  }
  const row=graphRow(event);if(row)$('graph-readout').textContent=`Count ${row.count} · sum ${row.sse.toFixed(3)} px² · RMS ${row.rms_pixels.toFixed(3)} px`;
});
$('graph').addEventListener('pointerup',event=>{
  if(graphDrag?.id!==event.pointerId)return;
  if(isClick(Math.max(graphDrag.travel,Math.hypot(event.clientX-graphDrag.x,event.clientY-graphDrag.y)))){
    const row=graphRow(event);if(row){$('show-matches').checked=true;schedule(row.count,score.hand);if($('score-dialog').open)$('score-dialog').close();}
  }
  graphDrag=null;
});
for(const name of ['pointercancel','lostpointercapture'])$('graph').addEventListener(name,()=>{graphDrag=null;});
$('graph-in').onclick=()=>zoomGraph(2);$('graph-out').onclick=()=>zoomGraph(.5);
$('fit-graph').onclick=()=>setScoreView(scoreBounds(score.rows));
$('fit-scores').onclick=()=>setScoreView(fitScoreY(scoreView,scoreBounds(score.rows),score.rows));
function viewScoreRange(low,high) {
  if(!score)return;
  const bounds=scoreBounds(score.rows);
  if(!Number.isFinite(low)||!Number.isFinite(high)||low>=high||low<bounds.xMin||high>bounds.xMax){$('graph-readout').textContent=`Use a view range inside ${bounds.xMin}–${bounds.xMax}.`;return;}
  setScoreView(fitScoreY(constrainScoreView({...scoreView,xMin:low,xMax:high},bounds),bounds,score.rows));
}
$('graph-range').onclick=()=>viewScoreRange(+$('graph-low').value,+$('graph-high').value);
for(const id of ['graph-low','graph-high'])$(id).onkeydown=event=>{if(event.key==='Enter'){event.preventDefault();$('graph-range').click();}};
$('best-window').onclick=()=>{const bounds=scoreBounds(score.rows);viewScoreRange(Math.max(bounds.xMin,score.best.count-30),Math.min(bounds.xMax,score.best.count+30));};
$('expand-graph').onclick=()=>{$('score-dialog').append($('score-panel'));$('score-dialog').showModal();drawGraph();};
$('close-graph').onclick=()=>$('score-dialog').close();
$('score-dialog').addEventListener('close',()=>{$('score-home').append($('score-panel'));drawGraph();});
new ResizeObserver(drawGraph).observe($('graph'));
$('plot').onclick=async()=>{
  if(plotting)return;plotting=true;score=null;scoreView=null;graphDrag=null;drawGraph();markControls();
  const version=marks.version,hand=requestedHand;
  try {
    if(dirty()||!centerDoc.revision)await saveCenters();
    if(marks.version!==version)throw new Error('Centers changed while saving. Plot again with the latest centers.');
    const job=await api('/api/score',{low:+$('score-low').value,high:+$('score-high').value,step:+$('score-step').value,hand,revision:centerDoc.revision});
    scoreJob=job.id;markControls();
    while(true) {
      const state=await api(`/api/score?id=${encodeURIComponent(job.id)}`);
      if(state.state==='error')throw new Error(state.error);
      if(state.state==='complete') {
        if(marks.version!==version)throw new Error('Scan saved for the earlier marks. Plot again for your current centers.');
        score=state.result;resetScoreView();drawGraph();
        scoreSummary(`Saved → ${state.path}.`);
        $('show-matches').checked=true;schedule(score.best.count,score.hand);break;
      }
      $('score-status').textContent=`Scanning hand ${hand>0?'+1':'−1'}: ${state.done} / ${state.total} counts…`;
      await new Promise(resolve=>setTimeout(resolve,350));
    }
  }catch(error){$('score-status').textContent=error.message;}
  finally{scoreJob=null;plotting=false;markControls();}
};
$('cancel-score').onclick=()=>{if(scoreJob)api('/api/cancel-score',{id:scoreJob}).catch(error=>{$('score-status').textContent=error.message;});};
$('download-score').onclick=()=>{if(score)download(new Blob([JSON.stringify(score,null,2)+'\n'],{type:'application/json'}),'bead-count-score.json');};
$('download-graph').onclick=()=>{if(score)$('graph').toBlob(blob=>{if(blob)download(blob,'bead-count-score.png');});};
