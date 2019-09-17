#// vscode-fold=1
import hunter
import re
import os
from functools import singledispatchmethod
from typing import List, Dict, Iterable, Union
from hunter import Q, Query
from hunter.predicates import And, When
from hunter.actions import CallPrinter, CodePrinter, VarsPrinter, VarsSnooper, CALL_COLORS, MISSING
import io,threading
from collections import namedtuple, defaultdict
from functools import partial
from fsplit.filesplit import FileSplit
from pathlib import Path
from tblib import Traceback
import pandas as pd
import pickle, sys
import traceback
from enum import Enum
from pdb import set_trace as st
from dataclasses import dataclass, field, InitVar

@dataclass
class EventKind:
  event: InitVar
  event_kind: str = field(init=False)
  event_function: str = field(init=False)
  filename_prefix: str
  stack: int
  argvars: Dict = field(default_factory=dict)

  def get_argvars(self,event):
    """event.arg from sys.settrace(tracefunc)
    ..call: `None`
    ..line: `None`
    ..return: `retval` or `None` (if exc)
    ..exception: `(exception, value, traceback)`
               : `(type, value, traceback)`
               : `(exception_class, instance, traceback)`
    """
    raise NotImplementedError("setup the dispatch")

  def __post_init__(self, event):
    d = {'call': self.get_argvars, 'line': lambda e: e.fullsource,
    'return': self.get_argvars, 'exception': self.get_argvars}
    self.event_kind = event.kind
    self.event_function = str(event.function)
    self.argvars = d[event.kind](event)

@dataclass
class CallEvent(EventKind):
  symbol: str = "=>"
  separator: str = "   "

  def get_argvars(self,event):
    varnames = event.code.co_varnames
    argcount = event.code.co_argcount
    avs = {}
    for var in varnames:
      try:
        val = str(event.locals.get(var))
      except AttributeError:
        val = repr(event.locals.get(var))
      except:
        val = 'error'
      avs.update({var:val})
    self.argvars = avs
    return

  def __str__(self):
    s = (
        f"{self.filename_prefix}{self.event_kind:9} "
        f"{self.separator * (len(self.stack) - 1)}{self.symbol} "
        f"{self.event_function}({self.argvars})"
    )
    return s

@dataclass
class ExceptionEvent(EventKind):
  symbol: str = " !"
  separator: str = "   "

  def get_argvars(self,event):
    """event.arg from sys.settrace(tracefunc)
    ..exception: `(exception, value, traceback)`
               : `(type, value, traceback)`
               : `(exception_class, instance, traceback)`
    """
    d = {
      "exception": event.arg[0],
      "value": event.arg[1],
      "traceback": event.arg[2]
    }
    self.argvars = d
    return

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator * (len(self.stack) - 1)} "
      f"{self.event_function}: "
      f"{self.argvars}\n"
    )
    return s

@dataclass
class ReturnEvent(EventKind):
  symbol: str = "<="
  separator: str = "   "

  def get_argvars(self,event):
    """event.arg from sys.settrace(tracefunc)
    ..return: `retval` or `None` (if exc)
    """
    if not event.arg:
      self.argvars = None
    elif isinstance(event.arg,str):
      try:
        self.argvars = str(event.arg)
      except:
        self.argvars = repr(event.arg)
    elif isinstance(event.arg,Iterable):
      if isinstance(event.arg,Dict):
        try:
          self.argvars = {k:str(v) for k,v in event.arg}
        except:
          self.argvars = {k:repr(v) for k,v in event.arg}
      elif isinstance(event.arg,List):
        try:
          self.argvars = [str(elm) for elm in event.arg]
        except:
          self.argvars = [repr(elm) for elm in event.arg]
    else:
      self.argvars = "else"
    return

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator  * (len(self.stack) - 1)}{self.symbol} "
      f"{self.event_function}: {self.argvars}\n"
    )
    return s

@dataclass
class LineEvent(EventKind):
  symbol: str = "<="
  separator: str = "   "

  def get_argvars(self, event):
    sauce = str(event.fullsource)
    self.argvars = sauce
    return

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator * len(self.stack)}"
      f"{self.argvars}\n"
    )
    return s

