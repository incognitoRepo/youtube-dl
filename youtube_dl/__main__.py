#!/Users/alberthan/VSCodeProjects/vytd/bin/ python3
from __future__ import unicode_literals

# Execute with
# $ python youtube_dl/__main__.py (2.6+)
# $ python -m youtube_dl          (2.7+)

import sys

if __package__ is None and not hasattr(sys, 'frozen'):
  # direct call of __main__.py
  import os.path
  path = os.path.realpath(os.path.abspath(__file__))
  sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import youtube_dl
import hunter
from youtube_dl.hunterconfig import QueryConfig
from hunter.tracer import Tracer
from pathlib import Path
from pdb import set_trace as st
import os
import pickle, sys

test = True

if __name__ == '__main__':
  if test:
    qc = QueryConfig()
    qcfg = [qc.eventpickle()]#,qc.noloop()]
    tracer = Tracer()
    for query,actions,outputs,filenames,write_func,epdf_pklpth in qcfg:
      tracer.trace(query)
      youtube_dl.main()
      # write_func()
      action = actions[0]
      evts_dcts = action.get_evt_dcts()
      with open('evts_dcts.pkl','wb') as f:
        pickle.dump(action.evt_dcts,f,pickle.HIGHEST_PROTOCOL)
      with open('evts_dcts.pkl','rb') as f:
        evts_dcts = pickle.load(f)

  else:
    youtube_dl.main()
