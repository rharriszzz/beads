import test from 'node:test';
import assert from 'node:assert/strict';
import {toSource, toScreen, zoomAt, resizeView, fitView, guideEdges, RequestGate} from './viewport.mjs';
const close = (a,b) => assert.ok(Math.abs(a-b)<1e-9, `${a} != ${b}`);

test('zoom keeps the source bead beneath the pointer, even at zoom limits',()=>{
  const view={x:-550,y:45,scale:2.3}, pointer={x:313,y:228};
  const bead=toSource(pointer,view);
  for(const factor of [.5,1.5,1000,.00001]) {
    const changed=zoomAt(view,pointer,factor), screen=toScreen(bead,changed);
    close(screen.x,pointer.x);close(screen.y,pointer.y);
    assert.ok(changed.scale>=.025 && changed.scale<=32);
  }
});
test('panning moves photo and circle together; window resizing keeps the inspected center',()=>{
  const view={x:-700,y:-140,scale:4}, moved={...view,x:view.x+45,y:view.y-28};
  const bead={x:1320,y:270};
  const before=toScreen(bead,view),after=toScreen(bead,moved);
  close(after.x-before.x,45);close(after.y-before.y,-28);
  const originalCenter=toSource({x:600,y:400},moved);
  const resized=resizeView(moved,{width:1200,height:800},{width:1000,height:600});
  const nextCenter=toSource({x:500,y:300},resized);
  close(originalCenter.x,nextCenter.x);close(originalCenter.y,nextCenter.y);
});
test('fit whole photo and starting patch share source coordinates without changing the crop',()=>{
  for(const crop of [[0,0,2540,3182],[1210,210,1450,365]]) {
    const view=fitView(1200,800,crop);
    const center=toScreen({x:(crop[0]+crop[2])/2,y:(crop[1]+crop[3])/2},view);
    close(center.x,600);close(center.y,400);
    for(const point of [{x:crop[0],y:crop[1]},{x:crop[2],y:crop[3]}]) {
      const p=toScreen(point,view);assert.ok(p.x>=0&&p.x<=1200&&p.y>=0&&p.y<=800);
    }
  }
});
test('a delayed earlier count reply cannot overwrite a newer slider choice',async()=>{
  const gate=new RequestGate(), first=gate.invalidate();
  let release;const delayed=new Promise(resolve=>{release=resolve;});
  const oldReply=delayed.then(()=>gate.accepts(first));
  const newer=gate.invalidate();
  assert.ok(gate.accepts(newer));release();
  assert.equal(await oldReply,false);
});
test('width comparison offsets both edges symmetrically and keeps centerline fixed through zoom/pan',()=>{
  const guides={centerline:[[20,40],[30,40],[20,40]],normals:[[0,1],[0,1],[0,1]],radius_pixels:10};
  const saved=JSON.stringify(guides), original=guideEdges(guides), expanded=guideEdges(guides,107);
  const view={x:-22,y:48,scale:3.2};
  for(let i=0;i<guides.centerline.length;i++) {
    close((expanded[0][i][1]+expanded[1][i][1])/2,guides.centerline[i][1]);
    close((expanded[0][i][1]-expanded[1][i][1])/(original[0][i][1]-original[1][i][1]),1.07);
    const a=toScreen({x:expanded[0][i][0],y:expanded[0][i][1]},view);
    const b=toScreen({x:expanded[1][i][0],y:expanded[1][i][1]},view);
    const c=toScreen({x:guides.centerline[i][0],y:guides.centerline[i][1]},view);
    close((a.y+b.y)/2,c.y);close(a.y-b.y,2*10*1.07*view.scale);
  }
  assert.equal(JSON.stringify(guides),saved);
});
