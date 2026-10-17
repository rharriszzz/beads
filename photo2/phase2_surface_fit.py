#!/usr/bin/env python3
"""R313 bounded fixed-photographic-evidence surface experiment."""
import os,sys
from pathlib import Path
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/beads-r313-mpl')
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
    if sys.prefix==sys.base_prefix and (root/'.venv/bin/python').exists():os.execv(str(root/'.venv/bin/python'),[str(root/'.venv/bin/python'),__file__,*sys.argv[1:]])
    from photo2.r313.run import main
    main()
