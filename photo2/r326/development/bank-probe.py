import json
from photo2.r326.compatibility import reconsider
from photo2.r323.tracker import save
x=json.load(open('photo2/r325/results/graph.json'));s,a=reconsider(x['windows'],x['global_solution'],x['stations_px'],x['period_px'])
save('photo2/r326/development/bank-probe.json',a)
print('kept',len(a['selected_windows']),'seconds',a['seconds'],'constraints',a['pair_constraints'],'changed',len(a['changed_from_cyclic']),'history',a['optimization'])
