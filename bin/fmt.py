# // vscode-fold=5
import sys
import re
from toolz.functoolz import compose_left, juxt
from functools import partial
from types import SimpleNamespace
from pathlib import Path
from fsplit.filesplit import FileSplit
import codecs
from bs4 import BeautifulSoup as Beaup
from pdb import set_trace as st
from typing import Dict, List, Any, Iterable, Tuple, Union
import fmtutil.readfile as fur
import fmtutil.dataframe as fud
import fmtutil.exception as fue
import fmtutil.constants as fuc
import fmtutil.utils as fu
import fmtutil.public_goods as fpgs
from fmtutil.row.process_row import process_row
from fmtutil.row.parse_verbose_argvars import pargvars, parse_argvars
from itertools import chain, repeat
import pysnooper
from math import floor
import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import OrderedDict, deque, UserString
from operator import methodcaller
from pprint import pprint as pp
import pdir
import argparse
from functools import partial
from textwrap import TextWrapper
from youtube_dl.hunterconfig import QueryConfig
from IPython.display import display, HTML
from fmtutil.row.classes import (
  SimpleFunkWithArgs, VerboseList,
  ParsedTuple, LineEvent,
  ParsedHTML, ParsedJSON,
  FormatSymbols, MutableStr,
  DataCollections
  )
from dataclasses import dataclass
import stackprinter
import dill as pickle
from enum import Enum
stackprinter.set_excepthook(style='lightbg2')
basepath = Path('/Users/alberthan/VSCodeProjects/vytd')
args_line_idx_len = 76
fmt_syms = FormatSymbols()
trunc_start,trunc_end = 0, 15

@dataclass
class HeaderRow:
  header: Union[str,None]
  row: tuple

  def __iter__(self):
    idr = iter([self.header,self.row])
    yield next(idr)

  def __len__(self):
    if self.header and self.row:
      return 2
    elif self.header or self.row:
      return 1
    else:
      return 0

