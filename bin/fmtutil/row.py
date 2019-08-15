import io, re
import string
import pandas as pd
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List
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

def pp(s) -> str:
  stream = io.StringIO()
  pprint(s,
    stream=stream,
    indent=2,
    width=220,
    # depth=_UNSET_SENTINEL, # default good
    compact=True, # noef?
    ribbon_width=220,
    max_seq_len=920, # noef?
    sort_dict_keys=True,
    end='\n' # the last line
  )
  return stream.getvalue()

def cp(s) -> str:
  stream = io.StringIO()
  cpprint(s,
    stream=stream,
    indent=2,
    width=220,
    # depth=_UNSET_SENTINEL, # default good
    compact=True, # noef?
    ribbon_width=220,
    max_seq_len=920, # noef?
    sort_dict_keys=True,
    end='\n' # the last line
  )
  return stream.getvalue()

class FmtdCellData:
  def __init__(self,
    funcname:str,
    fkncs:List,
    fvncs:List,
    fkcs:List,
    fvcs:List,
    ):
    self.fmtd_data = {k:v for k,v in zip(fkncs,fvncs)}
    self.fmtd_datac = {k:v for k,v in zip(fkcs,fvcs)}
    self.funcname = funcname
    self.args_keys = [k.strip().replace("'") for k in fkncs]

  def get_arg(self,argname,color=False):
    key_index = self.args_keys.index(argname)
    if color:
      for i,(k,v) in enumerate(self.fmtd_datac.items()):
        if i == key_index:
          return k, v
    else:
      for i,(k,v) in enumerate(self.fmtd_data.items()):
        if i == key_index:
          return k,v

def process_verbose_row(row):
  def process_call_datum(call_datum):
    rgx1 = re.compile(r"^(?P<indent>\s*)(?P<function>=>\s[A-z0-9_]+)\((?P<argvars>.*)\)$")
    m1 = rgx1.match(call_datum)
    gd1 = m1.groupdict()
    indent,function,argvars = gd1.values()
    keys,vals = parsed = parse_argvars(argvars)
    k0,k1 = keys
    v0,v1 = [eval(re.sub(r" <youtube_dl.utils.DateRange object at 0x111ed26a0>,",
                r" '<youtube_dl.utils.DateRange object at 0x111ed26a0>', ",v)) for v in vals]
    assert isinstance(v0,dict), v0
    assert isinstance(v1,dict), v1
    kncs,kcs = pp(k0),pp(k1),cp(k0),cp(k1)
    ks = kncs + kcs
    knoco0,knoco1,kco0,kco1 = fkncs,fkcs = [k.strip().replace("'","") for k in ks]
    vncs,vcs = pp(v0),pp(v1),cp(v0),cp(v1)
    vs = vncs + vcs
    vnoco0,vnoco1,vco0,vco1 = fvncs,fvcs = [v.strip().replace("'","") for v in vs]

    fmtd_cell_data = FmtdCellData(function,fkncs,fvncs,fkcs,fvcs)
    return fmtd_cell_data
  Index,filepath,line_number,symbol,event_kind,call_data,snoop_data = row
  assert isinstance(call_data,list), type(call_data)
  call_datum:str = call_data[0]
  fmtd_call_data = process_call_datum(call_datum)
  return fmtd_call_data

def _parse_argvars():
  firstflag = True
  kstr,vstr = "",""
  print(f"{vstr=}")
  keylst,vallst = [], []
  opnbrc,opnbrkt,opnparen = [],[],[]

  def entry(argvars:str):
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
      print(char)
      is_iter_start = check_start_iterable_symbol(char)
      if is_iter_start:
        continue
      is_iter_stop  = check_stop_iterable_symbol(char)
      if is_iter_stop:
        # if is_key_char():
        #   if vstr:
        #     vallst.append(vstr)
        #     vstr = ""
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

def initdf(initdf):
  initdf.iloc[10:14,0].filepath = 'extractor/__init__.py'
  initdf.iloc[14:16,:].filepath = 'downloader/__init__.py'
  initdflst = list(initdf.itertuples())
  idflm4 = initdflst[-4]
  print(idflm4)
  return idflm4

if __name__ == "__main__":
  dfpath=  Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/tfdf/idf.pkl')
  idf = pd.read_pickle(dfpath)
  row = initdf(idf)
  parsed = process_verbose_row(row)
  print(parsed)
