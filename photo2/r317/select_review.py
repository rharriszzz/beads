"""Add a Pareto review alternative without changing the sealed A/B/C selections."""
import numpy as np
from photo2.r297.common import read,save,utc
from .search import OUT,vals
from .refine import admissible

def main():
    rows=[read(p) for p in sorted((OUT/'trials').glob('*.gz'))];a0=vals(rows[3]);eligible=[r for r in rows if admissible(r) and np.all(vals(r)>=a0-1e-12)]
    chosen=min(eligible,key=lambda r:(-min(vals(r)[2],vals(r)[4]),-vals(r).mean()))
    save(OUT/'review-selection.json',dict(utc=utc(),selected=chosen['id'],eligible=len(eligible),policy='Additional post-search Pareto review candidate: retain all six R316 visible core fractions without regression, plus declared paper/bracket/worst-core limits; maximize smaller next-negative/+12 fraction, then six-core mean. No new geometric evaluations; original A/B/C selections remain unchanged. Comparison remains exposed, not validation.'))
if __name__=='__main__':main()