def update_evt_dct(evt_dct, event, filename_prefix, stack, output):
  d = {'call': CallEvent, 'line': LineEvent,
  'return': ReturnEvent, 'exception': ExceptionEvent}
  hntr_evt = d[event.kind](event,filename_prefix,stack)
  evt_dct['hunter_event'] = hntr_evt
  evt_dct['hunter_monostr'] = str(hntr_evt)
  evt_dct['hunter_polystr'] = output
  return evt_dct

class CustomPrinter(CallPrinter):
  """
  An action that just prints the code being executed, but unlike :obj:`hunter.CodePrinter` it indents based on
  callstack depth and it also shows ``repr()`` of function arguments.

  Args:
    stream (file-like): Stream to write to. Default: ``sys.stderr``.
    filename_alignment (int): Default size for the filename column (files are right-aligned). Default: ``40``.
    force_colors (bool): Force coloring. Default: ``False``.
    repr_limit (bool): Limit length of ``repr()`` output. Default: ``512``.
    repr_func (string or callable): Function to use instead of ``repr``.
      If string must be one of 'repr' or 'safe_repr'. Default: ``'safe_repr'``.

  .. versionadded:: 1.2.0
  """
  EVENT_COLORS = CALL_COLORS

  def __init__(self, *args, **kwargs):
    super(CustomPrinter, self).__init__(*args, **kwargs)
    self.locals = defaultdict(list)
    self.count = count(0)
    self.evt_dcts = []

  def filename_prefix(self, event=None):
    if event:
      filename = Path(event.filename) or '<???>'
      if filename.stem == "init":
        filename2 = f"{filename.parent.stem[0]}{filename.stem}"
      else:
        filename2 = f"{filename.stem}"
      filename3 = filename2[:self.filename_alignment]
      return '{:>{}}{COLON}:{LINENO}{:<5} '.format(
        filename3, self.filename_alignment, event.lineno, **self.other_colors)
    else:
      return '{:>{}}       '.format('', self.filename_alignment)

  def output_format(self, format_str, *args, **kwargs):
    output = (format_str.format(
      *args,
      **dict(self.other_colors, **kwargs)
    ))
    return output

  def write_output(self,outstr):
      self.stream.write(outstr)

  def get_locals(self,event,var):
    if event.detached:
      return event.locals.get(var, MISSING)
    else:
      return self.try_repr(event.locals.get(var, MISSING))

  def get_evt_dcts(self):
    self_id = id(self)
    return self.evt_dcts

  def event_dict(self,e,count):
    """e: event"""
    d = {
    'arg':e.arg,
    'calls':e.calls,
    'count':count,
    # 'code':e.code,
    'depth':e.depth,
    # 'detach':e.detach,
    # 'detached':e.detached,
    'filename':e.filename,
    # 'frame':frame,
    'fullsource':e.fullsource,
    'function':e.function,
    # 'function_object':e.function_object,
    # 'globals':frame['f_globals'],
    'kind':e.kind,
    'lineno':e.lineno,
    # 'locals':e.locals,
    'module':e.module,
    'source':e.source
    }
    return d

  def __call__(self, event):
    live_event = event
    event = event.detach(value_filter=lambda value: self.try_repr(value))
    ident = event.module, event.function

    thread = threading.current_thread()
    stack = self.locals[thread.ident]

    pid_prefix = self.pid_prefix()
    thread_prefix = self.thread_prefix(live_event)
    filename_prefix = self.filename_prefix(live_event)
    evt_dct = self.event_dict(event,next(self.count))
    if event.kind == 'call':
      # :event.arg: None = None
      code = event.code
      stack.append(ident)
      output = self.output_format(
        '{}{}{}{KIND}{:9} {}{COLOR}=>{NORMAL} {}({}{COLOR}{NORMAL}){RESET}\n',
        pid_prefix,
        thread_prefix,
        filename_prefix,
        event.kind,
        '   ' * (len(stack) - 1),
        event.function,
        ', '.join('{VARS}{VARS-NAME}{0}{VARS}={RESET}{1}'.format(
          var,
          event.locals.get(var, MISSING) if event.detached else self.try_repr(event.locals.get(var, MISSING)),
          **self.other_colors
        ) for var in code.co_varnames[:code.co_argcount]),
        COLOR=self.event_colors.get(event.kind),
      )
      evt_dct = update_evt_dct(evt_dct,event,filename_prefix,stack,output)
      self.evt_dcts.append(evt_dct)
      self.write_output(output)
    elif event.kind == 'exception':
      # :event.arg: tuple = (exception, value, traceback)
      output = self.output_format(
        '{}{}{}{KIND}{:9} {}{COLOR} !{NORMAL} {}: {RESET}{}\n',
        pid_prefix,
        thread_prefix,
        filename_prefix,
        event.kind,
        '   ' * (len(stack) - 1),
        event.function,
        event.arg if event.detached else self.try_repr(event.arg),
        COLOR=self.event_colors.get(event.kind),
      )
      evt_dct = update_evt_dct(evt_dct,event,filename_prefix, stack, output)
      self.evt_dcts.append(evt_dct)
      self.write_output(output)

    elif event.kind == 'return':
      # :event.arg: = return value or `None` if exception
      output = self.output_format(
        '{}{}{}{KIND}{:9} {}{COLOR}<={NORMAL} {}: {RESET}{}\n',
        pid_prefix,
        thread_prefix,
        filename_prefix,
        event.kind,
        '   ' * (len(stack) - 1),
        event.function,
        event.arg if event.detached else self.try_repr(event.arg),
        COLOR=self.event_colors.get(event.kind),
      )
      evt_dct = update_evt_dct(evt_dct, event,filename_prefix, stack, output)
      self.evt_dcts.append(evt_dct)
      self.write_output(output)
      if stack and stack[-1] == ident:
        stack.pop()
    else:
      # :event.arg: = `None`
      output = self.output_format(
        '{}{}{}{KIND}{:9} {RESET}{}{}{RESET}\n',
        pid_prefix,
        thread_prefix,
        filename_prefix,
        event.kind,
        '   ' * len(stack),
        self.try_source(event).strip(),
      )
      evt_dct = update_evt_dct(evt_dct, event,filename_prefix, stack, output)
      self.evt_dcts.append(evt_dct)
      self.write_output(output)

