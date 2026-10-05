/* R226: exercise the actual viewer script with a browser's restricted location
 * binding. This checks startup and pixel-coordinate handling, not browser paint.
 * Run: node photo2/test_mask_stage_viewer.cjs
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const html = fs.readFileSync(path.join(__dirname, 'review/r224/index.html'), 'utf8');
const payload = /<script id="trace-data" type="application\/json">([\s\S]*?)<\/script>/.exec(html)[1];
const cases = JSON.parse(payload).cases;
const scripts = [...html.matchAll(/<script(?![^>]*application\/json)[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]);

class Element {
  constructor() {
    this.children = []; this.handlers = {}; this.style = {}; this.value = ''; this.checked = true;
    this.selectedIndex = 0; this.innerHTML = ''; this.textContent = ''; this.paintCalls = 0;
    this.classList = {toggle() {}};
  }
  appendChild(child) {this.children.push(child);}
  addEventListener(type, handler) {this.handlers[type] = handler;}
  getBoundingClientRect() {return {left:-80, top:20};}
  getContext() {
    const owner = this;
    return {
      drawImage() {owner.paintCalls++;},
      getImageData(x,y,width,height) {return {data:new Uint8ClampedArray(width*height*4)};},
      putImageData() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, arc() {},
      strokeText() {}, fillText() {}, strokeRect() {}
    };
  }
}
const elements = new Map();
for (const id of ['trace-data','example','zoom','zoomvalue','paint','marks','point','steps',
                   'description','stagecaption','raw','stage','rawfallback','stagefallback','status','inspector']) {
  elements.set(id,new Element());
}
elements.get('trace-data').textContent = payload;
elements.get('zoom').value = '4';
globalThis.document = {getElementById:id=>elements.get(id),createElement:()=>new Element()};
const windowEvents = {};
globalThis.window = {addEventListener:(type,fn)=>{windowEvents[type]=fn;}};
// Window.location is non-configurable. A top-level lexical declaration fails.
Object.defineProperty(globalThis, 'location', {value:{href:'http://127.0.0.1:4001/'},configurable:false});
assert.throws(()=>vm.runInThisContext('let location = null;'),SyntaxError);
globalThis.Image = class {
  set src(value) {
    const png = Buffer.from(value.split(',')[1],'base64');
    this.width = png.readUInt32BE(16); this.height = png.readUInt32BE(20);
  }
  decode() {return Promise.resolve();}
};
globalThis.ImageData = class {constructor(data,width,height) {this.data=data;this.width=width;this.height=height;}};
const settle = () => new Promise(resolve=>setImmediate(resolve));

(async()=>{
  for (const source of scripts) vm.runInThisContext(source);
  await settle();
  assert.equal(elements.get('example').children.length,3);
  assert.equal(elements.get('steps').children.length,8);
  for (const [i,c] of cases.entries()) {
    if (i) {
      elements.get('example').selectedIndex=i;
      await elements.get('example').handlers.change();
    }
    assert.match(elements.get('status').textContent,new RegExp(`Example ${c.letter} loaded`));
    assert.equal(elements.get('raw').width,(c.crop[2]-c.crop[0])*4);
    assert.equal(elements.get('raw').height,(c.crop[3]-c.crop[1])*4);
    assert.equal(elements.get('raw').style.display,'block');
    assert.equal(elements.get('rawfallback').style.display,'none');
    assert.match(elements.get('inspector').innerHTML,new RegExp(`Native pixel \\(${c.point_xy.join(', ')}\\)`));
    // Click P after changing zoom, with a viewport offset representing pan.
    elements.get('zoom').value='6'; elements.get('zoom').handlers.input();
    elements.get('raw').handlers.click({clientX:-80+(c.point_crop_xy[0]+.5)*6,
                                     clientY:20+(c.point_crop_xy[1]+.5)*6});
    assert.match(elements.get('inspector').innerHTML,new RegExp(`Native pixel \\(${c.point_xy.join(', ')}\\)`));
    elements.get('zoom').value='4'; elements.get('zoom').handlers.input();
  }
  assert.ok(elements.get('raw').paintCalls>0 && elements.get('stage').paintCalls>0);
  windowEvents.error({message:'test failure'});
  assert.match(elements.get('status').textContent,/Viewer error: test failure/);
  console.log('PASS: restricted-global startup, all three cases, zoom/pan pixel coordinates and visible error reporting. Browser paint is not exercised.');
})().catch(error=>{console.error(error);process.exitCode=1;});
