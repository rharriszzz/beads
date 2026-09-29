import {sourceToScreen, screenToSource, fitView, zoomAt, withinCrop, clippedPoint, displayLabel, History, validNumber, nextNumber, nearestBead, startSeries, appendBead, endSeries, removeBead} from './model.mjs';

const $ = id => document.getElementById(id);
const canvas = $('canvas'), ctx = canvas.getContext('2d');
let config, image, records = [], series = [], history, selected = null, pending = null;
let view, width = 0, height = 0, boxes = [], gesture = null, space = false;
let revision = 0, changeVersion = 0, savedVersion = 0, saving = false, blocked = false, timer;
let draftKey;
const snapshot = () => ({annotations: records, series});
const activeSeries = () => series.find(s => s.status === 'active');
const seriesColors = {d1: '#ffbd59', d2: '#50e9ff', d3: '#bba0ff'};
function restore(state) { records = state.annotations; series = state.series; }

function status(text, error = false) {
  $('status').textContent = text; $('status').classList.toggle('error', error);
}
function writeDraft() {
  try {
    if (changeVersion === savedVersion) localStorage.removeItem(draftKey);
    else localStorage.setItem(draftKey, JSON.stringify({schema_version: 2, revision, ...snapshot()}));
  } catch { /* Server saving and JSON download still work without browser storage. */ }
}
async function flush() {
  clearTimeout(timer);
  if (!config || saving || blocked || changeVersion === savedVersion) return;
  if (gesture) { timer = setTimeout(flush, 200); return; }
  saving = true;
  const version = changeVersion, payload = {revision, ...structuredClone(snapshot())};
  status('Saving…');
  let success = false;
  try {
    const response = await fetch('/api/annotations', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    const doc = await response.json();
    if (!response.ok) {
      blocked = response.status === 409;
      throw new Error(doc.error || 'Could not save.');
    }
    revision = doc.revision; savedVersion = version; success = true; writeDraft();
    status(changeVersion === savedVersion ? 'Saved.' : 'Saving newer changes…');
  } catch (error) {
    status(`${error.message} Your edits remain here; Download JSON keeps a copy.`, true);
  } finally {
    saving = false;
    if (success && changeVersion > savedVersion) timer = setTimeout(flush, 0);
  }
}
function changed() {
  changeVersion++; writeDraft(); clearTimeout(timer); timer = setTimeout(flush, 450);
  status('Unsaved changes…');
}
function commit() { history.push(snapshot()); changed(); render(); refreshEditor(); refreshList(); refreshSeries(); }
function refreshEditor() {
  const marker = records.find(m => m.id === selected);
  $('empty').hidden = Boolean(marker || pending); $('editor').hidden = !(marker || pending);
  $('editor-heading').textContent = pending ? 'New bead location' : 'Bead location and number';
  if (pending || marker) $('number').value = pending ? pending.number : marker.number;
  $('apply').textContent = pending ? 'Add bead' : 'Apply number';
  $('remove').hidden = !marker;
  $('undo').disabled = !history?.canUndo; $('redo').disabled = !history?.canRedo;
}
function refreshSeries() {
  const current = activeSeries();
  const numbers = ids => ids.map(id => records.find(m => m.id === id)?.number ?? '?').join(' → ');
  $('start').disabled = Boolean(current); $('end').disabled = !current || current.bead_ids.length < 2;
  $('direction').disabled = Boolean(current);
  $('pop').hidden = !current?.bead_ids.length;
  $('active').textContent = current ? `${current.direction}: ${numbers(current.bead_ids) || 'Click the starting bead.'} — click near the next bead, then End series.` : 'No active series. Click the photo to place beads.';
  $('direction-help').textContent = config?.directions[$('direction').value] || '';
  $('series-list').replaceChildren();
  series.forEach((item, index) => {
    const row = document.createElement('div'); row.className = 'series-row';
    const label = document.createElement('span');
    label.textContent = `${index + 1}. ${item.direction} ${item.status === 'active' ? '(active)' : ''}: ${numbers(item.bead_ids) || '(no clicks yet)'}`;
    const remove = document.createElement('button'); remove.textContent = item.status === 'active' ? 'Cancel series' : 'Remove series';
    remove.onclick = () => { series = series.filter(s => s.id !== item.id); commit(); };
    row.append(label, remove); $('series-list').append(row);
  });
}
function refreshList() {
  $('count').textContent = `${records.length} bead${records.length === 1 ? '' : 's'}`;
  $('list').replaceChildren();
  for (const marker of records) {
    const button = document.createElement('button');
    button.className = `marker-row${marker.id === selected ? ' selected' : ''}`;
    button.textContent = displayLabel(marker);
    button.title = `Bead ${marker.number}`; button.setAttribute('role', 'listitem');
    button.onclick = () => { if (activeSeries()) { recordClick(marker.id); return; } select(marker.id); if (withinCrop(marker, config.crop)) {
      const p = sourceToScreen(marker, view, config.crop); view.x += width / 2 - p.x; view.y += height / 2 - p.y; render();
    } else status('This marker is outside the current crop. Its annotation is preserved.'); };
    $('list').append(button);
  }
}
function select(id, focus = false) {
  selected = id; pending = null; refreshEditor(); refreshList(); refreshSeries(); render();
  if (focus) { $('number').focus(); $('number').select(); }
}
function remove() {
  if (!selected) return;
  const state = snapshot();
  try { removeBead(state, selected); records = state.annotations; selected = null; commit(); }
  catch (error) { status(error.message, true); }
}
function recordClick(id) {
  try { appendBead(snapshot(), id); selected = id; pending = null; commit(); }
  catch (error) { status(error.message, true); }
}
function travel(direction) {
  if (!history || gesture) return;
  restore(direction === 'undo' ? history.undo() : history.redo()); pending = null;
  if (!records.some(m => m.id === selected)) selected = null;
  changed(); render(); refreshEditor(); refreshList(); refreshSeries();
}
function render() {
  if (!image?.complete || !image.naturalWidth || !view) return;
  ctx.clearRect(0, 0, width, height); ctx.imageSmoothingEnabled = false;
  ctx.drawImage(image, view.x, view.y, image.width * view.scale, image.height * view.scale);
  boxes = [];
  $('zoom').textContent = `${Math.round(view.scale * 100)}%`;
  if (!$('show').checked) return;
  ctx.font = '13px system-ui, sans-serif';
  for (const item of series) {
    ctx.strokeStyle = seriesColors[item.direction]; ctx.lineWidth = item.status === 'active' ? 3 : 1.5;
    for (let i = 1; i < item.bead_ids.length; i++) {
      const a = records.find(m => m.id === item.bead_ids[i - 1]);
      const b = records.find(m => m.id === item.bead_ids[i]);
      if (!a || !b || !withinCrop(a, config.crop) || !withinCrop(b, config.crop)) continue;
      const start = sourceToScreen(a, view, config.crop), end = sourceToScreen(b, view, config.crop);
      const angle = Math.atan2(end.y - start.y, end.x - start.x);
      ctx.beginPath(); ctx.moveTo(start.x, start.y); ctx.lineTo(end.x, end.y); ctx.stroke();
      const tip = {x: start.x + (end.x - start.x) * .65, y: start.y + (end.y - start.y) * .65};
      ctx.beginPath(); ctx.moveTo(tip.x - 8 * Math.cos(angle - .45), tip.y - 8 * Math.sin(angle - .45));
      ctx.lineTo(tip.x, tip.y); ctx.lineTo(tip.x - 8 * Math.cos(angle + .45), tip.y - 8 * Math.sin(angle + .45)); ctx.stroke();
    }
  }
  if (pending) {
    const p = sourceToScreen(pending, view, config.crop);
    ctx.strokeStyle = '#ffdf70'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(p.x, p.y, 8, 0, Math.PI * 2); ctx.stroke();
  }
  for (const marker of records) {
    if (!withinCrop(marker, config.crop)) continue;
    const anchor = sourceToScreen(marker, view, config.crop);
    const textPoint = sourceToScreen({x: marker.x + marker.label_dx, y: marker.y + marker.label_dy}, view, config.crop);
    const text = displayLabel(marker), tw = ctx.measureText(text).width;
    const box = {id: marker.id, x: textPoint.x, y: textPoint.y - 18, w: tw + 10, h: 22};
    ctx.strokeStyle = marker.id === selected ? '#ffdf70' : '#77edff'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(anchor.x, anchor.y); ctx.lineTo(box.x, box.y + box.h); ctx.stroke();
    ctx.fillStyle = 'rgba(10,20,30,.85)'; ctx.fillRect(box.x, box.y, box.w, box.h);
    ctx.fillStyle = '#fff'; ctx.fillText(text, box.x + 5, box.y + 16);
    if (marker.id === selected) { ctx.strokeStyle = '#ffdf70'; ctx.strokeRect(box.x, box.y, box.w, box.h); }
    ctx.fillStyle = marker.id === selected ? '#ffdf70' : '#77edff';
    ctx.beginPath(); ctx.arc(anchor.x, anchor.y, 4, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#15222a'; ctx.stroke(); boxes.push(box);
  }
}
function hit(point) {
  if (!$('show').checked) return null;
  const nearest = nearestBead(point, records, view, config.crop, activeSeries() ? 18 : 10);
  if (nearest) return {id: nearest.id, kind: 'anchor'};
  for (const box of [...boxes].reverse()) {
    if (point.x >= box.x && point.x <= box.x + box.w && point.y >= box.y && point.y <= box.y + box.h)
      return {id: box.id, kind: 'label'};
  }
  return null;
}
function eventPoint(e) {
  const bounds = canvas.getBoundingClientRect(); return {x: e.clientX - bounds.left, y: e.clientY - bounds.top};
}
canvas.addEventListener('pointerdown', e => {
  if (gesture || !view || !image?.naturalWidth || ![0, 1, 2].includes(e.button)) return;
  const point = eventPoint(e), found = hit(point);
  const pan = space || e.button !== 0 || !$('show').checked;
  if (found && !pan && !activeSeries()) select(found.id);
  gesture = {pointerId: e.pointerId, start: point, last: point, originalView: {...view},
             kind: pan ? 'pan' : activeSeries() ? 'series' : found?.kind || 'new', id: found?.id,
             marker: found ? structuredClone(records.find(m => m.id === found.id)) : null, moved: false};
  canvas.setPointerCapture(e.pointerId); canvas.focus(); e.preventDefault();
});
canvas.addEventListener('pointermove', e => {
  if (!gesture || gesture.pointerId !== e.pointerId) return;
  const point = eventPoint(e), dx = point.x - gesture.start.x, dy = point.y - gesture.start.y;
  if (Math.hypot(dx, dy) > 3) gesture.moved = true;
  if (!gesture.moved) return;
  if (gesture.kind === 'pan') {
    view.x = gesture.originalView.x + dx; view.y = gesture.originalView.y + dy;
  } else if (gesture.kind === 'anchor' || gesture.kind === 'label') {
    const marker = records.find(m => m.id === gesture.id);
    if (gesture.kind === 'anchor') Object.assign(marker, clippedPoint({x: gesture.marker.x + dx / view.scale, y: gesture.marker.y + dy / view.scale}, config.crop));
    else { marker.label_dx = Math.max(-10000, Math.min(10000, gesture.marker.label_dx + dx / view.scale)); marker.label_dy = Math.max(-10000, Math.min(10000, gesture.marker.label_dy + dy / view.scale)); }
  } else { // Empty-space drag pans instead of adding an accidental marker.
    view.x = gesture.originalView.x + dx; view.y = gesture.originalView.y + dy;
  }
  gesture.last = point; render();
});
function finishGesture(e, cancelled = false) {
  if (!gesture || gesture.pointerId !== e.pointerId) return;
  const g = gesture; gesture = null;
  if (canvas.hasPointerCapture(e.pointerId)) canvas.releasePointerCapture(e.pointerId);
  if (cancelled) {
    if (g.marker) Object.assign(records.find(m => m.id === g.id), g.marker);
    view = g.originalView; render(); return;
  }
  if (g.kind === 'series' && !g.moved) {
    if (g.id) recordClick(g.id);
    else status('No numbered bead near that click. Click near a dot or its number; no bead was added.', true);
  } else if (g.moved && ['anchor', 'label'].includes(g.kind)) commit();
  else if (!g.moved && g.kind === 'new') {
    const point = screenToSource(eventPoint(e), view, config.crop);
    if (withinCrop(point, config.crop)) {
      selected = null; pending = {...point, number: nextNumber(records)};
      refreshEditor(); refreshList(); refreshSeries(); render(); $('number').focus(); $('number').select();
      status('Choose a unique number, then Add bead. The ring shows your chosen location.');
    }
  } else if (!g.moved && g.id && g.kind !== 'pan') select(g.id, true);
}
canvas.addEventListener('pointerup', e => finishGesture(e));
canvas.addEventListener('pointercancel', e => finishGesture(e, true));
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('wheel', e => {
  if (!view || gesture) return;
  e.preventDefault(); view = zoomAt(view, eventPoint(e), Math.exp(-Math.sign(e.deltaY) * .15)); render();
}, {passive: false});
$('editor').onsubmit = e => {
  e.preventDefault();
  try {
    const number = validNumber($('number').value, records, selected);
    if (pending) {
      const id = crypto.randomUUID(); records.push({id, x: pending.x, y: pending.y, number, label_dx: 6, label_dy: -6});
      pending = null; selected = id;
    } else {
      const marker = records.find(m => m.id === selected); if (!marker) return;
      marker.number = number;
    }
    commit(); canvas.focus();
  } catch (error) { status(error.message, true); $('number').focus(); }
};
$('cancel').onclick = () => { pending = null; select(null); };
$('direction').onchange = refreshSeries;
$('start').onclick = () => {
  if (pending) { status('Add or cancel the new bead before starting a series.', true); return; }
  try { startSeries(snapshot(), $('direction').value, crypto.randomUUID()); selected = null; $('show').checked = true; commit(); canvas.focus(); }
  catch (error) { status(error.message, true); }
};
$('end').onclick = () => {
  try { endSeries(snapshot()); commit(); }
  catch (error) { status(error.message, true); }
};
$('pop').onclick = () => { const current = activeSeries(); if (current?.bead_ids.length) { current.bead_ids.pop(); commit(); } };
$('remove').onclick = remove;
$('fit').onclick = () => { if (config) { view = fitView(width, height, config.crop); render(); } };
for (const [id, factor] of [['zoom-in', 1.3], ['zoom-out', 1 / 1.3]]) $(id).onclick = () => {
  if (view) { view = zoomAt(view, {x: width / 2, y: height / 2}, factor); render(); }
};
$('show').onchange = () => { render(); status($('show').checked ? activeSeries() ? 'Click numbered beads to extend the active series.' : 'Click a bead to choose its location.' : 'Raw image view. Drag to pan.'); };
$('undo').onclick = () => travel('undo'); $('redo').onclick = () => travel('redo'); $('save').onclick = flush;
$('download').onclick = () => {
  if (!config) return;
  const doc = {schema_version: 2, source: config.source, view_crop: config.crop, revision,
               annotation_kind: 'manual numbered bead locations and ordered direction series', direction_definitions: config.directions, ...snapshot()};
  const url = URL.createObjectURL(new Blob([JSON.stringify(doc, null, 2) + '\n'], {type: 'application/json'}));
  const a = document.createElement('a'); a.href = url; a.download = 'bead-annotations.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
};
window.addEventListener('keydown', e => {
  const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName);
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') { e.preventDefault(); flush(); }
  else if (!typing && (e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') { e.preventDefault(); travel(e.shiftKey ? 'redo' : 'undo'); }
  else if (!typing && e.code === 'Space') { e.preventDefault(); space = true; canvas.style.cursor = 'grab'; }
  else if (!typing && e.key === 'Delete') remove();
  else if (e.key === 'Escape') { pending = null; select(null); canvas.focus(); }
});
window.addEventListener('keyup', e => { if (e.code === 'Space') { space = false; canvas.style.cursor = 'crosshair'; } });
window.addEventListener('blur', () => { space = false; canvas.style.cursor = 'crosshair'; });
window.addEventListener('beforeunload', e => { if (changeVersion > savedVersion) { e.preventDefault(); e.returnValue = ''; } });
new ResizeObserver(() => {
  const oldWidth = width, oldHeight = height;
  width = canvas.clientWidth; height = canvas.clientHeight;
  const ratio = devicePixelRatio || 1; canvas.width = Math.round(width * ratio); canvas.height = Math.round(height * ratio);
  ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  if (view) { view.x += (width - oldWidth) / 2; view.y += (height - oldHeight) / 2; }
  else if (config) view = fitView(width, height, config.crop);
  render();
}).observe($('viewport'));

async function boot() {
  try {
    const response = await fetch('/api/config'); config = await response.json();
    if (!response.ok) throw new Error(config.error || 'Cannot load annotations.');
    records = config.document.annotations; series = config.document.series; revision = config.document.revision;
    draftKey = `bead-labeler-v2:${config.source.sha256}:${config.annotations_path}`;
    let restored = false;
    try {
      const draft = JSON.parse(localStorage.getItem(draftKey));
      if (draft && draft.schema_version === 2 && draft.revision === revision && Array.isArray(draft.annotations) && Array.isArray(draft.series)) {
        records = draft.annotations; series = draft.series; changeVersion++; restored = true;
      }
    } catch { /* A broken browser draft cannot replace the saved file. */ }
    history = new History(snapshot());
    image = new Image(); image.src = config.image_url; await image.decode();
    view = fitView(width, height, config.crop); refreshEditor(); refreshList(); refreshSeries(); render();
    status(restored ? 'Recovered unsaved edits. Save to keep them.' : activeSeries() ? 'Ready. Continue your saved active series.' : 'Ready. Click a bead to choose its location and number.');
    if (restored) timer = setTimeout(flush, 450);
  } catch (error) { status(error.message, true); }
}
boot();
