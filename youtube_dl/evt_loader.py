#// vscode-fold=1
import pickle, regex
import pandas as pd
import urllib, http, optparse
from urllib.parse import urlparse, ParseResult
from validator_collection import validators, checkers
from hunter import CallPrinter
from ipdb import set_trace as st
import sys, shelve, re, codecs
from typing import Iterable
import stackprinter
from prettyprinter import pformat
from bs4 import BeautifulSoup
from pathlib import Path
from textwrap import TextWrapper

stackprinter.set_excepthook(
  style='lightbg2',#'darkbg3',
  source_lines=5,
  show_signature=True,
  show_vals='like_source',
  truncate_vals=500)

def info(o):
  try:
    lng = len(o)
  except TypeError as exc:
    lng = "cannot len this obj"
  typ = type(o)
  s = f"\n\n{typ}, {lng}\n{repr(o)}\n\n"
  return s

def auto_repr(obj):
  try:
    class_name = obj.__class__.__name__
    part_1 = f'<{class_name}: '
    items = []
    _d = obj.__dict__
    d = {k:v for k,v in _d.items() if not (k.startswith('_'))}
    for k,v in d.items():
      try:
        if is_class(v): nv = auto_repr(v)
        elif isinstance(v,dict): nv = pformat(v)
        else: nv = repr(v)
        s = f'{k} = {nv}'
        items.append(s)
      except:
        with open('auto_repr.log','w') as f:
          f.write(f"{obj}")
        raise SystemExit
    secondary_indent = ' '*len(part_1)
    part_2 = f',{secondary_indent}'.join(items)
    return f'{part_1}{part_2}>'
  except AttributeError:
    with open('auto_repr.log','w') as f:
      f.write(f"{obj}")
    raise SystemExit

def dict_prnt(d):
  # prints relevant info i.e., truncates attrs starting with '_' or '__'
  key_lst = list(d.keys())
  key_lst2 = [k for k in key_lst if not (k.startswith('_') or k.startswith('__'))]
  new_dct = {k:d[k] for k in key_lst2}
  ns = prettyprinter.pformat(new_dct)
  return ns

def clr(s,category=""):
  blk,red,grn,ylw,blu,mag,cyn,wht = (
    0,  1,  2,  3,  4,  5,  6,  7)
  rset,bold,fain,ital,undr = (
    0 ,  1 ,  2 ,  3 ,  4)
  intns_fg,reglr_fg =  9,3
  intns_bg,reglr_bg = 10,4
  if s == "()":
    return f"\x1b[{rset};{reglr_fg}{blu}m{s}\x1b[{rset}m"
  if category == "module":
    return f"\x1b[{fain};{reglr_fg}{blk}m{s}\x1b[{rset}m"
  if category == "klass":
    return f"\x1b[{bold};{reglr_fg}{blk}m{s}\x1b[{rset}m"
  if category == "key":
    return f"\x1b[{bold};{reglr_fg}{ylw}m{s}\x1b[{rset}m"
  if category == "bool":
    return f"\x1b[{bold};{reglr_fg}{cyn}m{s}\x1b[{rset}m"
  if category == "int":
    return f"\x1b[{bold};{reglr_fg}{mag}m{s}\x1b[{rset}m"
  if category == "url":
    return f"\x1b[{ital};{reglr_fg}{grn}m{s}\x1b[{rset}m"
  if category == "shortstr":
    return f"\x1b[{fain};{reglr_fg}{blk}m{s}\x1b[{rset}m"
  if category == "none":
    return f"\x1b[{fain};{reglr_fg}{red}m{s}\x1b[{rset}m"

class StrCtnsAngBrkt:
  def __call__(self, s):
    if "<" in s:
      return True
    return False

  def is_func_repr(self, s, c=False):
    """e.g.,
    '<optparse.IndentedHelpFormatter object at 0x1095fd250>'
    returns: newly formatted string | False
    """
    rgx = re.compile(r"^<(?P<module>[a-z_]+)[.](?P<klass>[A-z_0-9]+)\sobject\sat\s0x[0-9a-f]+>$")
    m = rgx.match(s[1])
    if m:
      module, klass = m.groupdict().values()
      ns = f"{module}.{klass}" if not c else f"{clr(module,'module')}.{clr(klass,'klass')}"
      return ns
    else:
      return False

