const $=id=>document.getElementById(id);
const data=await (await fetch('/hue-comparison.json')).json();
const image=new Image();image.src='/photo.png';await image.decode();
const raw=document.createElement('canvas');raw.width=image.width;raw.height=image.height;
const rc=raw.getContext('2d',{willReadFrequently:true});rc.drawImage(image,0,0);
let selected=null;
data.cases.forEach((c,i)=>$('crop').add(new Option(c.name,i)));
const inside=(r,x,y)=>r.pixel_runs.some(([ry,a,b])=>ry===y&&x>=a&&x<=b);
const fmt=x=>Number(x).toFixed(2);
function hsv(r,g,b){r/=255;g/=255;b/=255;const v=Math.max(r,g,b),m=Math.min(r,g,b),d=v-m;let h=0;if(d)h=60*(v===r?((g-b)/d+6)%6:v===g?(b-r)/d+2:(r-g)/d+4);return [h,v?d/v:0,v];}
function draw(){
 const c=data.cases[Number($('crop').value)], [x0,y0,x1,y1]=c.box,w=x1-x0,h=y1-y0;
 $('panels').replaceChildren();
 for(const hue of ['Original',...data.hues]){
  const card=document.createElement('article'),title=document.createElement('h2');title.textContent=hue==='Original'?hue:`${hue}°`;card.append(title);
  const canvas=document.createElement('canvas');canvas.width=w*4;canvas.height=h*4;canvas.tabIndex=0;canvas.setAttribute('aria-label',`${c.name} ${hue} identical native crop`);card.append(canvas);$('panels').append(card);
  const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=false;ctx.drawImage(image,x0,y0,w,h,0,0,w*4,h*4);ctx.scale(4,4);ctx.translate(-x0+.5,-y0+.5);
  const rows=c.runs[hue]||[];
  for(const r of rows){ctx.strokeStyle=r.id===selected?'#ffff33':'cyan';ctx.lineWidth=r.id===selected?.7:.25;
   for(const curve of r.contours){ctx.beginPath();curve.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.stroke();}
   const [x,y]=r.location;ctx.strokeStyle=r.id===selected?'#ffff33':'white';ctx.lineWidth=.35;ctx.beginPath();ctx.moveTo(x-1.5,y);ctx.lineTo(x+1.5,y);ctx.moveTo(x,y-1.5);ctx.lineTo(x,y+1.5);ctx.stroke();
  }
  function pixel(e){const b=canvas.getBoundingClientRect();return [Math.min(x1-1,Math.floor(x0+(e.clientX-b.left)/b.width*w)),Math.min(y1-1,Math.floor(y0+(e.clientY-b.top)/b.height*h))];}
  canvas.onpointermove=e=>{const [x,y]=pixel(e),rgb=rc.getImageData(x,y,1,1).data,q=hsv(...rgb);$('readout').textContent=`Native (${x}, ${y}) · RGB ${[...rgb].slice(0,3).join(', ')} · H ${fmt(q[0])}° · S ${fmt(q[1])} · V ${fmt(q[2])} · ${rows.filter(r=>inside(r,x,y)).map(r=>r.id).join(', ')||'no support at this pixel'}`;};
  canvas.onclick=e=>{const [x,y]=pixel(e),matches=rows.filter(r=>inside(r,x,y));if(matches.length){const i=matches.findIndex(r=>r.id===selected);selected=matches[(i+1)%matches.length].id;draw();}};
 }
 const rows=[];for(const hue of data.hues)for(const r of c.runs[hue]){if(selected&&r.id!==selected)continue;const q=r.hsv_diagnostic;rows.push(`<tr><td>${hue}°</td><td><a href="/?hue=${hue}&id=${r.id}">${r.id}</a></td><td>${r.location.join(', ')}</td><td>${r.pixel_count}</td><td>${q.at_location.map(fmt).join(' / ')}</td><td>${q.hue_relative_p10_p90.map(fmt).join(' … ')}</td><td>${q.value_p10_p90.map(fmt).join(' … ')}</td></tr>`);}
 $('table').innerHTML=`<button id="all">Show all supports</button><p>HSV at the supported coordinate; ΔH is the circular 10th–90th percentile relative to that coordinate over retained pixels. It is not the growth anchor or a boundary measurement. V range is also 10th–90th percentile.</p><table><thead><tr><th>Hue</th><th>Support / replay</th><th>Coordinate</th><th>Pixels</th><th>H° / S / V</th><th>ΔH° range</th><th>V range</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
 $('all').onclick=()=>{selected=null;draw();};
 window.hueTest={case:c.name,box:c.box,selected,panels:7};
}
$('crop').onchange=()=>{selected=null;draw();};
for(const [id,step] of [['previous',-1],['next',1]])$(id).onclick=()=>{$('crop').value=(Number($('crop').value)+step+data.cases.length)%data.cases.length;selected=null;draw();};
draw();$('readout').textContent='Hover any panel for native RGB / HSV. Select a support to compare its coordinates.';