class EventPicklesUtil:

  def __init__(self):
    self.homepath = basepath.joinpath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl')
    self.event_pickles: List = self.load_event_pickles()
    self.init_header_stack = deque()  # append/pop, raises on empty pop IndexError
    self.ydl_header_stack = deque()
    self.line_header_stack = deque()
    self.init_header_switch = True
    self.ydl_header_switch = True
    self.line_header_switch = True

  def load_event_pickles(self):
    pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle/evtdcts_pklpth.pkl")
    data = []
    with open(pklpth, 'rb') as fr:
      try:
        while True:
          data.append(pickle.load(fr))
      except EOFError:
        pass
    assert len(data) > 1, len(data)
    return data

  def make_datafarme_from_evts(self):
    es = self.event_pickles
    epdf = pd.DataFrame(es)
    return epdf

  def tier_test(self, pth, pth2):
    """..returns: self.headers_for_<tier> if tier else None"""
    pth,pth2 = Path(pth).stem,Path(pth2).stem
    if "__init__" in pth or "__init__" in pth2:
      return self.headers_for_init
    elif "YoutubeDL" in pth or "YoutubeDL" in pth2:
      return self.headers_for_ydl
    else:
      return None

  def header_switch_test(self):
    if self.init_header_switch:
      self.init_header_switch = False
      return self.init_header_stack
    elif self.ydl_header_switch:
      self.ydl_header_switch = False
      return self.ydl_header_stack
    elif self.line_header_switch:
      self.line_header_switch = False
      return self.line_header_stack
    else:
      return None

  def headers_for_init(self, row, row2):
    idx,pth,lno,evt,mos,pos,raw,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,raw2,ogi2 = row2
    pth,pth2 = Path(pth).stem,Path(pth2).stem
    t1=fmt_syms.get_tier1()
    if self.init_header_switch:
      self.init_header_switch = False
      header = MutableStr(f"{t1} {ogi+1}-")
      self.init_header_stack.append(header)
      return HeaderRow(row=row,header=header)
    elif "__init__" not in pth and "__init__" in pth2:
      # interp. pth2 will be a "first" of (possibly) adjacent init's.
      # therefore, pth2 will need a header, which will preceed it.
      # bc its pth2 that needs the header (not pth)
      # flip the switch for the next iteration (when pth2 => pth)
      self.init_header_switch = True
      # return [] # returning row causes header_row += row to convert pd.core.frame to list
    elif "__init__" in pth and "__init__" not in pth2:
      # interp. we are leaving the adjacent sequence of init's
      # update the header with the og_index, and pop from the stack
      if self.init_header_stack:
        header = self.init_header_stack.pop()
        header.modify_inplace(f"{ogi2}")
      else:
        with open('f148','w') as f:
          f.write(row)
          f.write(row2)
        raise SystemExit
    else:
      assert "__init__" in pth and "__init__" in pth2, f"{pth=}, {pth2=}"

  def headers_for_ydl(self, row, row2):
    idx,pth,lno,evt,mos,pos,raw,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,raw2,ogi2 = row2
    pth,pth2 = Path(pth).stem,Path(pth2).stem
    t2=fmt_syms.get_tier2()
    if self.ydl_header_switch:
      self.ydl_header_switch = False
      header = MutableStr(f"{t2} {ogi+1}-")
      self.ydl_header_stack.append(header)
      return HeaderRow(row=row,header=header)
    elif "YoutubeDL" not in pth and "YoutubeDL" in pth2:
      # interp. see headers_for_init
      self.ydl_header_switch = True
      # return [] # returning row causes header_row += row to convert pd.core.frame to list
    elif "YoutubeDL" in pth and "YoutubeDL" not in pth2:
      # interp. see headers_for_init
      if self.ydl_header_stack:
        header = self.ydl_header_stack.pop()
        header.modify_inplace(f"{ogi2}")
      else:
        with open('f173','w') as f:
          f.write(row)
          f.write(row2)
        raise SystemExit
    else:
      assert "YoutubeDL" in pth and "YoutubeDL" in pth2, f"{pth=}, {pth2=}"

  def headers_for_line_evts(self,row,row2):
    """Line Event"""
    idx,pth,lno,evt,mos,pos,raw,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,raw2,ogi2 = row2
    pth,pth2 = Path(pth).stem,Path(pth2).stem
    t3=fmt_syms.get_tier3()
    if "line" not in evt and "line" in evt2:
      header = MutableStr(f"{t3} {ogi}-")
      self.line_header_stack.append(header)
      self.line_header_switch = True
      return HeaderRow(header=header,row=row)
    elif "line" in evt and "line" not in evt2:
      if self.line_header_stack:
        header = self.line_header_stack.pop()
        m = re.search(r"\d+[-]$",str(header))
        og1 = m.group()[:-1]
        og2 = ogi2 - 1
        diff = int(og2) - int(og1)
        header.modify_inplace(f"{diff}")
        return [] # returning row causes header_row += row to convert pd.core.frame to list
      else:
        return []
    else:
      assert "line" in evt and "line" in evt2, f"{evt=}, {evt2=}"
      return []

