import hunter
import re
import os
from typing import List, Dict, Iterable
from hunter import Q, Query
from hunter.predicates import And, When
from hunter.actions import CallPrinter, CodePrinter, VarsPrinter, VarsSnooper, CALL_COLORS, MISSING
import io,threading
from collections import namedtuple, defaultdict
from functools import partial
from fsplit.filesplit import FileSplit
from pathlib import Path
import pandas as pd
import pickle, sys
from enum import Enum
from pdb import set_trace as st
from dataclasses import dataclass, field, InitVar

def event_dict(e):
  """e: event"""
  code = {
  'co_filename': e.frame.f_code.co_filename,
  'co_name': e.frame.f_code.co_name,
  }
  frame = {
  'f_lineno': e.frame.f_lineno,
  'f_globals':  {
      k:v
      for k,v in e.frame.f_globals.items()
      if k in ("__file__", "__name__")
  },
  # 'f_locals': e.frame.f_locals,
  'f_code': code,
  }
  d = {
  # 'arg':e.arg,
  'calls':e.calls,
  # 'code':code,
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

@dataclass
class EventKind:
  event: InitVar
  event_kind: str = field(init=False)
  event_function: str = field(init=False)
  filename_prefix: str
  stack: int

  def __post_init__(self, event):
    self.event_kind = event.kind
    self.event_function = str(event.function)

@dataclass
class CallEvent(EventKind):
  symbol: str = "=>"
  separator: str = "   "
  event_function: str = field(init=False)
  varnames: List[str] = field(default_factory=list)
  argvars: Dict = field(default_factory=dict)

  def __post_init__(self, event):
    super().__post_init__(event)
    for var in event.code.co_varnames[:event.code.co_argcount]:
        self.varnames.append(var)
    self.event_function = event.function
    for var in self.varnames:
      try:
        val = str(event.locals.get(var))
      except:
        val = var
      self.argvars.update({var:val})

  def __str__(self):
    s = (
        f"{self.filename_prefix}{self.event_kind:9} "
        f"{self.separator}{self.symbol} "
        f"{self.event_function}({self.argvars})"
    )
    return s

@dataclass
class ExceptionEvent(EventKind):
  symbol: str = " !"
  separator: str = "   "
  varnames: List[str] = field(default_factory=list)
  arg: str = field(init=False)

  def __post_init__(self, event):
    super().__post_init__(event)
    if event.arg and isinstance(event.arg,Iterable):
      try:
        self.arg = {k:str(v) for k,v in event.arg}
      except:
        self.arg = "shouldnt have passed"
    else:
      self.arg = ""

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator * (len(self.stack) - 1)} "
      f"{self.event_function}: "
      f"{self.arg}\n"
    )
    return s

@dataclass
class ReturnEvent(EventKind):
  symbol: str = "<="
  separator: str = "   "
  event_arg: str = field(init=False)

  def __post_init__(self, event):
    super().__post_init__(event)
    if event.arg and isinstance(event.arg,Iterable):
      try:
        self.arg = {k:str(v) for k,v in event.arg}
      except:
        self.arg = str(event.arg)
    else:
      self.arg = ""

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator  * (len(stack) - 1)}{self.symbol} "
      f"{self.event_function}: {self.event_arg}\n"
    )
    return s

@dataclass
class LineEvent(EventKind):
  symbol: str = "<="
  separator: str = "   "
  source: str = field(init=False)

  def __post_init__(self, event):
    super().__post_init__(event)
    self.source = event.fullsource

  def __str__(self):
    s = (
      f"{self.filename_prefix}{self.event_kind:9} "
      f"{self.separator * len(self.stack)}"
      f"{self.source.strip()}\n"
    )
    return s

def update_evt_dct(evt_dct, event, filename_prefix, stack, output):
  d = {'call': CallEvent, 'line': LineEvent,
  'return': ReturnEvent, 'exception': ExceptionEvent}
  hntr_evt = d[event.kind](event,filename_prefix,stack)
  evt_dct['hunter_event'] = hntr_evt
  evt_dct['hunter_string'] = output
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
    self.count = 0
    self.evt_dcts = []

  def output_format(self, format_str, *args, **kwargs):
    """
    Write ``format_str.format(*args, **ANSI_COLORS, **kwargs)`` to ``self.stream``.

    For ANSI coloring you can place these in the ``format_str``:

    Args:
      format_str: a PEP-3101 format string
      *args:
      **kwargs:

    Returns: string
    """
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

  def __call__(self, event):
    """
    Handle event and print filename, line number and source code. If event.kind is a `return` or `exception` also
    prints values.
    """
    ident = event.module, event.function

    thread = threading.current_thread()
    stack = self.locals[thread.ident]

    pid_prefix = self.pid_prefix()
    thread_prefix = self.thread_prefix(event)
    filename_prefix = self.filename_prefix(event)
    evt_dct = event_dict(event)
    if event.kind == 'call':
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
      evt_dct = update_evt_dct(evt_dct, event, filename_prefix, stack, output)
      self.evt_dcts.append(evt_dct)
      self.write_output(output)
    elif event.kind == 'exception':
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
      Cap4(stream=io.StringIO(),repr_limit=4096), # repr_limit=1024
    ]
    outputs = [action.stream for action in actions]
    filenames = [base.joinpath(filename).absolute() for filename in ['call.fullcall.log']]
    assert len(filenames) == 1, filenames
    write_func = partial(self.write_func,outputs,filenames)
    pkldf = partial(self.pickle_df,dfpath=base.joinpath('fcdf.pkl'))
    query = And(
      Q(filename_contains="youtube",
            stdlib=True,
            actions=actions),
      ~Q(filename_contains="hunterconfig"))
    c = QueryConfig.Config(query,actions,outputs,filenames,write_func,pkldf)
    self.configs.append(c)
    return c


  def eventpickle(self):
    base = self.basedir.joinpath('bin/eventpickle').absolute()
    base.mkdir(parents=True,exist_ok=True)
    actions = [
      CustomPrinter(stream=io.StringIO(),repr_limit=4096), # repr_limit=1024
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
