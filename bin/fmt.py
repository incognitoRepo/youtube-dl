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
from typing import Dict, List, Any, Iterable, Tuple
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
from youtube_dl.hunterconfig import QueryConfig
from IPython.display import display, HTML
from fmtutil.row.classes import (
  SimpleFunkWithArgs, VerboseList,
  ParsedTuple, LineEvent,
  ParsedHTML, ParsedJSON,
  FormatSymbols, MutableStr
  )
import stackprinter
import dill as pickle
from enum import Enum
stackprinter.set_excepthook(style='darkbg2')
basepath = Path('/Users/alberthan/VSCodeProjects/vytd')
args_line_idx_len = 76
fmt_syms = FormatSymbols()
DEBUG = True
break_point = 13
break_points = [38,39,40]
TRUNC = True
trunc_start,trunc_end = 0, 15

def load_event_pickles():
  pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/evts.pkl")
  with open(pklpth,'rb') as f:
    eps = event_pickles = pickle.load(f)
  return eps
eps = load_event_pickles()
e0,e1 = eps[0],eps[1]

def decompose_hunter_string(hs):
  rgx_cll = r""
  rgx_ret = r""
  rgx_exc = r""
  rgx_lne = r""

class EventPicklesUtil:

  def __init__(self):
    self.event_pickles: List = load_event_pickles()

  def load_event_pickles(self):
    pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/evts.pkl")
    with open(pklpth,'rb') as f:
      self.event_pickles = pickle.load(f)
    assert len(self.event_pickles) > 1, self.event_pickles

  def make_datafarme_from_evts(self):
    es = self.event_pickles
    epdf = pd.DataFrame(es)
    return epdf

  def get_filetexts(self):
    self.lst_o_init_filetexts = [pth.read_text() for pth in self.lst_o_init_filepaths]
    self.loif1 = [elm.split('\n') for elm in self.lst_o_init_filetexts]
    self.loif2 = [len(elm) for elm in self.loif1]  # [62, 47, 41, 486]
    return self.loif1

  def get_text_bs(self,html):
    tree = Beaup(html, 'lxml')
    body = tree.body
    if body is None:
      return None
    for tag in body.select('script'):
      tag.decompose()
    for tag in body.select('style'):
      tag.decompose()
    text = body.get_text(separator='\n')
    return text

  def headers_for_ydl(self,row):
    indent = "  "
    idx,pth,lno,evt,dta,ogi = row
    rgx = re.compile(r"(?P<funcname>[\<A-z][A-z0-9_\>]*)(?P<rest>.*)")
    t1,t2,t3 = fmt_syms.get_Tier2()
    if evt == "call":
      sym,cod = dta.split(" ",1)
      assert sym == "=>", sym
      m = rgx.match(cod)
      gd = m.groupdict()
      header = MutableStr(f"{t1}#region2 {ogi}-")
      self.ydl_header_stack.append(header)
      return [row,header]
    elif evt == "return":
      sym,cod = dta.split(" ",1)
      assert sym == "<=", sym
      m = rgx.match(cod)
      gd = m.groupdict()
      header = self.ydl_header_stack.pop()
      header.modify_inplace(f"{ogi}")
      endheader = MutableStr(f"{t1}#endregion2")
      return [endheader,row]
    else:
      return []

  def record_all_inits(self, row, row2):
    idx,pth,lno,evt,dta,ogi = row
    idx2,pth2,lno2,evt2,dta2,ogi2 = row2
    t1,t2,t3 = fmt_syms.get_Tier1()
    if "__init__" in pth and "__init__" not in pth2:
      header = MutableStr(f"{t1} #region1 {ogi+1}")
      self.init_header_stack.append(header)
      self.init_header_switch = True
      return [] # returning row causes header_row += row to convert pd.core.frame to list
    elif "__init__" not in pth and "__init__" in pth2:
      if self.init_header_stack:
        self.init_endheader_switch = True
        header = self.init_header_stack.pop()
        header.modify_inplace(f"-{ogi2}")
        m = re.search(r"\d+[-]\d+", str(header))
        og_nums = m.group()
        endheader = MutableStr(f"{t1} #endregion1 {og_nums}")
        return [row,endheader]
      else:
        return []
    else:
      assert "__init__" in pth and "__init__" in pth2, f"{pth=}, {pth2=}"
      return []

  def headers_for_line_evts(self,row,row2):
    """Line Event"""
    idx,pth,lno,evt,dta,ogi = row
    idx2,pth2,lno2,evt2,dta2,ogi2 = row2
    if "line" not in evt and "line" in evt2:
      le1,le2,le3 = fmt_syms.get_LE()
      header = MutableStr(f"{le1} {ogi}-")
      self.line_header_stack.append(header)
      self.line_header_switch = True
      return [row,header]
    elif "line" in evt and "line" not in evt2:
      if self.line_header_stack:
        header = self.line_header_stack.pop()
        m = re.search(r"\d+[-]$",str(header))
        og1 = m.group()[:-1]
        og2 = ogi2 - 1
        diff = int(og2) - int(og1)
        header.modify_inplace(f"{og2}({diff})")
        return [] # returning row causes header_row += row to convert pd.core.frame to list
      else:
        return []
    else:
      assert "line" in evt and "line" in evt2, f"{evt=}, {evt2=}"
      return []

