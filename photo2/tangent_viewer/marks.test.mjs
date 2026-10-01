import assert from 'node:assert/strict';
import {Marks,hitMark,isClick} from './marks.mjs';
import {toSource,toScreen,zoomAt} from './viewport.mjs';

const m=new Marks();
const view={x:-350,y:180,scale:2.5},pixel={x:140,y:220};
const source=toSource(pixel,view);m.add(source,'stable-a');m.add({x:230,y:24},'stable-b');
assert.deepEqual(toScreen(m.points[0],view),pixel);
const zoomed=zoomAt(view,pixel,1.7);
assert.equal(hitMark(m.points,toSource(pixel,zoomed),zoomed.scale),'stable-a');
assert.equal(hitMark(m.points,{x:0,y:0},view.scale),null);
assert.equal(isClick(4),true);assert.equal(isClick(4.1),false);
console.log('PASS source-coordinate placement, pointer zoom, hit selection and drag threshold');

m.move('stable-a',{x:199,y:47});m.renumber('stable-a',10);
assert.equal(m.points[0].id,'stable-a');assert.equal(m.points[0].number,10);
assert.throws(()=>m.renumber('stable-b',10));
m.remove('stable-a');assert.equal(m.points.length,1);m.undo();
assert.deepEqual(m.points[0],{id:'stable-a',number:10,x:199,y:47});
m.undo();assert.equal(m.points[0].number,1);m.undo();assert.deepEqual(m.points[0],{id:'stable-a',number:1,...source});
assert.equal(m.points[1].id,'stable-b');
console.log('PASS stable observation IDs, independent numbers, edit/delete/undo and collision rejection');
