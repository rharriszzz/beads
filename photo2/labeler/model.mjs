// Pure coordinate and history helpers; anchors stay in oriented source pixels.
export function sourceToScreen(point, view, crop) {
  return {x: view.x + (point.x - crop[0]) * view.scale,
          y: view.y + (point.y - crop[1]) * view.scale};
}
export function screenToSource(point, view, crop) {
  return {x: crop[0] + (point.x - view.x) / view.scale,
          y: crop[1] + (point.y - view.y) / view.scale};
}
export function fitView(width, height, crop) {
  const w = crop[2] - crop[0], h = crop[3] - crop[1];
  const scale = Math.max(.05, Math.min((width - 24) / w, (height - 24) / h));
  return {scale, x: (width - w * scale) / 2, y: (height - h * scale) / 2};
}
export function zoomAt(view, screen, factor) {
  const scale = Math.max(.05, Math.min(30, view.scale * factor));
  const ratio = scale / view.scale;
  return {scale, x: screen.x - (screen.x - view.x) * ratio,
          y: screen.y - (screen.y - view.y) * ratio};
}
export function withinCrop(point, crop) {
  return point.x >= crop[0] && point.x < crop[2] && point.y >= crop[1] && point.y < crop[3];
}
export function clippedPoint(point, crop) {
  return {x: Math.max(crop[0], Math.min(crop[2] - .001, point.x)),
          y: Math.max(crop[1], Math.min(crop[3] - .001, point.y))};
}
export function displayLabel(marker) {
  return String(marker.number);
}
const clone = value => JSON.parse(JSON.stringify(value));
export class History {
  constructor(records) { this.states = [clone(records)]; this.index = 0; }
  push(records) {
    if (JSON.stringify(records) === JSON.stringify(this.states[this.index])) return;
    this.states = this.states.slice(0, this.index + 1);
    this.states.push(clone(records));
    if (this.states.length > 101) this.states.shift();
    this.index = this.states.length - 1;
  }
  get canUndo() { return this.index > 0; }
  get canRedo() { return this.index < this.states.length - 1; }
  undo() { if (this.canUndo) this.index--; return clone(this.states[this.index]); }
  redo() { if (this.canRedo) this.index++; return clone(this.states[this.index]); }
}

// Numbers are maker-selected names, never interpreted as full-string indices.
export function validNumber(value, records, exceptId = null) {
  if (!/^-?\d+$/.test(String(value).trim())) throw new Error('Enter an integer bead number.');
  const number = Number(value);
  if (!Number.isSafeInteger(number)) throw new Error('That number is too large.');
  if (records.some(m => m.id !== exceptId && m.number === number)) throw new Error(`Bead ${number} already exists. Choose another number.`);
  return number;
}
export function nextNumber(records) {
  const used = new Set(records.map(m => m.number));
  let n = 1; while (used.has(n)) n++;
  return n;
}
export function nearestBead(point, records, view, crop, radius = 18) {
  let found = null, distance = radius;
  for (const marker of records) {
    if (!withinCrop(marker, crop)) continue;
    const p = sourceToScreen(marker, view, crop), d = Math.hypot(point.x - p.x, point.y - p.y);
    if (d <= distance) { found = marker; distance = d; }
  }
  return found;
}
export function startSeries(state, direction, id) {
  if (state.series.some(s => s.status === 'active')) throw new Error('End the active series first.');
  if (!['d1', 'd2', 'd3'].includes(direction)) throw new Error('Choose d1, d2 or d3.');
  if (!id || state.series.some(s => s.id === id)) throw new Error('Series ID must be unique.');
  state.series.push({id, direction, status: 'active', bead_ids: []});
}
export function appendBead(state, beadId) {
  const series = state.series.find(s => s.status === 'active');
  if (!series) throw new Error('Start a series first.');
  if (!state.annotations.some(m => m.id === beadId)) throw new Error('Select an existing numbered bead.');
  if (series.bead_ids.at(-1) === beadId) throw new Error('That bead is already the last click.');
  series.bead_ids.push(beadId);
}
export function endSeries(state) {
  const series = state.series.find(s => s.status === 'active');
  if (!series || series.bead_ids.length < 2) throw new Error('Click the starting bead and at least one more bead before ending.');
  series.status = 'complete';
}
export function removeBead(state, beadId) {
  if (state.series.some(s => s.bead_ids.includes(beadId))) throw new Error('This bead belongs to a series. Remove that series before deleting the bead.');
  state.annotations = state.annotations.filter(m => m.id !== beadId);
}
