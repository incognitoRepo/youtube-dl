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
import hunter, inspect
from youtube_dl.hunterconfig import QueryConfig
from prettyprinter import cpprint, pformat
from hunter.tracer import Tracer
from pathlib import Path
from ipdb import set_trace as st
import os, io, stackprinter
import pickle, sys
from optparse import OptionParser
from types import GeneratorType
from ansi2html import Ansi2HTMLConverter
from contextlib import contextmanager
from toolz.curried import compose_left
from hdlogger.tracers import hdTracer
from hdlogger.processors import TraceProcessor

test = True
output = True
dcts = []

def wf(filename,obj,mode="a"):
  path = Path(filename)
  if not path.parent.exists():
    path.mkdir(parents=True, exist_ok=True)
  if not isinstance(obj, str): obj = str(obj)
  if mode == "a" and not obj.endswith("\n"): obj = f"{obj}\n"
  with path.open(mode,encoding="utf-8") as f:
    f.write(obj)

@contextmanager
def captured_output():
  new_out, new_err = io.StringIO(), io.StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    sys.stdout, sys.stderr = new_out, new_err
    yield sys.stdout, sys.stderr
  except SystemExit as err:
    print('-- expected SystemExit: \x1b[1;32mSuccess\x1b[0m')
  except:
    sys.stdout, sys.stderr = old_out, old_err
    s = stackprinter.format(sys.exc_info()); print(s)
    # import IPython; IPython.embed()
    import ipdb; ipdb.post_mortem(sys.exc_info()[2])
    raise
  else:
    sys.stdout, sys.stderr = old_out, old_err
  finally:
    sys.stdout, sys.stderr = old_out, old_err

def setup():
  import sys
  import os
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  hd_tracer = hdTracer()

  try:
    with captured_output() as (io_out,io_err):
      sys.settrace(hd_tracer.trace_dispatch)
      youtube_dl.main()
  except SystemExit as err:
    print('-- expected SystemExit: \x1b[1;32mSuccess\x1b[0m')
    raise err
  except:
    wf('logs/error.except.main.log', stackprinter.format(sys.exc_info()), 'a')
    raise
  finally:
    output,error = io_out.getvalue(),io_err.getvalue()
    print(output)
    wf('logs/io_out.finally.log', output, 'a')
    wf('logs/io_err.finally.log', error, 'a')
  return (inspect.currentframe(), globals(), locals())

def go_interactive(pas):
  frame, glols, lols = pas
  filepath = '/Users/alberthan/VSCodeProjects/HDLogger/youtube-dl/logs/03.pickled_states_hex.tracer.log'
  tp = TraceProcessor(filepath)
  df = tp.dataframe
  import IPython; IPython.embed()

if __name__ == '__main__':
  compose_left(
    setup,
    go_interactive
  )()