def patched_filename_prefix2(self, event=None):
  if event:
    filepath = Path(event.filename) or '<???>'
    filename = filepath.stem
  if filename.startswith("__init__"):
    filename = f"{filepath.parts[-2][0]}.{filename}"
  if filename.startswith("microsoft"):
    filename = "ms_vac"
  self.filename_alignment = 26
  if len(filename) > self.filename_alignment:
    filename = '[...]{}'.format(filename[5 - self.filename_alignment:])
    return '{:>{}}{COLON}:{LINENO}{:<5} '.format(
        filename, self.filename_alignment, event.lineno, **self.other_colors)
  else:
   return '{:>{}}       '.format('', self.filename_alignment)



def safe_deep_repr(obj, maxdepth=10):
  if not maxdepth:
    return '...'
  obj_type = type(obj)
  newdepth = maxdepth - 1

  # specifically handle few of the container builtins that would normally do repr on contained values
  if isinstance(obj, dict):
      if obj_type is not dict:
          return '%s({%s})' % (
              obj_type.__name__,
              ', '.join('%s: %s' % (
                  safe_repr(k, maxdepth),
                  safe_repr(v, newdepth)
              ) for k, v in obj.items()))
      else:
          return '{%s}' % ', '.join('%s: %s' % (
              safe_repr(k, maxdepth),
              safe_repr(v, newdepth)
          ) for k, v in obj.items())
  elif isinstance(obj, list):
      if obj_type is not list:
          return '%s([%s])' % (obj_type.__name__, ', '.join(safe_repr(i, newdepth) for i in obj))
      else:
          return '[%s]' % ', '.join(safe_repr(i, newdepth) for i in obj)
  elif isinstance(obj, tuple):
      if obj_type is not tuple:
          return '%s(%s%s)' % (
              obj_type.__name__,
              ', '.join(safe_repr(i, newdepth) for i in obj),
              ',' if len(obj) == 1 else '')
      else:
          return '(%s%s)' % (', '.join(safe_repr(i, newdepth) for i in obj), ',' if len(obj) == 1 else '')
  elif isinstance(obj, set):
      if obj_type is not set:
          return '%s({%s})' % (obj_type.__name__, ', '.join(safe_repr(i, newdepth) for i in obj))
      else:
          return '{%s}' % ', '.join(safe_repr(i, newdepth) for i in obj)
  elif isinstance(obj, frozenset):
      return '%s({%s})' % (obj_type.__name__, ', '.join(safe_repr(i, newdepth) for i in obj))
  elif isinstance(obj, deque):
      return '%s([%s])' % (obj_type.__name__, ', '.join(safe_repr(i, newdepth) for i in obj))
  elif isinstance(obj, BaseException):
      return '%s(%s)' % (obj_type.__name__, ', '.join(safe_repr(i, newdepth) for i in obj.args))
  elif obj_type in (type, types.ModuleType,
          types.FunctionType, types.MethodType,
          types.BuiltinFunctionType, types.BuiltinMethodType,
          io.IOBase):
      # hardcoded list of safe things. note that isinstance ain't used
      # (we don't trust subclasses to do the right thing in __repr__)
      return repr(obj)
  elif not has_dict(obj_type, obj):
      return repr(obj)
  else:
      # if the object has a __dict__ then it's probably an instance of a pure python class, assume bad things
      #  with side-effects will be going on in __repr__ - use the default instead (object.__repr__)
      return object.__repr__(obj)

