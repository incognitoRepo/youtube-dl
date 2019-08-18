import io, re, sys
import string
import pandas as pd
from toolz.functoolz import compose_left
from ast import literal_eval
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Tuple
from pdb import set_trace as st
from prettyprinter import pprint
from prettyprinter import cpprint
from dataclasses import dataclass
from collections import namedtuple

def old_process_call_datum(call_datum):
    rgx1 = re.compile(r"^(?P<indent>\s*)(?P<function>=>\s[A-z0-9_]+)\((?P<argvars>.*)\)$")
    m1 = rgx1.match(call_datum)
    gd1 = m1.groupdict()
    indent,function,argvars = gd1.values()

    rgx2 = re.compile(r"{[^}]+,[^]]+}|(,)") # 562
    replacement = lambda m: "UniqStr" if m.group(1) else m.group(0)
    replaced = rgx2.sub(replacement, argvars)
    splitvars:List = replaced.split("UniqStr")
    splitdct=dict([(elm.split('=',1)) for elm in splitvars]) # keys=info_dict,params
    splitvals = list(splitdct.values())

    rgx3 = re.compile(r"(\'[^\']+)(\[\.{3}\])[^\']+,")
    rplcmt = lambda m: r"\1[...]'" if m.group(1) else m.group(0)
    spltvls = [rgx3.sub(r"\1[...]',",splitvals[0])for v in splitvals]
    # re.sub(r"(\'[^\']+)(\[\.{3}\])[^\']+,",r"\1[...]',",splitvals[0])

# def pp(s) -> str:
#   stream = io.StringIO()
#   pprint(s,
#     stream=stream,
#     indent=2,
#     width=220,
#     # depth=_UNSET_SENTINEL, # default good
#     compact=True, # noef?
#     ribbon_width=220,
#     max_seq_len=920, # noef?
#     sort_dict_keys=True,
#     end='\n' # the last line
#   )
#   return stream.getvalue()

# def cp(s) -> str:
#   stream = io.StringIO()
#   cpprint(s,
#     stream=stream,
#     indent=2,
#     width=220,
#     # depth=_UNSET_SENTINEL, # default good
#     compact=True, # noef?
#     ribbon_width=220,
#     max_seq_len=920, # noef?
#     sort_dict_keys=True,
#     end='\n' # the last line
#   )
#   return stream.getvalue()

def _parse_argvars() -> Tuple:
  firstflag = True
  kstr,vstr = "",""
  keylst,vallst = [], []
  opnbrc,opnbrkt,opnparen = [],[],[]

  def entry(argvars:str) -> Tuple[List,List]:
    if len(argvars) < 2000:
      parsed = argvars.split('=',1)
    parsed = parse_argvars(argvars)
    return parsed

  def check_start_iterable_symbol(char):
    nonlocal kstr,vstr
    if char == "{":
      vstr += "{"
      opnbrc.append("{")
      return True
    elif char == "[":
      vstr += "["
      opnbrkt.append("[")
      return True
    elif char == "(":
      vstr += "("
      opnparen.append("(")
      return True
    return False

  def check_stop_iterable_symbol(char):
    nonlocal kstr,vstr
    if char == "}":
      vstr += "}"
      opnbrc.pop()
      return True
    elif char == "]":
      vstr += "]"
      opnbrkt.pop()
      return True
    elif char == ")":
      vstr += ")"
      opnparen.pop()
      return True
    return False

  def is_val_char():
    """if any open symbol list has a value, char is valchar"""
    return any([opnbrc,opnbrkt,opnparen]) # no lst has a value

  def is_key_char():
    """if all lists are empty, char=keychar"""
    return not any([opnbrc,opnbrkt,opnparen]) # no lst has a value

  def is_equals_symbol(char):
    return char == "="

  def parse_argvars(argvars):
    nonlocal kstr,vstr
    nonlocal keylst,vallst
    nonlocal opnbrc,opnbrkt,opnparen
    for char in argvars:
      is_iter_start = check_start_iterable_symbol(char)
      if is_iter_start:
        continue
      is_iter_stop  = check_stop_iterable_symbol(char)
      if is_iter_stop:
        continue
      is_equalsign = is_equals_symbol(char)
      if is_equalsign and not is_val_char():
        keylst.append(kstr)
        kstr = ""
        continue
      elif is_val_char():
        assert len(keylst) >= 1, keylst
        vstr += char
        continue
      elif is_key_char():
        if char in "," or char in " ":
          continue
        assert char in string.ascii_letters+string.digits+"_", char
        if vstr:
          vstr = re.sub(r" <youtube_dl.utils.DateRange object at 0x111ed26a0>,",
            r" '<youtube_dl.utils.DateRange object at 0x111ed26a0>', ",
            vstr)
          vallst.append(vstr)
          vstr = ""
        kstr += char
        continue
      else:
        raise
    if vstr: vallst.append(vstr)
    return keylst,vallst

  sns = SimpleNamespace(entry=entry)
  return sns.entry