def _evtpkls_main():
  util = EventPicklesUtil()

  def tmp_dbg_wrt(container):
    """this is for debugging.
    since i cannot use pdb during hunter's usage of trace,
    i can use this function to write/append to a file
    it takes an iterable container
    """
    cntr = container
    avsl,fmtm,fmtp,mlst,plst,rlst = [],[],[],[],[],[]
    for dct in cntr:
      if "__init__" in dct['filename']:
        evt = dct['hunter_event']
        avsl.append(evt.argvars)
        fmtdm,fmtdp = evt.fmtd_str(c=False),evt.fmtd_str(c=True)
        mono,poly,raw = dct['hunter_monostr'],dct['hunter_polystr'],dct['hunter_raw_output']
        fmtm.append(fmtdm)
        fmtp.append(fmtdp)
        mlst.append(mono)
        plst.append(poly)
        rlst.append(raw)
    dta = fm,fp,mj,pj,rj = ["\n".join(elm) for lst in [(fmtm,fmtp,mlst,plst,rlst)] for elm in lst]
    fnms = [f"dbg_{fnm}.log" for fnm in ("fmtm","fmtp","mlst","plst","rlst")]
    for n,d in zip(fnms,dta):
      with open(n,"w") as f:
        f.write(d)
    with open('dbg_avs.log','w') as f:
      f.write("\n".join([f"{i}: {str(elm)}" for i,elm in enumerate(avsl)]))

  def entry():
    query,actions,outputs,filenames,write_func,evtdcts_pklpth = qcfg = QueryConfig().eventpickle()
    # with open(evtdcts_pklpth,'rb') as f:
    #   evt_dcts = pickle.load(f)len(evt_
    #   tmp_dbg_wrt(evt_dcts)
    evt_dcts = util.load_event_pickles()
    st()
    # e381: Dict = evt_dcts[381]
    # hm1 = e381['hunter_monostr'][:200]
    # he1 = e381['hunter_event']
    # he1fs = e381['hunter_event'].fmtd_str()[:200]
    dc = DataCollections(evt_dcts)
    epdf, evts, evts_df = dc.evt_dcts_df, dc.evts, dc.evts_df
    # not working in epdf
    # df381 = epdf.iloc[381]
    # hm2 = df381.hunter_monostr[:200]
    epdf = epdf[:10000]  #!! RIGHT HERE = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =
    epdf2 = epdf.rename_axis('og_index').reset_index()
    columns = [
      'filename','lineno','kind',
      'hunter_monostr','hunter_polystr','hunter_raw_output', # these 2 replace dta
      'og_index',
    ]
    # # not working epdf3
    epdf3 = epdf2[columns]
    # ep381 = epdf3.iloc[381]
    # hm3 = ep381.hunter_monostr[:200]
    # # # not working in lwr
    lwr = lst_w_regions = add_regions(epdf3)
    # lwr191 = lwr[191][1].row
    # hm4 = lwr191.hunter_monostr[:200]
    # not working in lwr2
    lwr2 = [elm for lst in lwr for elm in lst if elm] # now, each elm is a HeaderRow w/ len=(1|2)
    wpath = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/lwr")
    lwr3 = write_file(df=epdf3,lst_w_regions=lwr2,writepath=wpath)
    # st()
    return lwr3

  def add_regions(epdf):
    prwi = False  # prwi: prev row was init
    output_lines = []
    itrlst = list(epdf.itertuples())
    i,end = 0,len(itrlst)
    while i < end:
      header_row_objs = []
      row,row2 = itrlst[i],(itrlst[i + 1] if i < (len(itrlst) - 1) else None)
      idx,pth,lno,evt,mos,pos,raw,ogi = row
      idx2,pth2,lno2,evt2,mos2,pos2,raw2,ogi2 = row2 if row2 else [""] * len(row)
      if record_func := util.tier_test(pth,pth2):
        if not row2:
          i += 1
          continue
        header_row_objs.append(record_func(row,row2))
      elif header_stack := util.header_switch_test():
        header = header_stack.pop()
        header_row_objs.append(HeaderRow(row=row, header=header))
        header_stack.append(header)
      if not any(header_row_objs):
        i += 1
        header_row_objs.append(HeaderRow(header=None,row=row))
      output_lines.append(header_row_objs)
      i += 1
    return output_lines

  sns = SimpleNamespace(entry=entry)
  return sns.entry
evtpkls_main = _evtpkls_main()

