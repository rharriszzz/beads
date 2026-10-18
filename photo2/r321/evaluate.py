"""Reuse unmodified native R320 evaluator with the R321 geometry class."""
import photo2.r320.evaluate as implementation
from photo2.r297.common import ROOT
from .model import Chain
implementation.Chain=Chain
implementation.old_evidence.OUT=ROOT/'photo2/r321/results'
Evidence=implementation.Evidence
evaluate=implementation.evaluate
errors=implementation.errors
