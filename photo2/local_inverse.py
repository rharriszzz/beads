#!/usr/bin/env python3
"""Standalone R301 entry; automatically use the repository environment."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
venv=ROOT/'.venv/bin/python'
if Path(sys.prefix).resolve()!=venv.parent.parent.resolve():os.execv(str(venv),[str(venv),str(Path(__file__).resolve()),*sys.argv[1:]])
sys.path.insert(0,str(ROOT))
from photo2.r301.search import main
if __name__=='__main__':main()
