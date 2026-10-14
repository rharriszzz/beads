/**
 * R277 exploratory photo-only motif scan.
 *
 * This is NOT full crochet-string indexing, NOT a recovered repeat length.
 * It uses the heuristic R275 station/side associations, which have uncertainty.
 * Search treats forward and reversed motifs, with and without side exchange,
 * as distinct hypotheses. Never infer a physical bead index from station number.
 *
 * Run from repo root:
 *   node photo2/diagonal_motif_probe_r277.mjs > /tmp/beads-r277-motifs.json
 * Optional: --permutations 100
 */
import fs from 'node:fs';
import assert from 'node:assert/strict';
const CODE={red:0,yellow:1,black:2};
function makeSequence(stations,locations){
  const byId=new Map(locations.map(p=>[p.id,p]));
  return stations.groups.map(g=>{
    const result=[-1,-1];
    for(const id of g.ids){
      const p=byId.get(id);
      if(!p) throw Error('Station references unknown observation '+id);
      const side=p.signed_distance>0?1:0;
      if(result[side]!==-1) throw Error('Ambiguous duplicated station side '+id);
      result[side]=CODE[p.color];
      if(result[side]===undefined) throw Error('Unexpected color '+p.color);
    }
    return result;
  });
}
function compare(a,i,j,width,transform){
  let n=0,m=0,per=[0,0];
  for(let t=0;t<width;t++){
    const left=a[i+t],right=a[j+((transform&2)?width-1-t:t)];
    for(let side=0;side<2;side++){
      const x=left[side],y=right[(transform&1)?1-side:side];
      if(x<0||y<0) continue;
      n++;per[side]++;
      if(x===y)m++;
    }
  }
  return {n,m,per};
}
function scan(a,width,baseline,minimumSeparation=28,limit=18){
  const results=[];let max=-Infinity;
  const minN=Math.max(18,Math.floor(width*.8));
  const minSide=Math.max(5,Math.floor(width/4));
  for(let i=0;i<a.length-width;i++)
    for(let j=i+Math.max(minimumSeparation,width+2);j<a.length-width;j++)
      for(let tr=0;tr<4;tr++){
        const c=compare(a,i,j,width,tr);
        if(c.n<minN||c.per[0]<minSide||c.per[1]<minSide)continue;
        const score=(c.m-baseline*c.n)/Math.sqrt(baseline*(1-baseline)*c.n);
        if(score>max)max=score;
        if(limit && score>=5.3)
          results.push({first_station:i+1,second_station:j+1,window_stations:width,
            mode:(tr&2?'reversed':'forward')+(tr&1?'-swapped-sides':'-same-sides'),
            matches:c.m,comparable:c.n,match_fraction:c.m/c.n,exploratory_z:score});
      }
  results.sort((x,y)=>y.exploratory_z-x.exploratory_z);
  const distinct=[];
  for(const item of results){
    if(distinct.some(d=>Math.abs(d.first_station-item.first_station)<12 &&
                          Math.abs(d.second_station-item.second_station)<12))continue;
    distinct.push(item);
    if(distinct.length>=limit)break;
  }
  return {max_score:max,examples:distinct};
}
function blockShuffle(a,random,blockSize=8){
  const chunks=[];
  for(let i=0;i<a.length;i+=blockSize)chunks.push(a.slice(i,i+blockSize));
  for(let i=chunks.length-1;i>0;i--){
    const j=Math.floor(random()*(i+1));
    [chunks[i],chunks[j]]=[chunks[j],chunks[i]];
  }
  return chunks.flat();
}
function prng(seed){
  let state=seed>>>0;
  return ()=>{state=(Math.imul(state,1664525)+1013904223)>>>0;return state/4294967296};
}
function test(){
  const a=Array.from({length:40},()=>[-1,-1]);
  const shape=[[0,1],[1,2],[2,0],[2,1],[1,0],[0,2]];
  for(let t=0;t<6;t++){
    a[0+t]=shape[t];
    a[20+t]=[shape[5-t][1],shape[5-t][0]];
  }
  const found=compare(a,0,20,6,3);
  assert.equal(found.n,12);assert.equal(found.m,12);
  assert.equal(compare(a,0,20,6,0).m<12,true);
}
export function analyze(stations,locations,{permutations=40}={}){
  test();
  const a=makeSequence(stations,locations);
  const counts=[0,0,0];
  for(const row of a)for(const color of row)if(color>=0)counts[color]++;
  const n=counts.reduce((x,y)=>x+y,0);
  const baseline=counts.reduce((x,y)=>x+y*y,0)/(n*n);
  const widths=[18,24,30];
  const windows=Object.fromEntries(widths.map(w=>[w,scan(a,w,baseline)]));
  const random=prng(20261013), nullScores=[];
  for(let i=0;i<permutations;i++)
    nullScores.push(scan(blockShuffle(a,random),18,baseline,28,0).max_score);
  nullScores.sort((x,y)=>x-y);
  const observed=windows[18].max_score;
  const p=(1+nullScores.filter(x=>x>=observed).length)/(permutations+1);
  return {
    description:'Photographic station-color motif hints only; NOT reconstructed crochet string or an exact repeat',
    source:['photo2/review/r275/stations.json','photo2/review/r275/angular-locations.json'],
    stations:a.length,photographic_observations:n,color_counts:{red:counts[0],yellow:counts[1],black:counts[2]},
    null_baseline_match_fraction:baseline,
    method:'Compare two 2-sided station windows under forward/reverse and side-swap, with unknown colors omitted. Windows must have observations on both sides. Greedy overlap suppression retains distinct examples.',
    window_results:windows,
    exploratory_null:{
      method:'Shuffle whole eight-station blocks; preserves within-block colors, local runs, and paired-side missingness. Search maximum across all translations/reflections. Not a formal inference for physical crochet repeats.',
      permutations,observed_max_score:observed,maximum_null_score:nullScores.at(-1),
      median_null_score:nullScores[Math.floor(permutations/2)],finite_sample_p_upper:p
    },
    known_limitations:[
      'R275 stations are heuristic associations, not independently verified physical stitch rows',
      'Color similarities are not exact physical string repeats; nearly repeated and reflected motifs are explicitly allowed',
      'A shifted station index is not a fixed shift in the original bead-string index',
      'No 3D correspondence, hidden-bead labels, repeat length or unique string pattern is inferred',
      'The null is exploratory; local geometry and color runs can generate spurious peaks'
    ]
  };
}
if(process.argv[1] && import.meta.url===new URL('file://'+process.argv[1]).href){
  const arg=process.argv.indexOf('--permutations');
  const permutations=arg<0?40:Number(process.argv[arg+1]);
  if(!Number.isInteger(permutations)||permutations<0||permutations>1000)throw Error('Invalid permutation count');
  const base='photo2/review/r275/';
  const stations=JSON.parse(fs.readFileSync(base+'stations.json','utf8'));
  const locations=JSON.parse(fs.readFileSync(base+'angular-locations.json','utf8'));
  console.log(JSON.stringify(analyze(stations,locations,{permutations}),null,2));
}
