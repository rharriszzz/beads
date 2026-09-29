import test from 'node:test';
import assert from 'node:assert/strict';
import {sourceToScreen, screenToSource, fitView, zoomAt, History, clippedPoint, validNumber, nextNumber, nearestBead, startSeries, appendBead, endSeries, removeBead} from './model.mjs';

test('source anchors survive pan and zoom including nonzero crop origin', () => {
  const crop = [1180, 130, 1540, 520], anchor = {x: 1360.25, y: 256.75};
  let view = fitView(1000, 700, crop);
  for (const factor of [.1, 13, .01, 700, .3]) {
    const pointer = {x: 412.5, y: 212.25};
    const before = screenToSource(pointer, view, crop);
    view = zoomAt(view, pointer, factor);
    const after = screenToSource(pointer, view, crop);
    assert.ok(Math.abs(before.x - after.x) < 1e-9);
    assert.ok(Math.abs(before.y - after.y) < 1e-9);
    view.x += 24; view.y -= 35;
    const recovered = screenToSource(sourceToScreen(anchor, view, crop), view, crop);
    assert.ok(Math.abs(recovered.x - anchor.x) < 1e-9);
    assert.ok(Math.abs(recovered.y - anchor.y) < 1e-9);
  }
});
test('undo and redo preserve IDs, numbers and positions across deletion and a new branch', () => {
  const one = {id: 'stable-1', x: 1360, y: 256, number: 3}, two = {id: 'stable-2', x: 1348, y: 280, number: 9};
  const history = new History([one]); history.push([one, two]); history.push([two]);
  assert.deepEqual(history.undo(), [one, two]);
  assert.deepEqual(history.redo(), [two]);
  history.undo(); history.push([{...one, number: 12}, two]);
  assert.equal(history.canRedo, false);
  assert.deepEqual(history.undo(), [one, two]);
  const snapshot = history.undo(); snapshot[0].id = 'mutated';
  assert.equal(history.undo()[0].id, 'stable-1');
});
test('moving an anchor cannot leave the raw crop', () => {
  assert.deepEqual(clippedPoint({x: -100, y: 5000}, [1180,130,1540,520]), {x:1180,y:519.999});
});
test('numbers stay unique while renaming the same bead is allowed', () => {
  const records = [{id:'a',number:1},{id:'b',number:3}];
  assert.equal(nextNumber(records),2);
  assert.equal(validNumber('1',records,'a'),1);
  assert.equal(validNumber('-12',records),-12);
  for (const value of ['1','3','', '1.5','NaN','9007199254740992']) assert.throws(()=>validNumber(value,records));
});
test('click snapping uses screen distance after zoom and excludes outside-crop beads', () => {
  const crop=[1180,130,1540,520],view={x:17,y:32,scale:3};
  const a={id:'a',x:1200,y:150},b={id:'b',x:1210,y:150},outside={id:'outside',x:1179,y:150};
  const p=sourceToScreen(a,view,crop);
  assert.equal(nearestBead({x:p.x+8,y:p.y+7},[a,b,outside],view,crop).id,'a');
  assert.equal(nearestBead({x:p.x+30,y:p.y},[a,b],view,crop).id,'b');
  assert.equal(nearestBead({x:p.x,y:p.y+19},[a,b],view,crop),null);
  assert.equal(nearestBead(sourceToScreen(outside,view,crop),[outside],view,crop),null);
});
test('direction series record click order; undo, renumber and deletion preserve links', () => {
  const state={annotations:[{id:'a',number:1},{id:'b',number:9},{id:'c',number:20}],series:[]};
  const h=new History(state);
  startSeries(state,'d3','s'); h.push(state);
  assert.throws(()=>startSeries(state,'d2','t'));
  assert.throws(()=>endSeries(state));
  appendBead(state,'b'); h.push(state);
  assert.throws(()=>appendBead(state,'b'));
  assert.throws(()=>appendBead(state,'missing'));
  appendBead(state,'a');h.push(state);endSeries(state);h.push(state);
  assert.deepEqual(state.series[0].bead_ids,['b','a']);
  state.annotations[0].number=100;h.push(state);
  assert.deepEqual(state.series[0].bead_ids,['b','a']);
  assert.equal(h.undo().annotations[0].number,1);
  assert.equal(h.undo().series[0].status,'active');
  assert.deepEqual(h.undo().series[0].bead_ids,['b']);
  assert.deepEqual(h.redo().series[0].bead_ids,['b','a']);
  assert.throws(()=>removeBead(state,'a'));
  removeBead(state,'c');assert.equal(state.annotations.length,2);
  for(const direction of ['d1','d2']) {
    startSeries(state,direction,direction); appendBead(state,'a'); appendBead(state,'b');endSeries(state);
  }
  assert.deepEqual(state.series.map(s=>s.direction),['d3','d1','d2']);
});
