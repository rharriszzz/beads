import unittest
from collections import deque
import numpy as np
from .search_r269 import Neighborhood,Policy
from .climb_r268 import edge_reasons,Guards

class SearchTests(unittest.TestCase):
    def graph(self,v=None,sums=None,paper=None,hsv=None,start=(7,7),reference=None,side=5):
        v=np.full((15,15),200,np.uint8) if v is None else v
        sums=np.full(v.shape,200*side**2,np.int32) if sums is None else sums
        hsv=np.dstack((np.full(v.shape,.12),np.full(v.shape,.7),v/255)) if hsv is None else hsv
        paper=np.zeros(v.shape,np.uint8) if paper is None else paper
        return Neighborhood(v,hsv,paper,sums,side,start,reference,max_radius=6)

    def test_equal_then_shallow_descent_reaches_better_peak(self):
        scores=np.full((15,15),100*25);scores[7,7:12]=np.array([200,200,199,200,210])*25
        g=self.graph(sums=scores);r=g.search(6,Policy(12,2));self.assertEqual(g.xy[r['end']].tolist(),[11,7]);self.assertEqual(len(g.path(r['pred'],r['end'])),5)
        g.audit(g.path(r['pred'],r['end']),6,Policy(12,2))

    def test_search_radius_independent_of_score_window(self):
        scores=np.full((15,15),200*25);scores[7,12]=210*25;g=self.graph(sums=scores)
        self.assertEqual(g.xy[g.search(3,Policy())['end']].tolist(),[7,7])
        self.assertEqual(g.xy[g.search(6,Policy())['end']].tolist(),[12,7])

    def test_detour_around_substantial_valley(self):
        v=np.full((15,15),200,np.uint8);v[7,8]=100;scores=np.full(v.shape,200*25);scores[7,9]=210*25
        g=self.graph(v,scores);r=g.search(6,Policy());p=g.path(r['pred'],r['end'])
        self.assertEqual(g.xy[r['end']].tolist(),[9,7]);self.assertGreater(len(p),3);g.audit(p,6,Policy())

    def test_all_alternative_routes_blocked_by_valley(self):
        v=np.full((15,15),200,np.uint8);v[:,8]=150;scores=np.full(v.shape,200*25);scores[7,9]=210*25
        g=self.graph(v,scores);r=g.search(6,Policy());self.assertFalse(r['reachable'][g.index((9,7))]);cap,pred=g.widest(6,Policy())
        self.assertEqual(cap[g.index((9,7))],150)

    def test_background_and_diagonal_corners(self):
        paper=np.zeros((15,15),np.uint8);paper[7,8]=1;paper[8,7]=2;scores=np.full((15,15),100*25);scores[7,7]=scores[8,8]=200*25
        g=self.graph(sums=scores,paper=paper);self.assertFalse(g.search(6,Policy())['reachable'][g.index((8,8))])

    def test_raw_reference_preserves_original_prefix_peak(self):
        v=np.full((15,15),235,np.uint8);v[7,7]=245;scores=np.full(v.shape,200*25);scores[7,9]=210*25
        g=self.graph(v,scores,reference=250)
        self.assertEqual(g.search(6,Policy(12,2))['end'],g.start)
        self.assertEqual(g.xy[g.search(6,Policy(24,2))['end']].tolist(),[9,7])

    def test_clear_hue_boundary_and_circular_hue(self):
        hsv=np.full((15,15,3),[355/360,.7,.8]);hsv[:,8:,0]=5/360;g=self.graph(hsv=hsv)
        self.assertTrue(g.search(6,Policy())['reachable'][g.index((9,7))]);hsv[:,8:,0]=60/360;g=self.graph(hsv=hsv)
        self.assertFalse(g.search(6,Policy())['reachable'][g.index((9,7))])

    def test_ties_keep_anchor_and_replay(self):
        g=self.graph();a=g.search(6,Policy());b=g.search(6,Policy())
        self.assertEqual(a['end'],g.start);np.testing.assert_equal(a['pred'],b['pred'])

    def test_vector_color_guards_match_preserved_scalar_rules(self):
        rng=np.random.default_rng(269);hsv=rng.random((15,15,3));v=(hsv[:,:,2]*255).astype(np.uint8);paper=rng.integers(0,3,v.shape,dtype=np.uint8)
        g=self.graph(v=v,hsv=hsv,paper=paper);rules=Guards(raw_valley_dn=256)
        for a,b,bits in zip(g.a,g.b,g.colorbits):
            x,y=g.xy[a];xx,yy=g.xy[b];reasons=edge_reasons((x,y),(xx,yy),g.start_hsv,0,v,hsv,paper,rules)
            if xx!=x and yy!=y:
                for sx,sy in ((xx,y),(x,yy)):
                    reasons+=edge_reasons((x,y),(sx,sy),g.start_hsv,0,v,hsv,paper,rules)
                    reasons+=edge_reasons((sx,sy),(xx,yy),g.start_hsv,0,v,hsv,paper,rules)
            self.assertEqual(bool(bits),bool(reasons))

    def test_widest_path_agrees_with_independent_threshold_flood(self):
        rng=np.random.default_rng(927);v=rng.integers(180,221,(15,15),dtype=np.uint8);g=self.graph(v=v);policy=Policy(256,256,False)
        caps,pred=g.widest(6,policy)
        for level in (180,190,200,210,220):
            seen=set();q=deque()
            if v[7,7]>=level:seen.add((7,7));q.append((7,7))
            while q:
                x,y=q.popleft()
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        xx,yy=x+dx,y+dy
                        if not(dx or dy) or not(0<=xx<15 and 0<=yy<15) or (xx-7)**2+(yy-7)**2>36:continue
                        if v[yy,xx]<level:continue
                        if dx and dy and (v[y,xx]<level or v[yy,x]<level or (xx-7)**2+(y-7)**2>36 or (x-7)**2+(yy-7)**2>36):continue
                        if (xx,yy) not in seen:seen.add((xx,yy));q.append((xx,yy))
            expected={tuple(g.xy[i]) for i in np.flatnonzero(caps>=level)}
            self.assertEqual(seen,expected)

    def test_mean_floor_uses_exact_integer_sums(self):
        for k in range(49):
            scores=np.full((15,15),100*49);scores[7,7]=12000+k;scores[7,8]=12000+k-98;scores[7,9]=12000+k-99
            g=self.graph(sums=scores,side=7);r=g.search(6,Policy())
            self.assertTrue(r['reachable'][g.index((8,7))]);self.assertFalse(r['reachable'][g.index((9,7))])

    def test_background_anchor_remains_audited_but_does_not_expand(self):
        p=np.zeros((15,15),np.uint8);p[7,7]=1;g=self.graph(paper=p)
        r=g.search(6,Policy());self.assertEqual(len(r['order']),1);self.assertTrue(r['start_blocked'])

    def test_diagonal_side_pixels_must_stay_inside_search_disk(self):
        g=self.graph();spatial,bits=g.edge_masks(5,Policy())
        a=g.index((10,11));b=g.index((11,10));idx=np.flatnonzero((g.a==a)&(g.b==b))[0]
        self.assertFalse(spatial[idx])

if __name__=='__main__':unittest.main()
