import io, re, sys
import string
import codecs
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
from collections import namedtuple, deque
from bs4 import BeautifulSoup as Beaup
from .parse_verbose_argvars import pargvars
from .classes import ParsedTuple, VerboseList, LineEvent, ParsedHTML, ParsedJSON

def _process_row():
  Index = None
  filepath = None
  line_number = None
  symbol = None
  event_kind = None
  call_data = None
  og_index = None
  snoop_data = None

  def entry(row):
    nonlocal filepath,line_number,symbol,event_kind,call_data,snoop_data
    if 'snoop_data' in row:
      filepath,line_number,symbol,event_kind,call_data,snoop_data = row
    else:
      filepath,line_number,event_kind,call_data,og_index = row
    fmtd_row:Tuple = compose_left(
        switchboard
    )()
    return fmtd_row

  def process_regular_args(indented_function,argvars):
    parse_argvars_ez = lambda s: map(str.strip,s.split('='))
    keys,vals = parsed = parse_argvars_ez(argvars)
    keylst,vallst = [keys],colorize_string(vals,e=True) # keep consistent with verbose
    fmtd_cell_data = FmtdCellData(f"{indent}{function}",keylst,vallst)
    return fmtd_cell_data

  def parse_verbose_list(s):
    s1 = s[1:-1]
    l1 = s1.split(',')
    return list(l1)

  def dispatch_to_json(datum):
    def step0(datum,rgx):
      """returns:idntd_func,argvars"""
      m = rgx.match(datum)
      gd = m.groupdict()
      indented_function, argvars = gd.values()
      return indented_function, argvars

    def step1(indented_function,rgxlhs):
      """returns: symbol, funk, rest"""
      m = rgxlhs.match(indented_function)
      gd = m.groupdict()
      ws,symbol,funk = gd.values()
      return f"{ws}{symbol}", funk

    def step2(argvars,rgxrhs):
      """returns: argdct"""
      # try processing json 1st to allow for variable # args
      lhs,rhs = splt = argvars.split("json_string=")
      jsnstr,rest_dct = trim_jsnstr(rhs)
      assert len(lhs.split("=")) == 2, lhs.split("=") # assume only one arg
      # argdct_argname_1, argdct_argvalue_1
      adan1,_adav1 = lhs.split("=")
      adav1 = _adav1.strip().replace(",","")
      adan2,adav2 = "json_string",_rhs_json(jsnstr)
      d = {
        adan1:adav1,
        adan2:adav2,
        **rest_dct
      }
      return d

    def trim_jsnstr(rhs):
      rhs = codecs.decode(rhs, 'unicode-escape')
      stack = deque()
      stack.append("{")
      ri,li = rhs.find("{"),0
      for i,char in enumerate(rhs[ri+1:]):
        if not stack:
          li = i
          break
        elif char == "{":
          stack.append("{")
        elif char == "}":
          stack.pop()
      jsnstr = rhs[ri:li+2]
      _rest = rhs[li+2:].split(",")
      rest = [elm.strip() for elm in _rest if "=" in elm]
      rest_dct = dict(elm.split("=") for elm in rest)
      return jsnstr,rest_dct

    def _rhs_json(rhs):
      txt2 = rhs
      def myreplacement(m):
          if m.group(1):
              return f'"{m.group(1)}"'
          else:
              return m.group(0)
      regex1 = re.compile(r'"true"|(true)')
      regex2 = re.compile(r'"false"|(false)')
      matches1 = [group for group in re.findall(regex1, txt2) if group]
      matches2 = [group for group in re.findall(regex2, txt2) if group]
      replaced1 = regex1.sub(myreplacement, txt2)
      replaced2 = regex2.sub(myreplacement, replaced1)
      rp2 = replaced2
      try:
        parsed_json_as_dct = eval(rp2)
      except:
        rp5 = rp2 + "}"
        parsed_json_as_dct = eval(rp5)
      return parsed_json_as_dct

    prsdjsn = ParsedJSON()
    if "=>" in datum:
      rgx = re.compile(r"(?P<indented_function>[^(]+)\((?P<argvars>.*)\)$",re.DOTALL)
      rgxlhs = re.compile(r"(?P<whitespace>\s+)(?P<symbol>=\>)\s(?P<funk>[A-z_][A-z0-9-_]*)$")
      rgxrhs = re.compile(r"(?P<argname>json_string)=(?P<rest>[^$]+)$")
    elif "return" in datum:
      if len(datum) < 200:
        return datum
    indented_function, argvars = step0(datum,rgx)
    symbol, funk = step1(indented_function, rgxlhs)
    argdct = step2(argvars,rgxrhs)
    prsdjsn.symbol,prsdjsn.funk,prsdjsn.argdct = symbol,funk,argdct
    parsed = prsdjsn
    return parsed

  def dispatch_to_html(datum):
    sd = codecs.decode(datum,'unicode-escape')
    if "=>" in datum:
      rgx = re.compile(r"(?P<indented_function>[^(]+)\((?P<argvars>.*)\)$",re.DOTALL)
      rgxvb = re.compile(r"(?P<whitespace>\s+)(?P<symbol>=\>)\s(?P<funk>[A-z_][A-z0-9-_]*)$")
    elif "<=" in datum:
      rgx = re.compile(r"(?P<indented_function>[^:]+): (?P<argvars>[^$]+)$",re.DOTALL)
      rgxvb = re.compile(r"(?P<whitespace>\s+)(?P<symbol>\<=)\s(?P<funk>[A-z_][A-z0-9-_]*)$")
    m = rgx.match(sd)
    gd = m.groupdict()
    indented_function,argvars = gd.values()
    m = rgxvb.match(indented_function)
    gd = m.groupdict()
    whitespace,symbol,funk = gd.values()
    content_type_block,webpage_bytes_block = argvars.split(",",1)
    content_type_lst,webpage_bytes_lst = content_type_block.split("=",1),webpage_bytes_block.split("=",1)
    content_type_dct,webpage_bytes_dct = dict([content_type_lst]),dict([webpage_bytes_lst])
    ctd,wbd = {k:Beaup(v,'lxml') for k,v in content_type_dct.items()},{k:Beaup(v,'lxml') for k,v in webpage_bytes_dct.items()}
    assert isinstance(next(iter(wbd.values())), Beaup), type(next(iter(wbd.values())))
    argvarsD = dict(**ctd,**wbd)
    prsdhtm = ParsedHTML()
    prsdhtm.symbol = f"{whitespace}{symbol}"
    prsdhtm.funk = funk
    prsdhtm.argdct = argvarsD
    parsed = prsdhtm
    return parsed
    try:
      bs = get_text_bs(argvars)
      print(f"{bs=}")
      st()
    except Exception as exc:
      import stackprinter as sp
      tb = sp.format(exc)
      st()
    raise SystemExit

  def dispatch_to_call(datum):

    rgx = re.compile(r"(?P<indented_function>[^(]+)(?P<sep>\s?)(?P<argvars>[^$]+)$",re.DOTALL)
    m = rgx.match(datum)
    gd = m.groupdict()
    indented_funcname, sep, argvars = gd.values()
    argvars2 = argvars
    isverbose = len(argvars2) > 80
    if isverbose:
      rgxvb = re.compile(r"(?P<whitespace>\s+)(?P<symbol>=\>)\s(?P<funk>[<]?[A-z_][A-z0-9-_]*[>]?)$")
      m = rgxvb.match(indented_funcname)
      gd = m.groupdict()
      whitespace,symbol,funk = gd.values()
      prsdtpl = ParsedTuple()
      prsdtpl.symbol = f"{whitespace}{symbol}"
      prsdtpl.funk = funk
      parsed = pargvars(argvars2,prsdtpl=prsdtpl,first=True)
    else:
      parsed = (indented_funcname,argvars2)
    return parsed

  def dispatch_to_simpfunk(datum):
    pass

  def dispatch_to_return(datum):
    rgx = re.compile(r"(?P<indented_function>[^:]+)(?P<sep>:\s?)(?P<argvars>[^$]+)$",re.DOTALL)
    m = rgx.match(datum)
    gd = m.groupdict()
    indented_funcname, sep, retvals = gd.values()
    isverbose = len(retvals) > 2000
    if isverbose:
      parsed = VerboseList((indented_funcname, parse_verbose_list(retvals)))
    else:
      parsed = (indented_funcname, retvals)
    return parsed

  def dispatch_to_line(datum):
    lnevt = LineEvent(line_nc=datum)
    return lnevt

  def dispatch_to_exception(datum):
    rgx = re.compile(r"(?P<indented_function>[^:]+)(?P<sep>:\s?)(?P<argvars>[^$]+)$",re.DOTALL)
    m = rgx.match(datum)
    gd = m.groupdict()
    indented_funcname, sep, argvars = gd.values()
    return (indented_funcname, argvars)

  def make_eval_able(call_datum):
    """called at the beginning of the switch board to clean the data upfront"""
    # (?P<ws>\s*)(?P<sym>=>|<=) (?P<argname>[<]?[A-z_][A-z0-9_]*[>]?)
    if call_datum is None:
      return None
    rgx1 = re.compile(r"(?P<indented_function>[^(]+)(?P<sep>\s?)(?P<argvars>[^$]+)$",re.DOTALL)
    rgx2 = re.compile(r"(?P<indented_function>[^:]+)(?P<sep>:\s?)(?P<argvars>[^$]+)$",re.DOTALL)
    m1 = rgx1.match(call_datum)
    m2 = rgx2.match(call_datum)
    gd = m1.groupdict() if m1 else m2.groupdict()
    indented_funcname, sep, argvars = gd.values()
    dat1 = re.sub(
      r"(?P<left>^[^<]+)(?P<unquoted><[^>]+>)(?P<right>.+)$",
      r"\g<left>'\g<unquoted>'\g<right>",
      argvars
    )
    dat2 = dat1.replace("<listcomp>","<lstcmp>")
    dat3 = dat2.replace("list_iterator","lst_itrtr")
    cleaned_call_datum = f"{indented_funcname}{sep}{argvars}"
    return cleaned_call_datum

  def switchboard():
    # assert isinstance(call_data,str), call_data
    assert isinstance(call_data,list), call_data
    call_datum = call_data[0]
    cleaned_call_datum = make_eval_able(call_datum)
    if cleaned_call_datum is None:
      return None
    print(cleaned_call_datum)
    print(f"none in call{'None' in cleaned_call_datum}")
    print(f"{cleaned_call_datum.strip()=}")
    print(f"{cleaned_call_datum.strip().startswith('=>')=}")
    if "<!DOCTYPE html>" in cleaned_call_datum:
      print(1)
      fmtd_cell_data = dispatch_to_html(cleaned_call_datum)
    elif "json_string" in cleaned_call_datum:
      print(2)
      fmtd_cell_data = dispatch_to_json(cleaned_call_datum)
    elif cleaned_call_datum.strip().startswith('=>'):
      print(4)
      #      call: '{COLOR}=>{NORMAL} {}({}{COLOR}{NORMAL}){RESET}\n'
      fmtd_cell_data = dispatch_to_call(cleaned_call_datum)
    elif cleaned_call_datum.strip().startswith('<='):
      print(5)
      #    return: '{COLOR}<={NORMAL} {}: {RESET}{}\n',
      fmtd_cell_data = dispatch_to_return(cleaned_call_datum)
    elif cleaned_call_datum.strip().startswith('!'):
      print(6)
      # exception: '{COLOR} !{NORMAL} {}: {RESET}{}\n',
      fmtd_cell_data = dispatch_to_exception(cleaned_call_datum)
    elif "None" in cleaned_call_datum and not any([(sym in cleaned_call_datum) for sym in bracket_syms]):
      print(3)
      fmtd_cell_data = dispatch_to_line(cleaned_call_datum)
    else:
      print(7)
      # line
      fmtd_cell_data = dispatch_to_line(cleaned_call_datum)
    return fmtd_cell_data

  sns = SimpleNamespace(entry=entry)
  return sns.entry
process_row = _process_row()

if __name__ == "__main__":
  idf = pd.read_pickle('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/tfdf/idf.pkl')
  fmt(idf)
