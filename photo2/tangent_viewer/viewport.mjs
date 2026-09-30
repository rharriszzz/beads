export function toSource(point, view) {
  return {x: (point.x - view.x) / view.scale, y: (point.y - view.y) / view.scale};
}
export function toScreen(point, view) {
  return {x: point.x * view.scale + view.x, y: point.y * view.scale + view.y};
}
export function zoomAt(view, pivot, factor) {
  const source = toSource(pivot, view);
  const scale = Math.max(.025, Math.min(32, view.scale * factor));
  return {scale, x: pivot.x - source.x * scale, y: pivot.y - source.y * scale};
}
export function fitView(width, height, rect) {
  const [x0, y0, x1, y1] = rect;
  const scale = Math.max(.025, Math.min(32, Math.min(width / (x1-x0), height / (y1-y0)) * .95));
  return {scale, x: (width-(x1-x0)*scale)/2-x0*scale, y: (height-(y1-y0)*scale)/2-y0*scale};
}
export function resizeView(view, oldSize, newSize) {
  return {...view, x: view.x + (newSize.width-oldSize.width)/2,
                   y: view.y + (newSize.height-oldSize.height)/2};
}
// Changing the model invalidates outstanding replies without moving the view.
export class RequestGate {
  constructor() { this.generation = 0; }
  invalidate() { return ++this.generation; }
  accepts(generation) { return generation === this.generation; }
}
