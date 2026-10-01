// Score-domain coordinates are independent of photograph zoom and pan.
export function scoreBounds(rows) {
  const ys=rows.map(r=>r.sse),lo=Math.min(...ys),hi=Math.max(...ys);
  const padding=(hi-lo||Math.max(1,Math.abs(lo)*.01))*.05;
  return {xMin:rows[0].count,xMax:rows.at(-1).count,yMin:lo-padding,yMax:hi+padding};
}
function axis(low,high,boundLow,boundHigh,minSpan) {
  const span=Math.min(boundHigh-boundLow,Math.max(minSpan,high-low));
  const start=Math.max(boundLow,Math.min(boundHigh-span,low));
  return [start,start+span];
}
export function constrainScoreView(view,bounds) {
  if(!['xMin','xMax','yMin','yMax'].every(k=>Number.isFinite(view[k]))||view.xMin>=view.xMax||view.yMin>=view.yMax)
    throw new Error('Use finite graph ranges with From smaller than To.');
  const [xMin,xMax]=axis(view.xMin,view.xMax,bounds.xMin,bounds.xMax,1);
  const [yMin,yMax]=axis(view.yMin,view.yMax,bounds.yMin,bounds.yMax,(bounds.yMax-bounds.yMin)*1e-6);
  return {xMin,xMax,yMin,yMax};
}
export function zoomScore(view,bounds,pivot,factor,axes='both') {
  if(!Number.isFinite(factor)||factor<=0)throw new Error('Zoom factor must be positive and finite.');
  const next={...view};
  for(const [a,b,key] of [['xMin','xMax','x'],['yMin','yMax','y']]) {
    if(axes!=='both'&&axes!==key)continue;
    const fraction=Math.max(0,Math.min(1,pivot[key])),anchor=view[a]+fraction*(view[b]-view[a]);
    const minimum=key==='x'?1:(bounds.yMax-bounds.yMin)*1e-6;
    const span=Math.min(bounds[b]-bounds[a],Math.max(minimum,(view[b]-view[a])/factor));
    next[a]=anchor-fraction*span;next[b]=next[a]+span;
  }
  return constrainScoreView(next,bounds);
}
export function panScore(view,bounds,dx,dy) {
  return constrainScoreView({xMin:view.xMin+dx,xMax:view.xMax+dx,yMin:view.yMin+dy,yMax:view.yMax+dy},bounds);
}
export function fitScoreY(view,bounds,rows) {
  let subset=rows.filter(r=>r.count>=view.xMin&&r.count<=view.xMax);
  if(!subset.length)subset=[nearestScore(rows,(view.xMin+view.xMax)/2)];
  const ys=subset.map(r=>r.sse),lo=Math.min(...ys),hi=Math.max(...ys),padding=(hi-lo||Math.max(1,Math.abs(lo)*.01))*.05;
  return constrainScoreView({...view,yMin:lo-padding,yMax:hi+padding},bounds);
}
export function nearestScore(rows,count) {
  // Sorted sample counts; logarithmic lookup for hover and single-count zoom.
  let low=0,high=rows.length-1;
  while(low<high){const mid=Math.floor((low+high)/2);if(rows[mid].count<count)low=mid+1;else high=mid;}
  if(low && Math.abs(rows[low-1].count-count)<Math.abs(rows[low].count-count))return rows[low-1];
  return rows[low];
}