class FileWriterUtil:
  def __init__(self):
    self.cache = None
    self.return_monostr = []
    self.return_polystr = []
    self.first_line = True

  def _file_writer(self,string,path):
    dirname = path.parent
    dirname.mkdir(parents=True,exist_ok=True)
    plibpth = Path(path)
    filename = Path(path).name
    if plibpth.exists():
      plibpth.unlink()
    with open(path, 'w') as f:
      f.write(string)
    print(f'wrote to {path}')
    self._split_file(path)

  def _split_file(self,path):
    pth = path
    pth_dirname = pth.parent
    outdir = pth_dirname.joinpath(pth.stem)
    outdir.mkdir(parents=True,exist_ok=True)
    fs = FileSplit(file=pth, splitsize=1_100_000, output_dir=outdir)
    fs.split()

  def fix_init(self,elm):
    new_filepath = Path(elm.filename).stem
    assert new_filepath is not None, elm
    if "__init__" in new_filepath:
      parent_initial = Path(elm.filename).parent.stem[0]
      new_filepath = f"{parent_initial}{new_filepath}"
    if new_filepath is None: st()
    return new_filepath

  def fmt_lineno(self,lineno):
    return f"{lineno:>04}"

def _write_file():
  util = FileWriterUtil()

  def entry(df,lst_w_regions=None,writepath=None):
    iterlst = lst_w_regions
    util.cache = None
    return_monostr,return_polystr = iterate_thru_df(iterlst)
    m,p = "\n".join(return_monostr), "\n".join(return_polystr)
    if writepath:
      mpath = writepath.joinpath('fwr_m.log')
      ppath = writepath.joinpath('fwr_p.log')
      util._file_writer(m,mpath)
      util._file_writer(p,ppath)
      return m,p
    else:
      return m,p
    raise

  def iterate_thru_df(iterlst):
    """
    ..elm: len=(1|2), type=(HeaderRow)
    ..len:2 means there is a header and a row
    ..len:1 means there is a row only
    """
    for i,hr in enumerate(iterlst):
      # each elm is a HeaderRow w/ len=(1|2)
      prsdmono,prsdpoly = process_header_row(hr)
      util.return_monostr.append(prsdmono)
      util.return_polystr.append(prsdpoly)
    return util.return_monostr, util.return_polystr

  def process_header_row(hr):
    header,row = hr.header,hr.row
    if not header or header == "None":
      header = ""
    presyms = get_prefix_symbol_for_row(row)
    monostr,polystr = row.hunter_monostr,row.hunter_polystr
    monostr,polystr = monostr.strip(),polystr.strip() # hunterconfig:245 strip is opt
    tw=TextWrapper(width=120,
      tabsize=2,
      # initial_indent=presyms[0],
      subsequent_indent=presyms[1],
      drop_whitespace=False,
    )
    m = f"{header}\n{monostr}"
    p = f"{header}\n{polystr}"
    return m,p

  def get_prefix_symbol_for_row(row):
    symbols = set()
    knd_sym = {'call':fmt_syms.get_call(),
      'return':fmt_syms.get_return(),
      'exception':fmt_syms.get_exception(),
      'line':fmt_syms.get_line(first=util.first_line)}
    fnm_tier_sym = {'__init__' :(1,fmt_syms.get_tier1()),
                    'YoutubeDL':(2,fmt_syms.get_tier2())}
    idx,fnm,lno,knd,hms,hps,raw,ogi = row
    # tier is position 1
    idt,fs = fnm_tier_sym.get(Path(fnm).stem,(0,None))
    # fs = 1 if fs == "𝑡¹" else 2 if fs == "𝑡²" else 3
    ws = "\u0020"
    idt = ws * idt
    # kind is position 2
    ks = knd_sym.get(knd," ")
    util.first_line = False if knd == 'line' else True

    syms = initial_sym,subsequent_idt = f"{idt}{ks}",f"{idt}{len(ks)*ws}"
    return syms

  sns = SimpleNamespace(entry=entry)
  return sns.entry
write_file = _write_file()

if __name__ == "__main__":
  load_epdf = True

  if load_epdf:
    lwr = evtpkls_main()
    c,nc = lwr
