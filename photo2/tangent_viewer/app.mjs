import {toSource, zoomAt, fitView, resizeView, RequestGate} from './viewport.mjs';

const $ = id => document.getElementById(id);
const canvas = $('canvas'), ctx = canvas.getContext('2d');
for (const element of document.querySelectorAll('button,input,select')) element.disabled=true;
const gate = new RequestGate();
let config, image, frame, view, width = 0, height = 0, drag = null, timer, controller;
let requestedCount, requestedHand, saving = false;
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
function render() {
  if (!image || !view) return;
  const dpr = window.devicePixelRatio || 1;
  ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,width,height);
  ctx.imageSmoothingEnabled = true;
  ctx.drawImage(image,view.x,view.y,image.naturalWidth*view.scale,image.naturalHeight*view.scale);
  if (frame && $('show').checked) drawCircles(ctx,frame.circles,view,current()?1:.3);
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
    if (!gate.accepts(generation)) return;
    frame=result; buttons(); render();
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
canvas.addEventListener('wheel',event=>{
  event.preventDefault();
  const delta=event.deltaY*(event.deltaMode===1?16:event.deltaMode===2?height:1);
  zoom(Math.exp(-Math.max(-600,Math.min(600,delta))*.0015),point(event));
},{passive:false});
canvas.addEventListener('pointerdown',event=>{
  if(event.button!==0 || !view) return;
  const p=point(event); drag={id:event.pointerId,x:p.x,y:p.y,start:{...view}};
  canvas.setPointerCapture(event.pointerId); canvas.classList.add('dragging');
});
canvas.addEventListener('pointermove',event=>{
  if(!drag || drag.id!==event.pointerId) return;
  const p=point(event);view={...drag.start,x:drag.start.x+p.x-drag.x,y:drag.start.y+p.y-drag.y};render();
});
function stopDrag(event) { if(drag?.id===event.pointerId) {drag=null;canvas.classList.remove('dragging');} }
canvas.addEventListener('pointerup',stopDrag);canvas.addEventListener('pointercancel',stopDrag);
canvas.addEventListener('lostpointercapture',stopDrag);
$('save').onclick=async()=>{
  if(!current() || saving) return;
  saving=true;buttons();
  const choice={count:frame.count,hand:frame.hand,view:{...view}};
  try {
    const response=await fetch('/api/choice',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(choice)});
    const result=await response.json();if(!response.ok)throw new Error(result.error || 'Could not save choice.');
    $('saved').textContent=`Saved ${choice.count.toLocaleString()}, helicity ${choice.hand>0?'+1':'−1'} → ${result.path}`;
  } catch(error) { $('saved').textContent=`Save failed: ${error.message}`; }
  finally {saving=false;buttons();}
};
$('json').onclick=()=>{
  if(!current())return;
  download(new Blob([JSON.stringify(frame.parameters,null,2)+'\n'],{type:'application/json'}),`beads-${frame.hand>0?'plus':'minus'}-${frame.count}.json`);
};
$('png').onclick=()=>{
  if(!current())return;
  const selected=frame, output=document.createElement('canvas');
  [output.width,output.height]=config.source.oriented_size;
  const context=output.getContext('2d');context.drawImage(image,0,0);
  drawCircles(context,selected.circles,{x:0,y:0,scale:1});
  output.toBlob(blob=>{if(blob)download(blob,`beads-${selected.hand>0?'plus':'minus'}-${selected.count}.png`);},'image/png');
};
new ResizeObserver(resize).observe($('stage'));
async function start() {
  try {
    const response=await fetch('/api/config');config=await response.json();
    if(!response.ok)throw new Error(config.error || 'Could not load viewer.');
    for(const id of ['count','minimum','maximum']) {$(id).min=config.allowed_range[0];$(id).max=config.allowed_range[1];}
    $('minimum').value=$('slider').min=config.min_count;$('maximum').value=$('slider').max=config.max_count;
    const loaded=new Image();loaded.src=config.image_url;await loaded.decode();image=loaded;
    for (const element of document.querySelectorAll('button,input,select')) element.disabled=false;
    resize();schedule(config.initial_count,config.initial_hand);
  } catch(error) {status(error.message,true);}
}
start();
