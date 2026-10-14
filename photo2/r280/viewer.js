'use strict';
const $=id=>document.getElementById(id), scenes=window.REVIEW;
let bitmap=null, record=null;
for(let i=0;i<scenes.length;i++){const o=document.createElement('option');o.value=i;o.textContent=scenes[i].title;$('scene').append(o);}
function boundary(ctx,runs,color){const pixels=new Set();for(const [y,a,b] of runs)for(let x=a;x<=b;x++)pixels.add(x+','+y);ctx.fillStyle=color;for(const key of pixels){const [x,y]=key.split(',').map(Number);if(!pixels.has((x-1)+','+y)||!pixels.has((x+1)+','+y)||!pixels.has(x+','+(y-1))||!pixels.has(x+','+(y+1)))ctx.fillRect(x,y,1,1);}}
function draw(){if(!bitmap)return;for(const id of ['raw','overlay']){const c=$(id);c.width=bitmap.width;c.height=bitmap.height;c.style.width=(bitmap.width*2)+'px';c.getContext('2d').drawImage(bitmap,0,0);}
 const ctx=$('overlay').getContext('2d'),p=record.predictions.find(p=>p.id===$('bead').value),r=record.results.find(r=>r.id===p.id);
 if($('neighbors').checked)for(const q of record.predictions)if(q.id!==p.id)boundary(ctx,q.visible,'#aaa');
 if($('prediction').checked){boundary(ctx,p.visible,'#ff981c');ctx.strokeStyle='#ff981c';ctx.beginPath();ctx.moveTo(p.center[0]-4,p.center[1]);ctx.lineTo(p.center[0]+4,p.center[1]);ctx.moveTo(p.center[0],p.center[1]-4);ctx.lineTo(p.center[0],p.center[1]+4);ctx.stroke();}
 if($('evidence').checked){ctx.fillStyle='rgba(30,240,110,.60)';for(const [y,a,b] of r.support)ctx.fillRect(a,y,b-a+1,1);if(r.location){ctx.fillStyle='white';ctx.fillRect(r.location[0]-1,r.location[1]-1,3,3);}}
 if($('uncertainty').checked&&r.location){ctx.strokeStyle='#d674ff';ctx.setLineDash([2,2]);ctx.beginPath();ctx.arc(...r.location,r.uncertainty_radius_px,0,2*Math.PI);ctx.stroke();ctx.setLineDash([]);}
 if($('phase1').checked){ctx.strokeStyle='#18edff';for(const o of record.phase1){ctx.beginPath();ctx.arc(...o.point,2,0,2*Math.PI);ctx.stroke();}}
 const evaluation=record.evaluation.find(e=>e.id===p.id);$('details').textContent=JSON.stringify({hypothesis:p.id,status:r.status,color:r.color,score:r.score,measuredPixels:r.positive_pixels,photographicLocation:r.location,physicalCenter:r.physical_center,uncertaintyRadius:r.uncertainty_radius_px,photographicMetrics:r.metrics,registration:r.registration,competingOwners:r.competing_ids,existingPhase1:r.phase1_overlap_ids,evaluationOnly:evaluation?{tier:evaluation.tier,correct:evaluation.correct,wrongOwner:evaluation.wrong_owner,intendedPurity:evaluation.intended_purity,locationErrorDiameters:evaluation.location_error_diameter}: 'No independently established real-photo truth'},null,2);
}
function load(){record=scenes[Number($('scene').value)];$('bead').replaceChildren();for(const p of record.predictions){const o=document.createElement('option');o.value=p.id;const r=record.results.find(r=>r.id===p.id);o.textContent=p.id+' · '+r.status;$('bead').append(o);}$('bead').value=record.selected;bitmap=null;const im=new Image();im.onload=()=>{bitmap=im;draw();};im.src='results/'+record.image;}
$('scene').onchange=load;$('bead').onchange=draw;for(const id of ['phase1','prediction','evidence','uncertainty','neighbors'])$(id).onchange=draw;load();
