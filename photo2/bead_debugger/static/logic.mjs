export const wrap=(k,n)=>((k%n)+n)%n;
export const indexOf=(generator,origin,n)=>wrap(generator-origin,n);
export const generatorOf=(k,origin,n)=>wrap(k+origin,n);
export function triple(k,n){const s=k<=Math.floor(n/2)?k:k-n,b=Math.floor((s+3)/7);return [s-7*b,0,b];}
export function reviewedSet(reviews,model,generation){return new Set(reviews.filter(r=>r.model_version===model.version&&r.generation_id===generation).map(r=>r.generator_index));}
export function nextUnchecked(gi,origin,n,done){for(let d=1;d<=n;d++){const q=wrap(gi+d,n);if(!done.has(q))return q;}return null;}
export function nearest(rows,point,getPoint=r=>[r.x,r.y],count=8){return rows.map(r=>({row:r,distance:Math.hypot(getPoint(r)[0]-point[0],getPoint(r)[1]-point[1])})).sort((a,b)=>a.distance-b.distance).slice(0,count);}
export function labelAllowed(rect,occupied){if(occupied.some(b=>rect[0]<b[2]&&rect[2]>b[0]&&rect[1]<b[3]&&rect[3]>b[1]))return false;occupied.push(rect);return true;}