class Containers:
  def __call__(self,s):
    if "[" in s or "{" in s:
      return True
    return False

  def str_implies_container_BAK(self,s,depth,c=False):
    """returns newly formatted string | False
    ..args: s - must be a repr!
    """
    depth += 2
    join_str = f"\n{' '*depth}"
    # if isinstance(s,list) or isinstance(s,dict):
    #   return self.dispatch_container_type(s,depth=depth,c=c)
    if len(s) < 80:
      return s
    elif "[" in s or "{" in s:
      py_obj = self.make_eval_able(s)
      if isinstance(py_obj,str):
        ns = py_obj if not c else py_obj
        return ns
      elif isinstance(py_obj,list):
        ns = self.process_list(py_obj,depth=depth) if not c else self.process_list(py_obj,depth=depth,c=True)
        nl = ["[",ns,"]"]
        return join_str.join(nl)
      elif isinstance(py_obj,dict):
        ns = self.process_dict(py_obj,depth=depth) if not c else self.process_dict(py_obj,depth=depth,c=True)
        nl = ["{",ns,"}"]
        return join_str.join(nl)
      else:
        with open('el04','a') as f:
          f.write(stackprinter.format())
          f.write(s)
        raise SystemExit
    else:
      assert isinstance(s, str), info(s)
      return s

  def process_list(self,lst,depth,c=False):
    join_str = f",\n{' '*depth}"
    new_lst = []
    for elm in lst:
      new_e = process_vs(elm,depth=depth,c=c)
      new_lst.append(new_e)
    try:
      s = join_str.join(new_lst)
    except Exception as exc:
      with open('el16','a') as f:
        f.write(stackprinter.format(exc))
        f.write('\n'.join(new_lst))
      raise SystemExit
    return s

  def process_dict(self,dct,depth,c=False):
    join_str = f",\n{' '*depth}"
    new_d = {}
    for k,v in dct.items():
      new_v = process_vs(v,depth=depth,c=c)
      new_d.update({k:new_v})
    new_lst = []
    for k,v in new_d.items():
      nv = process_vs(v,depth=depth,c=c)
      if (isinstance(nv,list) or isinstance(nv,tuple)) and (len(nv) == 1):
        nv = nv[0]
      new_str = f"{k}: {v}" if not c else f"{clr(k,'key')}: {nv}"
      new_lst.append(new_str)
    fin_str = join_str.join(new_lst)
    return fin_str

  def make_eval_able(self,s):
    """returns a python object"""
    try:
      py_obj=eval(s)
      return py_obj
    except SyntaxError as exc:
      if len(s) < 200:
        return s
      else:
        with open('el155','a') as f:
          f.write(stackprinter.format())
          f.write(stackprinter.format(exc))
          f.write('\n----\n'+s+'\n')
        raise SystemExit

str_cnts_ang_brkt = StrCtnsAngBrkt()
containers = Containers()

def is_url(url):
  if checkers.is_url(url):
    result = validators.url(url)
    return result
  else:
    return False

def is_regex(s):
  try:
    rgx = re.compile(s)
    return rgx
  except:
    return False

def get_text_bs(html):
  tree = BeautifulSoup(html, 'lxml')
  body = tree.body
  if body is None:
    return None
  for tag in body.select('script'):
    tag.decompose()
  for tag in body.select('style'):
    tag.decompose()
  text = body.get_text(separator='\n')
  return text

def process_dcts(dcts,c=False):
  ds =dcts
  fmtd_dcts = []
  for d in ds:
    fmtd_dct = {}
    ks = list(d.keys())
    vs = list(d.values())
    new_ks = ks if not c else [clr(elm,'key') for elm in ks]
    new_vs = process_vs(vs,c=c)
    for k,v in zip(new_ks,new_vs):
      fmtd_dct.update({k:v})
    fmtd_dcts.append(fmtd_dct)
  return fmtd_dcts

