import json,time
from photo2.r326.compatibility import compatible_subset
x=json.load(open('photo2/r325/results/graph.json'))
s,a=compatible_subset(x['windows'],x['global_solution'],x['stations_px'],x['period_px'])
print('kept',len(a['selected_windows']),'conflicts',len(a['pair_conflicts']),'seconds',a['seconds'],'cycles',a['cycle_audit'])
print('abstain',a['abstained_windows'])
json.dump(a,open('photo2/r326/development/baseline-compatibility.json','w'),indent=2)
