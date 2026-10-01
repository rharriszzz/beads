// Independent observations in original-photo coordinates; never model indices.
export class Marks {
  constructor(points=[]) { this.points=structuredClone(points);this.history=[];this.version=0; }
  change(operation) {
    const before=structuredClone(this.points);
    operation();
    this.history.push(before);if(this.history.length>50)this.history.shift();this.version++;
  }
  add(point,id=crypto.randomUUID()) {
    if(this.points.length>=200)throw new Error('At most 200 center marks are supported.');
    const number=Math.max(0,...this.points.map(p=>p.number))+1;
    this.change(()=>this.points.push({id,number,x:point.x,y:point.y}));return id;
  }
  move(id,point) {
    if(!this.points.some(p=>p.id===id))throw new Error('Select a center first.');
    this.change(()=>Object.assign(this.points.find(p=>p.id===id),{x:point.x,y:point.y}));
  }
  remove(id) { if(this.points.some(p=>p.id===id))this.change(()=>{this.points=this.points.filter(p=>p.id!==id);}); }
  renumber(id,number) {
    if(!Number.isInteger(number)||number<1||number>100000||this.points.some(p=>p.id!==id&&p.number===number))
      throw new Error('Use a unique positive whole number.');
    if(!this.points.some(p=>p.id===id))throw new Error('Select a center first.');
    this.change(()=>{this.points.find(p=>p.id===id).number=number;});
  }
  undo() { if(this.history.length){this.points=this.history.pop();this.version++;} }
}

export function hitMark(points,source,scale,radius=10) {
  let closest=null,distance=radius;
  for(const p of points) {
    const d=Math.hypot(p.x-source.x,p.y-source.y)*scale;
    if(d<=distance){closest=p.id;distance=d;}
  }
  return closest;
}
export function isClick(maxTravel) { return maxTravel<=4; }
