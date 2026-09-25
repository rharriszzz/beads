// Exercise the saved viewer's controls without requiring a browser installation.
const fs = require('fs'), vm = require('vm'), assert = require('assert');
const html = fs.readFileSync('photo2/review/r085/review.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const finite = (...values) => assert(values.every(Number.isFinite));
const context = {drawImage(){}, beginPath(){}, closePath(){}, stroke(){},
  setTransform: finite, fillRect(){}, moveTo: finite, lineTo: finite};
const elements = {index:{value:'0'}, prev:{}, next:{}, info:{},
  whole:{getContext:()=>context}, detail:{getContext:()=>context}};
class Image {set src(value) {assert.equal(value, 'white-reference.png'); this.onload();}}
vm.runInNewContext(script, {Image, document:{getElementById:id=>elements[id]}});
for (let i=0; i<676; i++) {
  elements.index.value = String(i); elements.index.oninput();
  assert(elements.info.textContent.startsWith(`Index ${i} ·`));
}
elements.index.value='0'; elements.prev.onclick(); assert.equal(+elements.index.value,675);
elements.next.onclick(); assert.equal(+elements.index.value,0);
console.log('Viewer: all 676 index updates and wrap controls pass with a mocked canvas DOM.');