def process_vs(vs,depth=0,c=False):
  new_vs = []
  if not isinstance(vs,list):
    vs = [vs]
  for v in vs:
    sv = repr(v)
    if not v:
      ns = "None" if not c else clr("None","none")
      new_vs.append(ns)
    elif "%" in sv:
      ns = sv
      new_vs.append(ns)
    elif sv.lower() in ('true','false'): # bool
      ns_val = 'True' if sv.lower() == 'true' else 'False'
      ns = ns_val if not c else clr(ns_val,'bool')
      new_vs.append(ns)
    elif sv.isnumeric():
      ns = sv if not c else clr(sv,'int')
      new_vs.append(ns)
    elif is_url(v) or isinstance(v,ParseResult):
      ns = urlparse(v).geturl() if not c else clr(urlparse(v).geturl(),'url')
      new_vs.append(ns)
    elif rgx:=is_regex(sv):
      ns =repr(rgx)
      new_vs.append(ns)
    elif isinstance(v,urllib.response.addinfourl) or isinstance(v,http.client.HTTPResponse):
      v = v.__dict__
      sv = auto_repr(v)
      ns = process_vs(sv,depth=depth) if not c else process_vs(sv,depth=depth,c=True)
      new_vs.append(ns)
    elif sv.startswith("<"):
      if sv.startswith("<Values"):
        process_dict = containers.process_dict
        d = v.__dict__
        sv = repr(v)
        ns = process_dict(d,depth=depth) if not c else process_dict(d,depth=depth,c=True)
        new_vs.append('\n'+ns)
      elif sv.startswith("<!DOCTYPE html>"):
        ns = get_text_bs(v)
        new_vs.append(ns)
      elif sv.startswith("<_io"):
        ns = ns.__class__
        new_vs.append(ns)
      elif isinstance(v,optparse.OptionParser):
        ns = v.get_usage()
        new_vs.append(ns)
      else:
        try:
          if hasattr(v,'__dict__'):
            # startswith any(['class','method','function'])
            # ns = containers.process_dict(d,depth=depth) if not c else containers.process_dict(d,depth=depth,c=True)
            ns = dict_prnt(v.__dict__)
            new_vs.append(ns)
          else:
            sv = sv[1:]
            lst = sv.split(' ')
            ns = f"{lst[0]}.{lst[1]}"
            new_vs.append(ns)
        except Exception as exc:
          with open('el232','a') as f:
            f.write(stackprinter.format())
            f.write('='*80+"\n"+info(v))
    elif len(sv) < 200:
      rv = repr(v)
      ns = rv if not c else clr(rv,'shortstr')
      new_vs.append(ns)
    elif containers(sv):
      d = {"[":containers.process_list,
        "{": containers.process_dict,
        "(": containers.process_list}
      implies = lambda s: s.startswith("[") or s.startswith("{") or s.startswith("(")
      if isinstance(v,str):
        for k,v in d.items():
          if k in sv:
            try:
              evld = eval(sv)
              ns = d[k](evld,depth=depth)
              new_vs.append(ns)
            except:
              try:
                if len(sv) < 200:
                  ns = sv
                  new_vs.append(ns)
                else:
                  ns = d[k](sv,depth=depth)
                  new_vs.append(ns)
              except:
                with open('el272','a') as f:
                  f.write(
                    f'could not eval possible container type\n'
                    f'key: {k}\n'
                    f'value: {info(sv)}\n'
                    f'stackprinter traceback:\n {stackprinter.format(sys.exc_info())}'
                  )
          else:
            with open('el283','a') as f:
              f.write(
                f'im not sure y we are here\n'
                f'key: {k}\n'
                f'value: {info(sv)}\n'
              )
            raise SystemExit
        new_vs.append(ns)
      elif isinstance(v,list) or isinstance(v,dict) or isinstance(v,tuple):
        process = containers.process_dict if isinstance(v,dict) else containers.process_list
        ns = process(v,depth=depth) if not c else process(v,depth=depth,c=True)
        nl = ["{",ns,"}"] if isinstance(v,dict) else ["[",ns,"]"]
        join_str = f"\n{' '*depth}"
        return join_str.join(nl)
        # ns = implies(sv,depth=depth) if not c else implies(sv,depth=depth,c=True)
        # new_vs.append('\n'+ns)
      else:
        with open('el239','a') as f:
          f.write(stackprinter.format())
          f.write(info(v))
        raise SystemExit
    elif isinstance(v,CallPrinter):
      new_vs.append(repr(v))
    elif hasattr(v,'__name__'):
      new_vs.append(v.__name__)
    else:
      with open('el231','a') as f:
        f.write(stackprinter.format())
      raise SystemExit
  return "\n".join(new_vs)

def open_shelf():
  pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle/eventpickle_hex")
  data = []
  with shelve.open(str(pklpth)) as s:
    evt_dcts = s['evt_dcts']
    # evt_dcts = s['evt_dcts']
  lsts = [e for e in evt_dcts if isinstance(e,list)]
  dcts = [e for e in evt_dcts if isinstance(e,dict)]
  dks = [list(itm.keys()) for itm in dcts]
  dvs = [list(itm.values()) for itm in dcts]
  strs = [e for e in evt_dcts if isinstance(e,str)]
  pds = prcsd_dcts = process_dcts(dcts,c=True)
  def p(pds):
    for elm in pds:
      for k,v in elm.items():
        print(f"{k}: {v}")
  p(pds)