CustomPrinter.safe_repr = safe_deep_repr
CustomPrinter.filename_prefix = patched_filename_prefix2
class QueryConfig:
  """note: changes in __call__ methods are visible in ytdev not ytdf"""
  Config = namedtuple('Config' , 'query actions outputs filenames write_func epdf_pklpth')

  def __init__(self):
    self.basedir = Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl')
    self.fulldir = self.basedir.joinpath('bin/agg.full').absolute()
    self.configs = []

  def write_func(self,outputs,filenames):
    for filename in filenames:
        fndir = filename.parent
        fndir.mkdir(parents=True,exist_ok=True)
    for output,filename in zip(outputs,filenames):
        with open(filename, 'w') as f:
          f.write(output.getvalue())
    for filename in filenames:
        dirname = filename.parent
        new_pth_cmpts = dirname.relative_to(self.basedir)
        outdir = self.basedir.joinpath(new_pth_cmpts)
        fs = FileSplit(file=filename, splitsize=1_100_000, output_dir=outdir)
        fs.split()

  def fullcall(self):
    base = self.basedir.joinpath('bin/agg.fullcall').absolute()
    base.mkdir(parents=True,exist_ok=True)
    actions = [
      CallPrinter(stream=io.StringIO(),repr_limit=4096), # repr_limit=1024
    ]
    outputs = [action.stream for action in actions]
    filenames = [base.joinpath(filename).absolute() for filename in ['call.fullcall.log']]
    assert len(filenames) == 1, filenames
    write_func = partial(self.write_func,outputs,filenames)
    epdf_pklpth = base.joinpath('epdf.pkl')
    query = And(
      Q(filename_contains="youtube",
            stdlib=True,
            actions=actions),
      ~Q(filename_contains="hunterconfig"))
    c = QueryConfig.Config(query,actions,outputs,filenames,write_func,epdf_pklpth)
    self.configs.append(c)
    return c

  def eventpickle(self):
    base = self.basedir.joinpath('bin/eventpickle').absolute()
    base.mkdir(parents=True,exist_ok=True)
    actions = [
      # CustomPrinter(stream=io.StringIO(),repr_limit=4096), # repr_limit=1024
      CustomPrinter(repr_limit=4096), # repr_limit=1024
    ]
    outputs = [action.stream for action in actions]
    filenames = [base.joinpath(filename).absolute() for filename in ['call.eventpickle.log']]
    write_func = partial(self.write_func,outputs,filenames)
    epdf_pklpth = base.joinpath('epdf.pkl')
    query = And(
      Q(filename_contains="youtube",
            stdlib=True,
            actions=actions),
      ~Q(filename_contains="hunterconfig"))
    c = QueryConfig.Config(query,actions,outputs,filenames,write_func,epdf_pklpth)
    self.configs.append(c)
    return c

  # Args: query: criteria to match on.

  # Accepted arguments:
  # `arg`,
  # `calls`,
  # `code`,
  # `depth`,
  # `filename`,
  # `frame`,
  # `fullsource`,
  # `function`,
  # `globals`,
  # `kind`,
  # `lineno`,
  # `locals`,
  # `module`,
  # `source`,
  # `stdlib`,
  # `threadid`,
  # `threadname`.