def _evtpkls_main():
  util = EventPicklesUtil()

  def entry():
    query,actions,outputs,filenames,write_func,epdf_pklpth = qcfg = QueryConfig().eventpickle()
    dfs = {}
    if not epdf_pklpth.exists():
      epdf = util.make_datafarme_from_evts()
      epdf.to_pickle(epdf_pklpth)
    else:
      epdf = pd.read_pickle(epdf_pklpth)
    fcdf = fcdf[:30]  #!! RIGHT HERE
    # if TRUNC: fcdf = fcdf[trunc_start:trunc_end]
    columns = ["filepath","line_number","event_kind","call_data","og_index"]
    fcdf_agg = fud.aggregate_aggdfs([fcdf],columns=columns)
    cds = call_data_series = fcdf_agg.apply(process_row,axis=1)
    cdl = call_data_lst = [SimpleFunkWithArgs(cd)
                           if not (
        isinstance(cd,LineEvent)
        or isinstance(cd,VerboseList)
        or isinstance(cd,ParsedHTML)
        or isinstance(cd,ParsedJSON)
        or isinstance(cd[0], ParsedTuple)
    )
        else cd for cd in call_data_series]
    fcdf_agg.call_data = call_data_lst
    lwr = lst_w_regions = add_regions(fcdf_agg)
    lwr_df = pd.DataFrame(lwr)
    wpath = util.homepath.joinpath('bin/lwr')
    lwr2 = write_file(df=fcdf_agg,lst_w_regions=lwr,writepath=wpath)
    return lwr2

  def add_regions(fcdf):
    prwi = False  # prwi: prev row was init
    output_lines = []
    itrlst = list(fcdf.itertuples())
    i,end = 0,len(itrlst)
    while i < end:
      # print(f"{i=}")
      header_row = []
      # print(f"11. {header_row=}\n---")
      row,row2 = itrlst[i],(itrlst[i + 1] if i < (len(itrlst) - 1) else None)
      # print(f"{row=}\n{row2=}\n")
      idx,pth,lno,evt,dta,ogi = row
      idx2,pth2,lno2,evt2,dta2,ogi2 = row2 if row2 else [""] * len(row)
      if "__init__" in pth or "__init__" in pth2:
        if not row2:
          i += 1
          continue
        header_row += util.record_all_inits(row,row2)
        # print(f"1 {header_row=}\n---")
      elif util.init_header_switch:
        util.init_header_switch = False
        header = util.init_header_stack.pop()
        header_row += [row, header]
        # print(f"2 {header_row=}\n---")
        util.init_header_stack.append(header)
      # elif util.init_endheader_switch:
      #   util.init_endheader_switch = False
      #   header = util.init_header_stack.pop()
      #   header_row += [row, header]
        print(f"2 {header_row=}\n---")
      #   util.init_header_stack.append(header)
      elif "YoutubeDL" in pth:
        header_row += util.headers_for_ydl(row)
        # print(f"3 {header_row=}\n---")
      if "line" in evt or "line" in evt2:
        if not row2:
          i += 1
          continue
        retvals = util.headers_for_line_evts(row,row2)
        # print(f"abc {header_row=}\n---")
        if retvals:
          # print(f"{retvals=}")
          retrow,rethead = retvals
          if len(header_row) > 1:
            header_row += [rethead]
            # print(f"4 {header_row=}\n---")
          else:
            header_row += [retrow,rethead]
            # print(f"5 {header_row=}\n---")
      if header_row:
        output_lines.append(header_row)
        # print(f"87. {header_row=}\n---")
        header_row = []
        i += 1
      else:
        output_lines.append(row)
        i += 1
        # print(f"{row=}\n---")
    return output_lines

  sns = SimpleNamespace(entry=entry)
  return sns.entry
