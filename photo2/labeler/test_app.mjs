// Exercise the real application handlers with a minimal DOM/canvas adapter.
// This does not substitute for graphical-browser layout or pointer testing.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fitView, sourceToScreen} from './model.mjs';

test('place and number beads, reject duplicates, click a series, undo and save through app handlers', async () => {
  class Element {
    constructor(id = '') { this.id=id; this.children=[]; this.events={}; this.style={}; this.classList={toggle(){}}; this.value=''; this.checked=false; this.clientWidth=400; this.clientHeight=400; }
    addEventListener(name,fn) { this.events[name]=fn; }
    replaceChildren(...children) { this.children=children; }
    append(...children) { this.children.push(...children); }
    setAttribute() {}
    focus() { document.activeElement=this; }
    select() {}
    getBoundingClientRect() { return {left:0,top:0}; }
    setPointerCapture(id) { this.capture=id; }
    hasPointerCapture(id) { return this.capture===id; }
    releasePointerCapture() { this.capture=null; }
  }
  const html=await readFile(new URL('./index.html',import.meta.url),'utf8');
  const elements=new Map([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element(m[1])]));
  const el=id=>elements.get(id);
  el('show').checked=true;el('direction').value='d1';el('number').tagName='INPUT';
  el('canvas').getContext=()=>new Proxy({}, {get:(_,key)=>key==='measureText'?s=>({width:String(s).length*8}):()=>{},set:()=>true});
  globalThis.document={getElementById:id=>{assert.ok(elements.has(id),`missing HTML element ${id}`);return el(id);},createElement:()=>new Element(),activeElement:null};
  globalThis.window=new Element();
  globalThis.ResizeObserver=class { constructor(fn) {this.fn=fn;} observe() {this.fn();} };
  globalThis.devicePixelRatio=1;
  globalThis.Image=class { complete=true;naturalWidth=40;width=40;height=40;decode(){return Promise.resolve();} };
  const drafts=new Map();globalThis.localStorage={getItem:k=>drafts.get(k)??null,setItem:(k,v)=>drafts.set(k,v),removeItem:k=>drafts.delete(k)};
  const crop=[20,30,60,70];
  let saved={schema_version:2,revision:0,annotations:[],series:[]};
  globalThis.fetch=async (url,options)=>{
    if(url==='/api/config')return {ok:true,json:async()=>({crop,image_url:'/image.png',source:{sha256:'test'},annotations_path:'/tmp/test.json',directions:{d1:'±1',d2:'up/down clockwise',d3:'down/up clockwise'},document:structuredClone(saved)})};
    assert.equal(url,'/api/annotations');const payload=JSON.parse(options.body);assert.equal(payload.revision,saved.revision);
    saved={...payload,revision:payload.revision+1};return {ok:true,json:async()=>structuredClone(saved)};
  };
  await import('./app.mjs');await new Promise(resolve=>setImmediate(resolve));
  assert.match(el('status').textContent,/Ready/);
  const view=fitView(400,400,crop),canvas=el('canvas');
  const pointer=(x,y)=>({clientX:x,clientY:y,button:0,pointerId:1,preventDefault(){}});
  function click(x,y,offset=0) {
    const p=sourceToScreen({x,y},view,crop),event=pointer(p.x+offset,p.y);
    canvas.events.pointerdown(event);canvas.events.pointerup(event);
  }
  function submit(number) { el('number').value=String(number);el('editor').onsubmit({preventDefault(){}}); }
  async function save() { await el('save').onclick();await new Promise(resolve=>setImmediate(resolve)); }
  click(25,35);submit(101);click(45,55);submit(101);
  assert.match(el('status').textContent,/already exists/);submit(202);await save();
  assert.deepEqual(saved.annotations.map(m=>m.number),[101,202]);
  assert.ok(Math.abs(saved.annotations[0].x-25)<1e-10);
  el('direction').value='d3';el('start').onclick();
  click(45,55,8);click(25,35,5); // Near locations, not exact anchors.
  assert.match(el('active').textContent,/202 → 101/);
  click(25,35);assert.match(el('status').textContent,/already the last click/);
  el('end').onclick();await save();
  assert.equal(saved.series[0].direction,'d3');assert.equal(saved.series[0].status,'complete');
  const ids=saved.annotations.map(m=>m.id);assert.deepEqual(saved.series[0].bead_ids,[ids[1],ids[0]]);
  click(25,35);submit(999);await save();
  assert.equal(saved.annotations[0].number,999);assert.deepEqual(saved.series[0].bead_ids,[ids[1],ids[0]]);
  el('remove').onclick();assert.match(el('status').textContent,/belongs to a series/);
  el('undo').onclick();await save();assert.equal(saved.annotations[0].number,101);
  el('undo').onclick();await save();assert.equal(saved.series[0].status,'active');
  el('pop').onclick();await save();assert.deepEqual(saved.series[0].bead_ids,[ids[1]]);
  click(35,65);assert.match(el('status').textContent,/No numbered bead/);
  await save();assert.equal(saved.annotations.length,2);
});
