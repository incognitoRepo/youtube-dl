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
from prettyprinter import cpprint
from hunter.tracer import Tracer
from pathlib import Path
from pdb import set_trace as st
import os, io, stackprinter
import pickle, sys
from optparse import OptionParser
from types import GeneratorType
from ansi2html import Ansi2HTMLConverter

test = True
output = True
dcts = []

if __name__ == '__main__':
  print(f"\x1b[0;36m{youtube_dl}\x1b[0m")
  qc = QueryConfig()
  qcfg = qc.eventpickle()
  tracer = Tracer()
  query,actions,outputs,filenames,write_func,epdf_pklpth = qcfg
  filename = filenames[0]
  action = actions[0]
  if output:
    output = io.StringIO()
    action._stream = output
  tracer.trace(query)
  try:
    youtube_dl.main()
  except SystemExit:
    tb1 = stackprinter.format(sys.exc_info())
    try:
      tracer.stop()
      if output:
        outval = output.getvalue()
        conv = Ansi2HTMLConverter()
        html = conv.convert(outval)
        output.close()
        with open(outvalpth:=filename.parent.joinpath('output.log'),'w') as f:
          f.write(outval)
          print(f"wrote output value to {outvalpth}")
        with open(htmlpth:=filename.parent.joinpath('output.html','w')) as f:
          f.write(html)
          print(f"wrote html output to {htmlpth}")
      evt_dcts = action.read_from_pickle()
      dcts.append(evt_dcts)
    except BaseException as exc:
      tb2 = stackprinter.format(exc)
      with open('tb.log','w') as f:
        f.write(tb1)
        f.write(tb2)
      print("failed")