evtpkls_main = _evtpkls_main()

class FileWriterUtil:
  def __init__(self):
    self.cache = None
    self.initfiles = self.load_init_files()
    self.rsc = []
    self.rsnc = []

  def load_init_files(self):
    with open("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/extractor/__init__.py", "r") as f:
      extr = f.readlines()  # len: 46
    with open("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/downloader/__init__.py", "r") as f:
      down = f.readlines()  # len: 61
    with open("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/postprocessor/__init__.py", "r") as f:
      post = f.readlines()  # len: 40
    with open("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/youtube_dl/__init__.py", "r") as f:
      ytdl = f.readlines()  # len: 485
    return [extr,down,post,ytdl]

  def _file_writer(self,string,path):
    dirname = path.parent
    dirname.mkdir(parents=True,exist_ok=True)
    filename = Path(path).name
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

  def remove_color(self,s):
    s1 = re.sub(r"\x1b\[0m", "", s)
    s2 = re.sub(r"\x1b\[\d;\d{2}m","",s1)
    s3 = re.sub(r"\x1b\[\d{2};\d;\d{3};\d{3};\d{3}m", "" ,s2)
    return s3

  def fix_init(self,elm):
    new_filepath = Path(elm.filepath).stem
    assert new_filepath is not None, elm
    if "__init__" in new_filepath:
      lno = int(elm.line_number)
      def trunc(f): return f[lno - 3:lno + 3]
      def func(e): return e.filepath
      e,d,p,y = trnctd_fls = [trunc(f) for f in self.initfiles]
      try:
        if lno > 61:
          new_filepath = "__init__"
        elif e and any([func(elm) in itm for itm in e]):
          new_filepath = "e.__init__"
        elif d and any([func(elm) in itm for itm in d]):
          new_filepath = "d.__init__"
        elif p and any([func(elm) in itm for itm in p]):
          new_filepath = "p.__init__"
        elif y and any([func(elm) in itm for itm in y]):
          new_filepath = "__init__"
      except Exception as exc:
        tb = stackprinter.format(exc)
        print('The front fell off.' + tb)
        st()
    if new_filepath is None: st()
    return new_filepath

  def fmt_lineno(self,lineno):
    return f"{lineno:>04}"

  def fmt_filename(self,filename,width=6):
    return f"{filename:<{width}}"

  def filter3(self,df):
    df2 = df[['filepath','line_number','call_data']]
    return df2

  def args_prefix(self):
    cyn = 36
    pirate_c = f"\x1b[1;{cyn}m\x1b[3;{cyn}mArrr️\x1b[0m\x1b[2;{cyn}mgs\x1b[0m  "
    pirate_nc = f"Arrr️gs  "
    return pirate_c,pirate_nc

  def get_fillchars(self,sym_func,fcfg=None):
    if not fcfg:
      fcfg = {"flen":80,"fchr":"~ "}
    flen,fchr = fcfg.values()
    fillcharsneeded = (flen - len(sym_func)) / len(fchr)
    no_extra_space,fillcharsneeded = fillcharsneeded.is_integer(),floor(fillcharsneeded)
    fillchar = fchr
    fillchars = f"{fillchar*fillcharsneeded}"
    if not no_extra_space:
      fillchars = f" {fillchars}"
    return fillchars

  def filename_fileno(self,filename,fileno,fn_width=6):
    """the filename:fileno at the end of the line
    filename can be a filestem or fileletter
    fileno can be fileno or og_index"""
    name = f"{self.fmt_filename(filename,width=fn_width)}"
    numb = f":{self.fmt_lineno(fileno)}"
    return f"{name}{numb}"

  def filename_fileno2(self,filename,fileno,fn_width=6):
    """the filename:fileno at the end of the line
    filename can be a filestem or fileletter
    fileno can be fileno or og_index"""
    filename = filename.replace("__init__","init")
    rgx = re.compile(r"[^_]")
    filestem = Path(filename).stem
    if fn_width == 1:
      m = rgx.search(filestem)
      filename = m.group(0)
    else:
      filename = Path(filename).stem
    name = f"{self.fmt_filename(filename,width=fn_width)}"
    numb = f":{self.fmt_lineno(fileno)}"
    if str(fileno) == '2837': st()
    return f"{name}{numb}"

  def fmt_first_args_line(self,line,fcfg=None):
    """i:0001
    refactor with def prsd_line"""
    filename_fileno = self.filename_fileno2(self.cache.filepath,self.cache.og_index,fn_width=1)
    fillchars = self.get_fillchars(line,fcfg)
    if len(fillchars) > 0:
      line = f"{line}{fillchars}{filename_fileno}"
    return line

  def fmt_argname_argvals(self,indent,arrow,name_vals,singleline=False):
    if not name_vals:
      return
    args_line = f'{indent} {arrow}' + name_vals
    if singleline:
      args_line_idx = self.fmt_first_args_line(args_line,fcfg={"flen":79,"fchr":" "})
    else:
      _row1,rest = args_line.split("\n",1)
      row1 = self.fmt_first_args_line(_row1,fcfg={"flen":79,"fchr":" "})
      args_line_idx = "\n".join([row1,rest])
    return args_line_idx

  def fmt_line_event(self,line,fcfg=None):
    blt1, = fmt_syms.get_BLTS()
    fillchars = self.get_fillchars(line,fcfg)
    if len(fillchars) > 0:
      line = f"{line}{fillchars}{blt1}{self.fmt_lineno(self.cache.og_index)}"
    return line

  def is_tier_level_elm(self,elm):
    tier_levels = ["__init__" in elm.filepath, "YoutubeDL" in elm.filepath]
    return tier_levels

