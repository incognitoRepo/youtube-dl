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
stackprinter.set_excepthook(style='darkbg2')
basepath = Path('/Users/alberthan/VSCodeProjects/vytd')
args_line_idx_len = 76
fmt_syms = FormatSymbols()
DEBUG = True
break_point = 13
break_points = [38,39,40]
TRUNC = True
trunc_start,trunc_end = 0, 15

def decompose_hunter_string(hs):
  rgx_cll = r""
  rgx_ret = r""
  rgx_exc = r""
  rgx_lne = r""

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
    self.init_header_switch = False
    self.ydl_header_switch = False
    self.init_endheader_switch = False

  def load_event_pickles(self):
    pklpth = Path("/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle/evtdcts_pklpth.pkl")
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

  def tier_test(self, pth, pth2):
    """..returns: self.headers_for_<tier> if tier else None"""
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
    else:
      return None

  def headers_for_ydl(self, row, row2):
    idx,pth,lno,evt,mos,pos,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,ogi2 = row2
    t1,t2,t3 = fmt_syms.get_Tier1()
    if "YoutubeDL" in pth and "YoutubeDL" not in pth2:
      header = MutableStr(f"{t2} #region2 {ogi+1}")
      self.ydl_header_stack.append(header)
      self.ydl_header_switch = True
      return [] # returning row causes header_row += row to convert pd.core.frame to list
    elif "YoutubeDL" not in pth and "YoutubeDL" in pth2:
      if self.ydl_header_stack:
        self.ydl_endheader_switch = True
        header = self.ydl_header_stack.pop()
        header.modify_inplace(f"-{ogi2}")
        m = re.search(r"\d+[-]\d+", str(header))
        og_nums = m.group()
        endheader = MutableStr(f"{t2} #endregion2 {og_nums}")
        return HeaderRow(row=row,header=endheader)
      else:
        return []
    else:
      assert "YoutubeDL" in pth and "YoutubeDL" in pth2, f"{pth=}, {pth2=}"
      return []

  def headers_for_init(self, row, row2):
    idx,pth,lno,evt,mos,pos,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,ogi2 = row2
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
        return HeaderRow(row=row,header=endheader)
      else:
        return []
    else:
      assert "__init__" in pth and "__init__" in pth2, f"{pth=}, {pth2=}"
      return []

  def headers_for_line_evts(self,row,row2):
    """Line Event"""
    idx,pth,lno,evt,mos,pos,ogi = row
    idx2,pth2,lno2,evt2,mos2,pos2,ogi2 = row2
    if "line" not in evt and "line" in evt2:
      le1,le2,le3 = fmt_syms.get_LE()
      header = MutableStr(f"{le1} {ogi}-")
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
    query,actions,outputs,filenames,write_func,evtdcts_pklpth = qcfg = QueryConfig().eventpickle()
    with open(evtdcts_pklpth,'rb') as f:
      evt_dcts = pickle.load(f)
    dc = DataCollections(evt_dcts)
    epdf, evts, evts_df = dc.evt_dcts_df, dc.evts, dc.evts_df
    epdf = epdf[:10000]  #!! RIGHT HERE = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =   = = =
    epdf2 = epdf.rename_axis('og_index').reset_index()
    columns = [
      'filename','lineno','kind',
      'hunter_monostr','hunter_polystr', # these 2 replace dta
      'og_index',
    ]
    epdf3 = epdf2[columns]
    lwr = lst_w_regions = add_regions(epdf3)
    str_lst = []
    for elm in lwr:
      s = []
      if not any(elm):
        continue
      s.append(f"{len(elm)=}, {type(elm)=}")
      for subelm in elm:
        if subelm:
          header,row = subelm.header,subelm.row
          s.append(f"  {header=}\n")
          s.append(f"  {row=}\n")
      sj = "\n".join(s)
      str_lst.append(sj)
    str_join = "\n".join(str_lst)
    with open('str_join.log', 'w') as f:
      f.write(str_join)
    wpath = util.homepath.joinpath('bin/lwr')
    lwr2 = [elm for lst in lwr for elm in lst if elm] # now, each elm is a HeaderRow w/ len=(1|2)
    lwr3 = write_file(df=epdf3,lst_w_regions=lwr2,writepath=wpath)
    return lwr3

  def add_regions(epdf):
    prwi = False  # prwi: prev row was init
    output_lines = []
    itrlst = list(epdf.itertuples())
    i,end = 0,len(itrlst)
    while i < end:
      header_row_objs = []
      row,row2 = itrlst[i],(itrlst[i + 1] if i < (len(itrlst) - 1) else None)
      idx,pth,lno,evt,mos,pos,ogi = row
      idx2,pth2,lno2,evt2,mos2,pos2,ogi2 = row2 if row2 else [""] * len(row)
      if record_func := util.tier_test(pth,pth2):
        if not row2:
          i += 1
          continue
        header_row_objs.append(record_func(row,row2))
      elif header_stack := util.header_switch_test():
        header = header_stack.pop()
        header_row_objs.append(HeaderRow(row=row, header=header))
        header_stack.append(header)
      if "line" in evt or "line" in evt2:
        if not row2:
          i += 1
          continue
        header_row_objs.append(util.headers_for_line_evts(row,row2))
      if not any(header_row_objs):
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
    self.initfiles = self.load_init_files()
    self.return_monostr = []
    self.return_polystr = []

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

  def entry(df,lst_w_regions=None,writepath=None):
    iterlst = lst_w_regions
    util.cache = None
    return_strings_c,return_strings_nc = iterate_thru_df(iterlst)
    #
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
    """
    ..elm: len=(1|2), type=(HeaderRow)
    ..len:2 means there is a header and a row
    ..len:1 means there is a row only
    """
    for i,elm in enumerate(iterlst):
      # each elm is a HeaderRow w/ len=(1|2)
      prsdmono,prsdpoly = process_header_row(elm)
      util.return_monostr += prsdmono
      util.return_polystr += prsdpoly
    return util.return_monostr, util.return_polystr

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

  def get_prefix_symbol_for_row(self,row):
    symbols = set()
    d = {'call':fmt_syms.get_call(),'return':fmt_syms.get_return()}
    tier_lvls = {'__init__':}
    idx,fnm,lno,knd,hms,hps,ogi = r0

  def process_header_row(hr):
    header,row = hr.header,hr.row
    if DEBUG and row.og_index == break_point: st()
    util.cache = row
    if "call" in row.event_kind:
      prefixsymbol = fmt_syms.get_call()
    elif "return" in row.event_kind:
      prefixsymbol = fmt_syms.get_return()
    else:
      prefixsymbol = ""
    if ("line" not in row.event_kind):
      row = row._replace(filepath=util.fix_init(row))
    hunter_event = row.hunter_event
    if any(util.is_tier_level_row(row)):
      tier_levels = util.is_tier_level_row(row)
      c,nc = tier_level_row(row, tier_levels)
      return c,nc
    elif isinstance(row, UserString):
      us1,us2,us3 = uss = fmt_syms.get_US(presym)
      c,nc = f'{us}' + str(row),f'{us}' + str(row)
      return c,nc
    elif isinstance(cd, SimpleFunkWithArgs):
      sfwa1,sfwa2,sfwa3 = sfwas = fmt_syms.get_SFWA(presym)
      c = simp_funk_w_args(row,sym1=sfwa1,sym2=sfwa2,c=True),
      nc =  simp_funk_w_args(row,sym1=sfwa1,sym2=sfwa2,c=False)
      # print(c);print(nc)
      # st()
      return c,nc
    elif isinstance(cd,LineEvent):
      lec,lenc = prsd_line(row,c=True),prsd_line(row,c=False)
      return lec,lenc
    elif isinstance(cd,ParsedHTML):
      ph1,ph2,ph3 = phs = fmt_syms.get_PH(presym)
      return (
        prsd_html(row,sym1=ph1,sym2=ph2,c=True),
        prsd_html(row,sym1=ph1,sym2=ph2,c=False)
      )
    elif isinstance(cd,ParsedJSON):
      pj1,pj2,pj3 = pjs = fmt_syms.get_PJ(presym)
      return (prsd_json(row,sym1=pj1,sym2=pj2,c=True),
        prsd_json(row,sym1=pj1,sym2=pj2,c=False)
      )
    elif isinstance(cd,VerboseList):
      return prsd_lst(row,c=True),prsd_lst(row,c=False)
    elif isinstance(cd[0],ParsedTuple):
      return prsd_tpl(row,c=True),prsd_tpl(row,c=False)
    else:
      return prsd_else(row,c=True),prsd_else(row,c=False)

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
  load_epdf = True

  if load_epdf:
    lwr = evtpkls_main()
    c,nc = lwr

  # print(epdf.head())
  # print("\n".join(epdf))
