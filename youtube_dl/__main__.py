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

import youtube_dl, inspect, traceback
from prettyprinter import cpprint, pformat
from pathlib import Path
from ipdb import set_trace as st
import os, io, stackprinter, pickle, hunter
from optparse import OptionParser
from types import GeneratorType
from typing import Any, Dict
from ansi2html import Ansi2HTMLConverter
from contextlib import contextmanager
from toolz.curried import compose_left
from hdlogger.utils import *
from hdlogger.serializers.tracers import hdTracer
from hdlogger.processors import TraceProcessor
from hdlogger.serializers.classes import PickleableFrame

test = True
output = True
dcts = []
vars_to_watch = ['count']

@contextmanager
def captured_output():
  new_out, new_err = io.StringIO(), io.StringIO()
  old_out, old_err = sys.stdout, sys.stderr
  try:
    # sys.stdout, sys.stderr = new_out, new_err
    sys.stdout, sys.stderr = old_out, old_err
    yield sys.stdout, sys.stderr
  except:
    s = stackprinter.format(sys.exc_info())
    wf(s, 'logs/captured_output.error.log', 'a')
    raise
  finally:
    sys.stdout, sys.stderr = old_out, old_err

def setup_debug():
  import sys, os
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  hd_tracer = hdTracer()
  sys.settrace(hd_tracer.trace_dispatch)
  try:
    youtube_dl.main()
  # except SystemExit as err:
    # wf(stackprinter.format(err), 'logs/system_exit.expected_error.log', 'a')
    # print('--- expected SystemExit: \x1b[1;32mSuccess\x1b[0m')
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main.log', 'a')
    raise
  finally:
    # hd_tracer.varswatcher.write_var_history()
    wf(output,'logs/setup_debug.finally0.log','a')
  return (inspect.currentframe(), globals(), locals())
def setup_debug2():
  import sys, os
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  hd_tracer = hdTracer()
  oldout,olderr = sys.stdout,sys.stderr
  sys.stdout = newout = io.StringIO()
  sys.stderr = newerr = io.StringIO()
  sys.settrace(hd_tracer.trace_dispatch)
  try:
    youtube_dl.main()
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main.log', 'a')
    raise
  finally:
    output,error = newout.getvalue(),newerr.getvalue()
    wf(output,'logs/stdout.finally2.log','a')
    wf(error,'logs/stderr.finally2.log','a')
  return (inspect.currentframe(), globals(), locals())

def setup_debug3():
  try:
    youtube_dl.main()
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main3.log', 'a')
    raise

def setup_hunter_code():
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  lines = io.StringIO()
  try:
    with hunter.trace(filename__contains="youtube",action=hunter.CodePrinter(stream=lines)):
      youtube_dl.main()
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main.log', 'a')
    raise
  finally:
    output = lines.getvalue()
    wf(output,'logs/hunteroutput.finally.log','a')
  return (inspect.currentframe(), globals(), locals())

def setup_hunter_call():
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  lines = io.StringIO()
  try:
    with hunter.trace(filename__contains="youtube",action=hunter.CallPrinter(stream=lines)):
      youtube_dl.main()
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main.log', 'a')
    raise
  finally:
    output = lines.getvalue()
    wf(output,'logs/huntercall.finally.log','a')
  return (inspect.currentframe(), globals(), locals())

def setup():
  import sys
  import os
  sys.path.insert(0, '/Users/alberthan/VSCodeProjects/HDLogger')
  hd_tracer = hdTracer(vars_to_watch)
  oldout,olderr = sys.stdout,sys.stderr
  sys.stdout = newout = io.StringIO()
  sys.stderr = newerr = io.StringIO()
  sys.settrace(hd_tracer.trace_dispatch)
  try:
    youtube_dl.main()
  # except SystemExit as err:
    # wf(stackprinter.format(err), 'logs/system_exit.expected_error.log', 'a')
    # print('--- expected SystemExit: \x1b[1;32mSuccess\x1b[0m')
  except:
    wf(stackprinter.format(sys.exc_info()), 'logs/error.except.main.log', 'a')
    raise
  finally:
    # hd_tracer.varswatcher.write_var_history()
    output,error = newout.getvalue(),newerr.getvalue()
    print(output)
    wf(output,'logs/stdout.finally.log','a')
    wf(error,'logs/stderr.finally.log','a')
  return (inspect.currentframe(), globals(), locals())

def process():
  filepath = '/Users/alberthan/VSCodeProjects/HDLogger/youtube-dl/logs/03.pickled_states_hex.tracer.log'
  tp = TraceProcessor(filepath)
  df = tp.dataframe.drop('attrs',1)
  tp.level1; tp.level_1
  sts = tp.pickleable_states
  maxstacklen = df['stacklen'].max() # 56
  try:
    df[df['stacklen'].apply(lambda cell: cell <= maxstacklen)]
  except:
    exc = sys.exc_info()
    tb = traceback.format_exception(*sys.exc_info())
    wf(tb,'logs/catchall.tb.log','w')
    sp = stackprinter.format(sys.exc_info())
    wf(sp,'logs/catchall.sp.log','w')

  try:
    df[df['stacklen'].apply(lambda cell: cell <= maxstacklen)]
  except Exception as e:
    exc = e
    tb = traceback.format_exception(*e)
    wf(tb,'logs/named.tb.log','w')
    sp = stackprinter.format(e)
    wf(sp,'logs/named.sp.log','w')

  wf(tp.level1,'logs/process.level1.log','a')
  wf(tp.level_1,'logs/process.level_1.log','a')

  # import IPython; IPython.embed()

if __name__ == '__main__':
  pas = setup_debug2()
  # go_interactive(pas)
  # process()
