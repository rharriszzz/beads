"""Failure-oriented controls for connected growth and revision."""
from .grow import extend,search,SEED

def state(coords):return dict(coords=coords,H=None,returns=[],score=0.,path=[],skips=0)
def patch(w,ab,score=1.,i=0):return dict(window=w,hypothesis=i,patch=i,assignments=ab,edges=[],score=score)
def main():
    s=state({('a',0):(0,0),('b',0):(1,0)})
    p=patch(1,{'a':(0,0),'b':(1,0),'c':(0,1)})
    good,reason=extend(s,p,{(o,0):v for o,v in p['assignments'].items()});assert good and ('c',0) in good['coords']
    no,reason=extend(s,p,{('x',0):(0,0),('y',0):(1,0)});assert no is None and reason=='insufficient frontier overlap'
    no,reason=extend(s,p,{('a',0):(0,0),('b',0):(0,1)});assert no is None and reason=='shared-coordinate disagreement'
    no,reason=extend(s,p,{('a',0):(0,0),('b',0):(1,0),('c',0):(1,0)});assert no is None and 'one lattice site' in reason
    # A genuine return fixes a free translation; a second return contradicting
    # that translation must fail, even though the graph would be connected.
    s=state({('a',0):(0,0),('b',0):(1,0),('x',0):(9,9),('y',0):(10,9)})
    good,_=extend(s,p,{('x',0):(0,0),('y',0):(1,0),('a',1):(1,1),('b',1):(2,1)})
    assert good['H']==(10,10) and set(good['returns'])=={'a','b'}
    no,why=extend(s,p,{('x',0):(0,0),('y',0):(1,0),('a',1):(1,1),('b',1):(3,1)})
    assert no is None and why=='inconsistent return translation'
    # Width-one greedy choice cannot continue. Five-window rollback expands
    # alternatives and recovers a less attractive seed that continues.
    goodab={SEED:(0,0),'a':(0,1),'b':(1,0)};badab={SEED:(0,0),'a':(1,0),'b':(0,1)}
    bank=dict(period_px=1000.,stations_px={SEED:0.,'a':0.,'b':0.},windows=[dict(arc_px=i*20.) for i in range(8)])
    pp=[[patch(0,badab,10,0),patch(0,goodab,9,1)]]+[[patch(i,goodab,10)] for i in range(1,8)]
    r=search(bank,pp,width=1,budget=10)
    assert any(v['failed_step']==4 and v['reopen_from']==0 for v in r['rollbacks'])
    assert any(t['step']==7 and not t.get('failed') for t in r['trace'])
    assert not r['completed'] # geographic circuit deliberately has no return overlap
    print('PASS disconnected attach, row disagreement, duplicate site, free return, contradictory return, rollback, incomplete circuit')
if __name__=='__main__':main()