def _write_file():
  util = FileWriterUtil()
  util.load_init_files()

  def entry(df,lst_w_regions=None,writepath=None,cdsl=None):
    iterlst = lst_w_regions if lst_w_regions else list(df.itertuples())
    util.cache = None
    return_strings_c,return_strings_nc = iterate_thru_df(iterlst)
    c,nc = "\n".join(return_strings_c), "\n".join(return_strings_nc)
    if writepath:
      cpath = writepath.joinpath('fwrc.log')
      ncpath = writepath.joinpath('fwrnc.log')
      util._file_writer(c,cpath)
      util._file_writer(nc,ncpath)
      return c,nc
    else:
      return c,nc
    raise

  def iterate_thru_df(iterlst):
    for i,elm in enumerate(iterlst):
      print(i, break_point)
      if DEBUG and i == break_point: st()
      if len(elm) == 3:
        e0,e1,e2 = elm
        if e0.__module__ == "pandas.core.frame":
          tier_lvls = [True,False]
          util.cache = elm[0]
          if "endregion" in str(elm[1]):
            (elmc,elmnc),h1,h2 = process_elm(elm[0]),str(elm[1]),str(elm[2])
            util.rsc += [elmc,h2]
            util.rsnc += [elmnc,h2]
          else:
            (elmc,elmnc),h1,h2 = tier_level_elm(elm[0],tier_lvls),str(elm[1]),str(elm[2])
            util.rsc += [elmc,h1,h2]
            util.rsnc += [elmnc,h1,h2]
        elif e1.__module__ == "pandas.core.frame":
          (elmc,elmnc),h1,h2 = process_elm(elm[1]),str(elm[0]),str(elm[2])
          util.rsc += [elmc,h1,h2]
          util.rsnc += [elmnc,h1,h2]
        elif e2.__module__ == "pandas.core.frame":
          (elmc,elmnc),h1,h2 = process_elm(elm[2]),str(elm[0]),str(elm[1])
          util.rsc += [elmc,h1,h2]
          util.rsnc += [elmnc,h1,h2]
        else:
          raise
      elif len(elm) == 2:
        util.rsc,util.rsnc = process_mutable_str(elm[0],elm[1])
      else:
        elm_rv = process_elm(elm)
        util.rsc.append(elm_rv[0])
        util.rsnc.append(elm_rv[1])
    return util.rsc, util.rsnc

  def process_mutable_str(elm0,elm1):
    le1,le2,le3 = fmt_syms.get_LE()
    if isinstance(elm1, MutableStr):
      if ("endregion1" in elm1) or (le1 in elm1):
        if DEBUG and elm0.og_index == break_point: st()
        util.cache = elm0
        if any(util.is_tier_level_elm(elm0)):
          tier_lvls = [True,False]
          (elmc,elmnc),header = tier_level_elm(elm0,tier_lvls),str(elm1)
          util.rsc += [elmc]
          util.rsnc += [elmnc]
          return util.rsc,util.rsnc
        else:
          (elmc,elmnc),header = process_elm(elm0),str(elm1)
          util.rsc += [elmc,header]
          util.rsnc += [elmnc,header]
          return util.rsc,util.rsnc
      elif ("region" in elm1) or (le1 in elm1):
        (elmc,elmnc),header = process_elm(elm0),str(elm1)
        util.rsc += [elmc,header]
        util.rsnc += [elmnc,header]
        return util.rsc,util.rsnc
    elif isinstance(elm0, MutableStr):
      # if ("endregion1" in elm0):
      #   tier_lvls = [True,False]
      #   util.cache = elm1
      #   (elmc,elmnc),header = tier_level_elm(elm1,tier_lvls),str(elm0)
      #   util.rsc += [elmc]
      #   util.rsnc += [elmnc]
      if ("#region" in elm0) or (le1 in elm0):
        (elmc,elmnc),header = process_elm(elm1),str(elm0)
        util.rsc += [elmc,header]
        util.rsnc += [elmnc,header]
        return util.rsc,util.rsnc
    else:
        st()

  def tier_level_elm(elm,tier_levels):
    """tier_levels=[bool,bool]"""
    if elm.og_index in break_points: st()
    cd = elm.call_data
    t1,t2,t3 = fmt_syms.get_Tier1() if tier_levels[0] else fmt_syms.get_Tier2()
    tier = 1 if tier_levels[0] else 2
    if isinstance(cd,SimpleFunkWithArgs):
      return (
        simp_funk_w_args(elm,sym1=t1,sym2=t2,c=True),
        simp_funk_w_args(elm,sym1=t1,sym2=t2,c=False)
      )
    elif isinstance(cd,LineEvent):
      return (
        prsd_line(elm,le2=t2,c=True),
        prsd_line(elm,le2=t2,c=False)
      )
    elif isinstance(cd,ParsedHTML):
      t1,t2,t3 = fmt_syms.get_Tier(tier)
      return (
        prsd_html(elm,sym1=t1,sym2=t2,c=True),
        prsd_html(elm,sym1=t1,sym2=t2,c=False)
      )
    elif isinstance(cd,ParsedJSON):
      t1,t2,t3 = fmt_syms.get_Tier(tier)
      return (prsd_json(elm,sym1=t1,sym2=t2,c=True),
        prsd_json(elm,sym1=t1,sym2=t2,c=False)
      )
    elif isinstance(cd,VerboseList):
      return prsd_lst(elm,c=True,tier=tier),prsd_lst(elm,c=False,tier=tier)
    elif isinstance(cd[0],ParsedTuple):
      return prsd_tpl(elm,c=True,tier=tier),prsd_tpl(elm,c=False,tier=tier)
    else:
      raise

  def process_elm(elm):
    if DEBUG and elm.og_index == break_point: st()
    util.cache = elm
    if "call" in elm.event_kind:
      prefixsymbol = fmt_syms.get_call()
    elif "return" in elm.event_kind:
      prefixsymbol = fmt_syms.get_return()
    else:
      prefixsymbol = ""
    presym = prefixsymbol
    if ("line" not in elm.event_kind):
      elm = elm._replace(filepath=util.fix_init(elm))
    cd = elm.call_data
    if any(util.is_tier_level_elm(elm)):
      tier_levels = util.is_tier_level_elm(elm)
      c,nc = tier_level_elm(elm, tier_levels)
      return c,nc
    elif isinstance(elm, UserString):
      us1,us2,us3 = uss = fmt_syms.get_US(presym)
      c,nc = f'{us}' + str(elm),f'{us}' + str(elm)
      return c,nc
    elif isinstance(cd, SimpleFunkWithArgs):
      sfwa1,sfwa2,sfwa3 = sfwas = fmt_syms.get_SFWA(presym)
      c = simp_funk_w_args(elm,sym1=sfwa1,sym2=sfwa2,c=True),
      nc =  simp_funk_w_args(elm,sym1=sfwa1,sym2=sfwa2,c=False)
      # print(c);print(nc)
      # st()
      return c,nc
    elif isinstance(cd,LineEvent):
      lec,lenc = prsd_line(elm,c=True),prsd_line(elm,c=False)
      return lec,lenc
    elif isinstance(cd,ParsedHTML):
      ph1,ph2,ph3 = phs = fmt_syms.get_PH(presym)
      return (
        prsd_html(elm,sym1=ph1,sym2=ph2,c=True),
        prsd_html(elm,sym1=ph1,sym2=ph2,c=False)
      )
    elif isinstance(cd,ParsedJSON):
      pj1,pj2,pj3 = pjs = fmt_syms.get_PJ(presym)
      return (prsd_json(elm,sym1=pj1,sym2=pj2,c=True),
        prsd_json(elm,sym1=pj1,sym2=pj2,c=False)
      )
    elif isinstance(cd,VerboseList):
      return prsd_lst(elm,c=True),prsd_lst(elm,c=False)
    elif isinstance(cd[0],ParsedTuple):
      return prsd_tpl(elm,c=True),prsd_tpl(elm,c=False)
    else:
      return prsd_else(elm,c=True),prsd_else(elm,c=False)

  def prsd_line(elm,le2=None,c=False):
    """Line Event"""
    header = ""
    cd = elm.call_data
    if not le2:
      le1,le2,le3 = fmt_syms.get_LE()
    if c:
      line = f"{le2}{str(cd.line_c)}"
      filestem = Path(elm.filepath).stem
      fileletter = filestem[0] if not "init" in filestem else "i"
      filename_fileno = util.filename_fileno(fileletter,elm.og_index,fn_width=1)
    else:
      line = f"{le2}{str(cd.line_nc)}"
      filestem = Path(elm.filepath).stem
      fileletter = filestem[0] if not "init" in filestem else "i"
      filename_fileno = util.filename_fileno(fileletter,elm.og_index,fn_width=1)
    fillchars = util.get_fillchars(line)
    elm_as_str = line + fillchars + filename_fileno
    return elm_as_str

  def structure1(elm,sym1,sym2,c=False):  # !! TODO: maybe have a method to return the length of nc sym_func in the class
    """SimpleFunkWithArgs"""
    cd = elm.call_data
    blt1, = fmt_syms.get_BLTS()
    arr1,_,_ = fmt_syms.get_Arrows()
    m = re.match(r"\s*",cd.get_funcname())
    idt = m.group(0)
    _argname_argvals = cd.get_args()
    if not _argname_argvals:
      sym_func_c = f"{cd.get_funcname(c=True)}"
      sym_func_nc = f"{cd.get_funcname(c=False)}"
      if c:
        sym_func = sym_func_c
        filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number)
      else:
        sym_func = sym_func_nc
        filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number)
      fillchars = util.get_fillchars(sym_func_nc,fcfg={"flen":79,"fchr":"-"})
      elm_as_str = f'{sym1}' + sym_func + fillchars + filename_fileno
    else:
      sym_func_c = f"{cd.get_funcname(c=True)}"
      sym_func_nc = f"{cd.get_funcname(c=False)}"
      if c:
        sym_func = sym_func_c
        filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number) + "\n"
        argname_argvals = f"{cd.get_args(c=True)}"
        args_line_idx = util.fmt_argname_argvals(idt,arr1,argname_argvals,isinstance(cd.argval,str))
      else:
        sym_func = sym_func_nc
        filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number) + "\n"
        argname_argvals = f"{cd.get_args(c=False)}"
        # st()
        args_line_idx = util.fmt_argname_argvals(idt,arr1,argname_argvals,isinstance(cd.argval,str))
      fillchars = util.get_fillchars(sym_func_nc,fcfg={"flen":79,"fchr":"-"})
      elm_as_str = f'{sym1}' + sym_func + fillchars + filename_fileno + args_line_idx
    return elm_as_str

  def structure2(elm,sym1,sym2,c=False):
    """ParsedHTML, ParsedJSON"""
    cd = elm.call_data
    blt1, = fmt_syms.get_BLTS()
    _,arr2,_ = fmt_syms.get_Arrows()
    m = re.match(r"\s*",cd.get_funcname())
    idt = m.group(0)
    if c:
      sym_func = f"{cd.get_funcname(c=True)}"
      filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number) + "\n"
      argname_argvals = f"{cd.argdct.get_cstr()}"
      _row1,rest = argname_argvals.split("\n",1)
      row1 = util.fmt_first_args_line(_row1,fcfg={"flen":78,"fchr":" "})
      args_line = "\n".join([row1,rest])
      args_line_idx = f'{sym2}{idt} {arr2}' + args_line
    else:
      sym_func = f"{cd.get_funcname(c=False)}"
      filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number) + "\n"
      argname_argvals = f"{cd.argdct.get_str()}"
      _row1,rest = argname_argvals.split("\n",1)
      row1 = util.fmt_first_args_line(_row1,fcfg={"flen":78,"fchr":" "})
      args_line = "\n".join([row1,rest])
      args_line_idx = f'{sym2}{idt} {arr2}' + args_line
    fillchars = util.get_fillchars(sym_func)
    elm_as_str = f'{sym1}' + sym_func + fillchars + filename_fileno + args_line_idx
    return elm_as_str

  simp_funk_w_args = structure1
  prsd_html = structure2
  prsd_json = structure2

  def prsd_lst(elm,c=False,tier=0):
    """VerboseList"""
    if elm.og_index == 39: st()
    cd = elm.call_data
    m = re.match(r"\s*",cd.get_funcname())
    idt = m.group(0)
    if c:
      sym_func = f"{cd.symbol} {cd.funk}"
      filename_fileno = (
          f"{util.fmt_filename(elm.filepath)}"
          f":{util.fmt_lineno(elm.line_number)}\n"
      )
      filename_fileno = util.filename_fileno2(elm.filepath,elm.line_number) + "\n"
      argname_argvals = (
          f"{cd.get_args(c=True)}"
      )
    else:
      sym_func = f"{cd.symbol} {cd.funk}"
      filename_fileno = (
          f"{util.remove_color(util.fmt_filename(elm.filepath))}"
          f":{util.remove_color(util.fmt_lineno(elm.line_number))}\n"
      )
      argname_argvals = (
          f"{cd.get_args(c=False)}"
      )
    split_args = argname_argvals.split("\n")
    num_args = len(split_args)
    vl1,vl2 = fmt_syms.get_VL(nargs=num_args)
    argname_argvals = "\n".join([f"{next(vl2,None)}{idt}{line}" for line in argname_argvals.split("\n")])
    fillchars = util.get_fillchars(sym_func)
    elm_as_str = f'{vl1}' + sym_func + fillchars + filename_fileno + argname_argvals
    return elm_as_str

  def prsd_tpl(elm,c=False,tier=0):
    """ParsedTuple"""
    cd = elm.call_data[0]
    m = re.match(r"\s*",cd.get_funcname())
    idt = m.group(0)
    if c:
      sym_func = f"{cd.symbol} {cd.funk}"
      filename_fileno = (
          f"{util.fmt_filename(elm.filepath)}"
          f":{util.fmt_lineno(elm.line_number)}\n"
      )
      argname_argvals = (
          f"{cd.get_argname(c=True)}={cd.get_argdct(c=True)}"
      )
    else:
      sym_func = f"{cd.symbol} {cd.funk}"
      filename_fileno = (
          f"{util.remove_color(util.fmt_filename(elm.filepath))}"
          f":{util.remove_color(util.fmt_lineno(elm.line_number))}\n"
      )
      argname_argvals = (
          f"{cd.get_argname(c=False)}={cd.get_argdct(c=False)}"
      )
    split_args = argname_argvals.split("\n")
    num_args = len(split_args)
    pt1,pt2 = fmt_syms.get_PT(nargs=num_args)
    argname_argvals = "\n".join([f"{next(pt2,None)}{idt}{line}" for line in argname_argvals.split("\n")])
    fillchars = util.get_fillchars(sym_func)
    elm_as_str = f'{pt1}' + sym_func + fillchars + filename_fileno + argname_argvals
    return elm_as_str

  def prsd_else(elm,c=False):
    cd = elm.call_data[0]
    if isinstance(cd,str):
      return cd
    elif c:
      sym_func = f"{cd}"
      filename_fileno = (
          f"{util.fmt_filename(elm.filepath)}"
          f":{util.fmt_lineno(elm.line_number)}\n"
      )
      argname_argvals = f"{arg_name_val}"
    else:
      sym_func = f"{cd}"
      filename_fileno = (
          f"{util.remove_color(util.fmt_filename(elm.filepath))}"
          f":{util.remove_color(util.fmt_lineno(elm.line_number))}\n"
      )
      argname_argvals = f"{arg_name_val}"
    fillchars = util.get_fillchars(sym_func)
    elm_as_str = f'{S3}' + sym_func + fillchars + filename_fileno + argname_argvals
    return elm_as_str

  sns = SimpleNamespace(entry=entry)
  return sns.entry
write_file = _write_file()

if __name__ == "__main__":
  # load_aggdf = True
  # load_tfdf = False
  load_fcdf = True
  # if load_aggdf: aggdf = agg_main()

  # loadidf,whichload = True,"short_tfdf"
  # whichdf = "idf_w_lines"
  # idf2, cds = load_idf(loadidf,whichload,whichdf)
  # write_idf_file(idf2,list(cds))

  if load_fcdf:
    lwr = evtpkls_main()
    c,nc = lwr

  # print(fcdf.head())
  # print("\n".join(fcdf))