parse_argvars = _parse_argvars()

class FmtdCellData:
  def __init__(self,funcname):
    self.funcname = funcname

  def colorize(self,s) -> str:
    assert isinstance(s,str), s
    _stream = io.StringIO()
    try:
      litval = literal_eval(s)
      cpprint(litval,stream=_stream)
    except:
      cpprint(s,stream=_stream)
    rv = _stream.getvalue()
    _stream.close()
    return rv

class FmtdCallData(FmtdCellData):
  def __init__(self, funcname, keyslst, valslst):
    super().__init__(funcname)
    self.keyslst = keyslst
    self.valslst = valslst
    self.argnames = [k.strip().replace("'","") for k in self.keyslst]
    self.argvalues = [v.strip().replace("'","") for v in self.valslst]

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      d = {k:v for k,v in zip(self.argnames,self.argvalues)}
    if c or c == 'All':
      cz = self.colorize
      cd = {cz(k):cz(v) for k,v in zip(self.argnames,self.argvalues)}
    rv = (d,cd) if c == 'All' else d if not c else d
    return rv

class FmtdVerboseCallData(FmtdCellData):
  def __init__(self, funcname, keyslst, valslst):
    super().__init__(funcname)
    self.keyslst = keyslst
    self.valslst = valslst
    self.argnames = [k.strip().replace("'") for k in self.keyslst]
    self.argvalues = [v.strip().replace("'") for v in self.valslst]

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      d = {k:v for k,v in zip(self.argnames,self.argvalues)}
    if c or c == 'All':
      cz = self.colorize
      cd = {cz(k):cz(v) for k,v in zip(self.argnames,self.argvalues)}
    rv = (d,cd) if c == 'All' else d if not c else d
    return rv

class FmtdReturnData(FmtdCellData):
  def __init__(self, funcname, retvalslst):
    super().__init__(funcname)
    self.retvalslst = retvalslst

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      t =(self.funcname, self.retvalslst)
    if c or c == 'All':
      cz = self.colorize
      ct =(cz(self.funcname), cz(self.retvalslst))
    rv = (t,ct) if c == 'All' else t if not c else ct
    return rv
class FmtdExceptionData(FmtdCellData):
  def __init__(self, funcname, retvalslst):
    super().__init__(funcname)
    self.retvalslst = retvalslst

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      t =(self.funcname, self.retvalslst)
    if c or c == 'All':
      cz = self.colorize
      ct =(cz(self.funcname), cz(self.retvalslst))
    rv = (t,ct) if c == 'All' else t if not c else ct
    return rv

