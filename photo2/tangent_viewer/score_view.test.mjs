import assert from 'node:assert/strict';
import {scoreBounds,constrainScoreView,zoomScore,panScore,fitScoreY,nearestScore} from './score_view.mjs';

const rows=Array.from({length:101},(_,i)=>({count:2500+i,sse:100+(i-62)**2}));
const original=structuredClone(rows),bounds=scoreBounds(rows),pivot={x:.3,y:.4};
const next=zoomScore(bounds,bounds,pivot,2);
const anchor=(view,axis,f)=>view[axis+'Min']+(view[axis+'Max']-view[axis+'Min'])*f;
assert.equal(anchor(next,'x',.3),anchor(bounds,'x',.3));
assert.equal(anchor(next,'y',.4),anchor(bounds,'y',.4));
assert.equal(next.xMax-next.xMin,50);
const yOnly=zoomScore(bounds,bounds,pivot,2,'y');
assert.equal(yOnly.xMin,bounds.xMin);assert.equal(yOnly.xMax,bounds.xMax);
const xOnly=zoomScore(bounds,bounds,pivot,2,'x');
assert.equal(xOnly.yMin,bounds.yMin);assert.equal(xOnly.yMax,bounds.yMax);
console.log('PASS pointer-anchored graph zoom and independent count/score axes');

const moved=panScore(next,bounds,10,25);
assert.equal(moved.xMin,next.xMin+10);assert.equal(moved.yMin,next.yMin+25);
const limited=panScore(next,bounds,999999,-999999);
assert.equal(limited.xMax,bounds.xMax);assert.equal(limited.yMin,bounds.yMin);
assert.equal(limited.xMax-limited.xMin,next.xMax-next.xMin);
const tiny=zoomScore(bounds,bounds,{x:.5,y:.5},1e20);
assert.equal(tiny.xMax-tiny.xMin,1);
assert.throws(()=>constrainScoreView({...bounds,yMax:NaN},bounds));
console.log('PASS pan direction, domain limits, minimum span and saved-view validation');

const fitted=fitScoreY({...bounds,xMin:2558,xMax:2567},bounds,rows);
assert(fitted.yMax<bounds.yMax);assert(fitted.yMin<100 && fitted.yMax>125);
assert.equal(nearestScore(rows,2562.1).count,2562);
assert.equal(nearestScore(rows,-10).count,2500);assert.equal(nearestScore(rows,10000).count,2600);
const flat=[{count:1,sse:0},{count:2,sse:0}],flatBounds=scoreBounds(flat);
assert(flatBounds.yMax>flatBounds.yMin);
assert.deepEqual(rows,original);
console.log('PASS fit scores to visible counts, nearest sample, constant curve and data preservation');