if __name__ == "__main__":
  pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/eventpickle/eventpickle_hex")
  suppth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/eventpickle/eventpickle_supp_hex")
  serialized_files = []
  for fp in (pklpth,suppth):
    with open(fp,'r') as f:
      serialized_files.append(f.readlines())
  argvars, evtinfos = serialized_files
  avs_fromhex = [bytes.fromhex(elm) for elm in argvars]
  eis_fromhex = [bytes.fromhex(elm) for elm in evtinfos]

  def load_pkld_line(ln):
    try:
      ldd = pickle.loads(ln)
      if isinstance(ldd,list):
        ldd = ["" if elm is None else elm for elm in ldd]
      return ldd
    except:
      return "error"

  def load_type_or_none(t):
    try:
      return pickle.loads(t)
    except:
      return t

  avs_unpkld = []
  for elm in avs_fromhex:
    tup = unpkld_tup = pickle.loads(elm)
    avs_unpkld.append({'arg_h_idx':tup[0],'arg_type':load_type_or_none(tup[1]),'arg_obj':load_pkld_line(tup[2])})

  eis_unpkld = [pickle.loads(elm)._asdict() for elm in eis_fromhex]
  eis_unpkld = []
  for elm in eis_fromhex:
    supp_field_tup = pickle.loads(elm)
    supp_field_dct = supp_field_tup._asdict()
    d = {}
    for k,v in supp_field_dct.items():
      if v.mono == v.poly:
        d.update({f"{k}":f"{v.mono}"})
      else:
        d.update({f"{k}_mono":f"{v.mono}"})
        d.update({f"{k}_poly":f"{v.poly}"})
    eis_unpkld.append(d)

  merged = [dict(**d1,**d2) for d1,d2 in zip(avs_unpkld,eis_unpkld)]
  df = pd.DataFrame(merged)
  df['df_idx'] = df.index

  df2 = df[[
    "df_idx","arg_h_idx","h_idx","arg_obj","arg_type",
    "filename_prefix_mono","filename_prefix_poly",
    "event_kind_mono","event_kind_poly",
    "indent_len",
    "event_symbol_mono","event_symbol_poly",
    "event_function","event_source"
  ]]

  with open("df.txt","w") as dfout:
    write_cols = [
      "df_idx","arg_h_idx","h_idx","arg_obj","arg_type",
      "filename_prefix_mono",
      "event_kind_mono",
      "indent_len",
      "event_symbol_mono",
      "event_function",
      "event_source"
    ]
    df2.to_string(dfout,columns=write_cols)

  df3 = df2[~df2.arg_obj.isnull()].copy()
  df3.reset_index(drop=True,inplace=True)
  df3['df_idx'] = df3.index
  join_to_write_list,test = [],[]
  for tup in df3.itertuples():
    arg_obj = tup.arg_obj
    arg_type = tup.arg_type
    idt_len = tup.indent_len
    evt_fnc = tup.event_function
    fmtd = pformat(arg_obj)
    fmtdec = codecs.decode(fmtd,'unicode_escape')
    # l:list = tw.wrap(text)
    # s:str = tw.fill(text)
    test.append(fmtdec)
    join_to_write_list.append((
      f"evt_fnc: {evt_fnc}\n"
      f"arg_type: {arg_type}, idt_len: {idt_len}\n"
      f"arg_obj:\n{arg_obj}\n"
      f"{'----'*20}\n"
      f"{evt_fnc}" + "(" + fmtd + ")\n"
      f"{'----'*20}\n"
      f"{'*~*~'*20}\n"
    ))
  with open('arg_objs.txt','w') as f:
    f.write("".join(join_to_write_list))
  with open('test','w') as f:
    f.write("".join(test))

"""
 style: string
        'plaintext' (default): Output just text
        'darkbg', 'darkbg2', 'darkbg3', 'lightbg', 'lightbg2', 'lightbg3':
            Enable colors, for use in terminals that support 256 ansi
            colors or in jupyter notebooks (or even with `ansi2html`)
    source_lines: int or 'all'
        Select how much source code context will be shown.
        int 0: Don't include a source listing.
        int n > 0: Show n lines of code. (default: 5)
        string 'all': Show the whole scope of the frame.
    show_signature: bool (default True)
        Always include the function header in the source code listing.
    show_vals: str or None
        Select which variable values will be shown.
        'line': Show only the variables on the highlighted line.
        'like_source' (default): Show only those visible in the source listing
        'all': Show every variable in the scope of the frame.
        None: Don't show any variable values.
    truncate_vals: int
        Maximum number of characters to be used for each variable value.
        Default: 500
    suppressed_paths: list of regex patterns
        Set less verbose formatting for frames whose code lives in certain paths
        (e.g. library code). Files whose path matches any of the given regex
        patterns will be considered boring. The first call to boring code is
        rendered with fewer code lines (but with argument values still visible),
        while deeper calls within boring code get a single line and no variable
        values.
        Example: To hide numpy internals from the traceback, set
        `suppressed_paths=[r"lib/python.*/site-packages/numpy"]`
"""