def process_verbose_row(row):
  print(1)

  def process_verbose_args(indent,function,argvars):
    keyslst,valslst = parsed = parse_argvars(argvars)
    fmtd_cell_data = FmtdVerboseCellData(function,keyslst,valslst)
    return fmtd_cell_data
    k0,k1 = keys

  def process_regular_args(indent,function,argvars):
    parse_argvars_ez = lambda s: map(str.strip,s.split('='))
    keys,vals = parsed = parse_argvars_ez(argvars)
    # print(indent,function,argvars)
    keylst,vallst = [keys],colorize_string(vals,e=True) # keep consistent with verbose
    fmtd_cell_data = FmtdCellData(f"{indent}{function}",keylst,vallst)
    return fmtd_cell_data

  def classify_whether_argvars_verbose(tplpak):
    indent,function,argvars = tplpak
    assert isinstance(argvars,str), argvars
    if len(argvars[1]) > 2000:
      return process_verbose_args(indent,function,argvars)
    else:
      return process_regular_args(indent,function,argvars)

  def prep_clean_classify_format(call_datum):
    calrgx = re.compile(r"(?P<indented_function>^\s*=\>\s[<>A-z0-9_-]+)\((?P<argname>\.\d+)=(?P<argval><[^>]+>)\)$")
    excrgx = re.compile(r"(?P<indented_function>^\s*\<=\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
    retrgx = re.compile(r"(?P<indented_function>^\s*\s!\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
    print(11)
    if '=>' in call_datum:
      print(22)
      #      call: '{COLOR}=>{NORMAL} {}({}{COLOR}{NORMAL}){RESET}\n'
      if m1 := calrgx.match(call_datum):
        print('a')
        gd1 = m1.groupdict()
        indented_function,argname,argval = gd1.values()
        keyslst,valslst = [argname],[argval] # keep consistent with verbose
        fmtd_cell_data = FmtdCallData(indented_function,keyslst,valslst)
        return fmtd_cell_data
        print('b')
    elif '<=' in call_datum:
      print(33)
      #    return: '{COLOR}<={NORMAL} {}: {RESET}{}\n',
      if m2 := excrgx.match(call_datum):
        gd2 = m2.groupdict()
        indented_function,retvals = gd2.values()
        retvalslst = [retvals] # keep consistent with verbose
        fmtd_cell_data = FmtdReturnData(indented_function,retvalslst)
        return fmtd_cell_data
    elif ' !' in call_datum:
      print(44)
      # exception: '{COLOR} !{NORMAL} {}: {RESET}{}\n',
      if m3 := retrgx.match(call_datum):
        gd3 = m3.groupdict()
        indented_function,retvals = gd3.values()
        retvalslst = [retvals] # keep consistent with verbose
        fmtd_cell_data = FmtdExceptionData(indented_function,retvalslst)
        return fmtd_cell_data
    print(55)
    return fmtd_cell_data

  print(2)
  Index,filepath,line_number,symbol,event_kind,call_data,snoop_data = row
  call_datum = call_data[0]
  print(3)
  fmtd_data = prep_clean_classify_format(call_datum)
  print(4)
  assert isinstance(call_data,list), type(call_data)
  return fmtd_data


def prep_clean_classify_format(call_datum):
  calrgx = re.compile(r"(?P<indented_function>^\s*=\>\s[<>A-z0-9_-]+)\((?P<argname>\.\d+)=(?P<argval><[^>]+>)\)$")
  excrgx = re.compile(r"(?P<indented_function>^\s*\<=\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
  retrgx = re.compile(r"(?P<indented_function>^\s*\s!\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
  print(1)
  if '=>' in call_datum:
    print(2)
    #      call: '{COLOR}=>{NORMAL} {}({}{COLOR}{NORMAL}){RESET}\n'
    if m1 := calrgx.match(call_datum):
      gd1 = m1.groupdict()
      indented_function,argname,argval = gd1.values()
      keyslst,valslst = [argname],[argval] # keep consistent with verbose
      fmtd_cell_data = FmtdCallData(indented_function,keyslst,valslst)
      return fmtd_cell_data
  elif '<=' in call_datum:
    print(3)
    #    return: '{COLOR}<={NORMAL} {}: {RESET}{}\n',
    if m2 := excrgx.match(call_datum):
      gd2 = m2.groupdict()
      indented_function,retvals = gd2.values()
      retvalslst = [retvals] # keep consistent with verbose
      fmtd_cell_data = FmtdReturnData(indented_function,retvalslst)
      return fmtd_cell_data
  elif ' !' in call_datum:
    print(4)
    # exception: '{COLOR} !{NORMAL} {}: {RESET}{}\n',
    if m3 := retrgx.match(call_datum):
      gd3 = m3.groupdict()
      indented_function,retvals = gd3.values()
      retvalslst = [retvals] # keep consistent with verbose
      fmtd_cell_data = FmtdExceptionData(indented_function,retvalslst)
      return fmtd_cell_data
  print(5)
  return fmtd_cell_data

def initdf(initdf):
  initdf.iloc[10:14,0].filepath = 'extractor/__init__.py'
  initdf.iloc[14:16,:].filepath = 'downloader/__init__.py'
  initdflst = list(initdf.itertuples())
  idflm4 = initdflst[-4]
  # print(idflm4)
  return idflm4

if __name__ == "__main__":
  dfpath=  Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/tfdf/idf.pkl')
  idf = pd.read_pickle(dfpath)
  row = initdf(idf)
  # st()
  parsed = process_verbose_row(row)
  # print(dir(parsed))
  # print(parsed.funcname)
  # print(parsed.fmtd_data)
  # print(parsed.fmtd_datac)
  print(parsed.args_keys)
  info_dict, idval= parsed.get_arg('info_dict')
  params, parval= parsed.get_arg('params')
  print(idval)
  print(parval)
  info_dict, idval= parsed.get_arg('info_dict',color=True)
  params, parval= parsed.get_arg('params',color=True)
  print(idval)
  print(parval)



