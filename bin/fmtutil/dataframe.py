import sys
import ast
import re,os
import pandas as pd
import numpy as np
import itertools
import importlib.util
spec = importlib.util.spec_from_file_location("row", "/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/fmtutil/row.py")
row = importlib.util.module_from_spec(spec)
spec.loader.exec_module(row)
# sys.modules[module_name] = module



from pathlib import Path
from pdb import set_trace as st
from typing import Dict, List, Any, Iterable
from toolz.functoolz import compose_left
from dataclasses import dataclass, field, InitVar
from collections import OrderedDict, namedtuple
from types import SimpleNamespace
from functools import partial
from textwrap import TextWrapper
from beautifultable import BeautifulTable
from itertools import accumulate
from IPython.core import ultratb
sys.excepthook = ultratb.VerboseTB()
import better_exceptions
# better_exceptions.hook()
import traceback as tb
# exc = sys.exc_info()
# exc_tb = exc[2]
# tb.print_exception(*exc)
# tb.print_tb(exc_tb)

# def colorizetxt(txt,bgc=None,fgc=None):
#   d = {
#       "blu":f'\x1b[0;34m',
#       "grn":f'\x1b[0;32m',
#       "cyn":f'\x1b[0;36m'
#   }
#   reset = f'\x1b[0m'
#   rv = f"{d.get(bgc)}{txt}{reset}"
#   return rv

def _format_snoop_datacell():
  ledger = {}
  space = "\u0020"
  hard_coded_replacements = [
    ('/Users/alberthan/VSCodeProjects/vytd','vytd'),
    ('object at','@')
  ]
  d = {
    "1":f'|\x1b[0;34m',
    "2":f'|\x1b[0;32m',
    "3":f'|\x1b[0;36m',
    "4":f'|\x1b[0;33m'
  }

  def entry(cell):
    assert isinstance(cell,list) and isinstance(cell[0],str), f'{type(cell)=}{cell=}'
    cleaned_cell = [elm.strip() for elm in cell]
    paired_cell = [(elm.split(':=',1) if ':=' in elm else elm.split(':',1)) for elm in cleaned_cell]
    labeled_cell = {k.strip():v.strip() for k,v in paired_cell}
    fmtd_lst_o_str_nc, fmtd_lst_o_str_c = process_snoop_dct(labeled_cell,'nc'), process_snoop_dct(labeled_cell,'c')
    return (fmtd_lst_o_str_nc, fmtd_lst_o_str_c)

  implies_iterable = lambda v: v.startswith('[')
  def hard_coded_mods(v):
    og_v = v
    for hcr in hard_coded_replacements:
      v = v.replace(*hcr)
    return v

  def process_snoop_dct(cell:Dict,color:str):
    lst_o_fmtd_snoop_lines = []
    for indent_flag,(k,v) in enumerate(cell.items()):
      if not indent_flag:
        fmtd_kv_str = f"{process_key(k,color)}: {process_val(v)}"
      else:
        fmtd_kv_str = f"{space*2}{process_key(k,color)}: {process_val(v)}"
      lst_o_fmtd_snoop_lines.append(fmtd_kv_str)
    return lst_o_fmtd_snoop_lines

  def process_key(k:str,c:str):
    if c == 'nc':
      rv = f"{k[1:]}"
    else:
      rv = f"{d[k[0]]}{(k[1:])}\x1b[0m"
    return rv

  def process_val(v:str):
    v = hard_coded_mods(v)
    if implies_iterable(v):
      rv = process_implied_iterable(v)
    else:
      rv = process_str(v)
    return rv

  def process_implied_iterable(v:str):
    viterlen = v.count(',')+1
    viter = v[1:-1].split(',')
    viter_first,viter_rest_len = viter[0], viterlen-1 # n_rest = number of the rest of args
    assert viterlen == len(viter), f"{v=}, {viter=}"
    rv = f"{viter_first}, +({viter_rest_len})…,"
    return rv

  def process_str(v:str):
    viterlen = v.count(',')
    viter_first,viter_rest_len = v[0], viterlen-1
    rv = f"{v}, +({viterlen})...,"
    return rv

  return entry

format_snoop_datacell = _format_snoop_datacell()

def _format_call_datacell():
  ledger = {}
  space = "\u0020"
  hard_coded_replacements = [
    ('/Users/alberthan/VSCodeProjects/vytd','vytd'),
    ('object at','@')
  ]
  rgx1 = re.compile(r"(?P<funkname>.+?)(?P<fargs>\(.*\))")
  rgx2 = re.compile(r"(?P<funkname>.+?):\s(?P<fargs>\(.+\))")
  d = {
    "1":f'\x1b[0;34m',
    "2":f'\x1b[0;32m',
    "3":f'\x1b[0;36m',
    "4":f'\x1b[0;33m'
  }

  def entry(cell,event_kind):
    assert isinstance(cell,list) and len(cell) == 1, f'{type(cell)=}{cell=}'
    cell0 = cell[0]
    if event_kind.strip() not in ['exception','call']:
      return cell0, cell0
    fmtd_str_nc,fmtd_str_c = (process_exc_event_cell(cell0) # TODO: add a var here to cause an error
      if ('exception' in event_kind)
      else process_call_event_cell(cell0)
      if (event_kind == 'call' or '=' in cell0)
      else st())
    return fmtd_str_nc,fmtd_str_c # str

  def process_call_event_cell(cell) -> str:
    funkname,fargs = rgx1.search(cell).groupdict().values()
    # ['argv=None)','argv=None)']
    nicely_prepared_cell_args = _split_logic_for_call_datacell(fargs)
    if fargs == '()':
      return f"{funkname}{fargs}",f"{funkname}{fargs}"
    cleaned_cell_args = [elm.strip() for elm in nicely_prepared_cell_args]
    paired_cell_args = [elm.split('=',1) for elm in cleaned_cell_args]
    labeled_cell_args = {k.strip():v.strip() for k,v in paired_cell_args}
    lst_o_keys_nc, lst_o_keys_c = process_cell_dct(labeled_cell_args,'nc'), process_cell_dct(labeled_cell_args,'c')
    joined_loks_nc,joined_loks_c = ",".join(lst_o_keys_nc),",".join(lst_o_keys_c)
    fmtd_str_nc, fmtd_str_c = f"{funkname}({joined_loks_nc})",f"{funkname}({joined_loks_c})"
    return fmtd_str_nc, fmtd_str_c

  def process_cell_dct(cell:Dict,color:str) -> List[str]:
    lst_o_keys = []
    for i,(k,v) in enumerate(cell.items()):
      k = process_key(k,i,color)
      lst_o_keys.append(k)
    return lst_o_keys

  def process_key(k:str,i:int,c:str):
    if c == 'nc':
      if i == 1:
        rv = f"{k}"
      else:
        rv = f"{k}"
    else:
      if i == 1:
        rv = f"{d['1']}{k}\x1b[0m"
      else:
        rv = f"{d['2']}{k}\x1b[0m"
    return rv

  def process_exc_event_cell(cell) -> str:
    funkname,fargs = rgx2.search(cell).groupdict().values()
    # (<class 'OSError'>, OSError('dlopen(libc.so.6, 6): image not found'), <traceback object at 0x104bfa500>)
    split_cell = fargs[1:-1].split(',')
    exc_info_value = "".join(split_cell[1:3]) # sys.exc_info[1]
    fmtd_str_nc,fmtd_str_c = f"{funkname}({exc_info_value})",f"{funkname}({exc_info_value})"
    return fmtd_str_nc,fmtd_str_c

  def _split_logic_for_call_datacell(extracted_args_cell) -> List[str]:
    _split1 = extracted_args_cell.split(',')
    draft,record = [],[]
    for elm in _split1:
      if elm.startswith('('): elm = elm[1:]
      if elm.endswith(')'): elm = elm[:-1]
      if ('=') in elm:
        if draft:
          # join the current draft, append to record, start new draft with elm
          final = "".join(draft)
          record.append(final)
          draft = [elm]
        else:
          draft.append(elm)
      else:
        draft.append(elm)
    final = "".join(draft)
    record.append(final)
    return record


  sns = SimpleNamespace(entry=entry)
  return sns.entry

format_call_datacell = _format_call_datacell()

class LiterateUtil:
  def __init__(self):
    self.FormatLengths = namedtuple('FormatLengths', ['Index', 'filepath', 'line_number', 'event_kind', 'call_data', 'snoop_data'])
    self.FormatStrings = namedtuple('FormatStrings', ['Index', 'filepath', 'line_number', 'event_kind', 'call_data', 'snoop_data'])
    self.rgx1 = re.compile(r"(|\\x1b)\[\d;\d+m") # 10
    self.rgx2 = re.compile(r"(|\\x1b)\[0m")      # 7
    self.lengths = [9,20,9,10,80,180]

  def typeset(self,dnc,dc):
    """copy editor
        ['Index', 'filepath', 'line_number', 'event_kind', 'call_data', 'snoop_data']
    Arguments:
        strings {iterable[str]}
    Keyword Arguments:
        lengths {iterable[int]}
    lst_o_vals = [f"{str(r.Index):9.9}",f"{r.filepath:>20.20}",f"{str(r.line_number):<9.9}",f"{r.event_kind:>10.10}",f"{next(caitrr,'^'):<80.80}",f"{next(snitrr,'&'):<180.180}"]
    """
    stringsnc,stringsc = dnc['strings'],dc['strings']
    # sc = [s for s in strings[:5]] + [process_snoop_]
    # rgxcnt = [len(self.rgx1.findall(str(s))) for s in strings]
    # lengths = [r * 17 + l for l,r in zip(lengths,rgxcnt)]
    flens = self.FormatLengths(*self.lengths)
    _borders = list(accumulate([l for l in flens])) # 9+20+9+80=118 (snp starts on 119)
    # if len(strings) != 6: st()
    fstrsnc,fstrsc = self.FormatStrings(*stringsnc),self.FormatStrings(*stringsc)
    padtrunc = [f"{pad}.{trunc}" for pad,trunc in zip(flens,flens)]
    fmtdlstnc = [f"{str(s):<{pt}}" for s,pt in zip(fstrsnc,padtrunc)]
    fmtdlstc = [f"{str(s):<{pt}}" for s,pt in zip(fstrsc,padtrunc)]
    fmtdstrnc,fmtdstrc = "".join(fmtdlstnc),"".join(fmtdlstnc)
    return fmtdstrnc,fmtdstrc

def _write_literate_style_df():
  util = LiterateUtil()
  space = "\u0020"
  typeset_args_lengths = [9,20,9,10,80,180]

  def typeset_args1(r):
    ca_nc,ca_c = format_call_datacell(r.call_data,r.event_kind)
    sn_nc,sn_c = format_snoop_datacell(r.snoop_data)
    stringsnc = [r.Index, r.filepath, r.line_number, r.event_kind, ca_nc, sn_nc]
    stringsc = [r.Index, r.filepath, r.line_number, r.event_kind, ca_c, sn_c]
    dnc = {
      "strings": stringsnc,
      "lengths": typeset_args_lengths #[clrcnt(s)*15+l for s,l in zip(strings,typeset_args_lengths)]
    }
    dc = {
      "strings": stringsc,
      "lengths": typeset_args_lengths
    }
    return dnc,dc

  def typeset_args2(r):
    sn_nc,sn_c = format_snoop_datacell(r.snoop_data)
    stringsc = [space]*5 + [sn_c]
    stringsnc = [space]*5 + [sn_nc]
    dnc = {
      "strings": stringsnc,
      "lengths": typeset_args_lengths #[clrcnt(s)*15+l for s,l in zip(strings,typeset_args_lengths)]
    }
    dc = {
      "strings": stringsc,
      "lengths": typeset_args_lengths
    }
    return dnc,dc

  def entry(df,filename,color=True):
    return write_literate_style_df(df,filename,color=color)

  def write_literate_style_df(df,filename,color=True):
    _nclst,_clst = [],[]
    for rowtpl in df.itertuples():
      r = rowtpl
      # assert r._fields == ('Index', 'filepath', 'line_number', 'symbol', 'event_kind', 'call_data', 'code_data', 'snoop_data'), r
      lines_for_row = len(r.snoop_data) - 1
      _ncsublst,_csublst=[],[]
      dnc,dc = typeset_args1(r)
      fmtdstr_nc,fmtdstr_c = util.typeset(dnc,dc)
      _ncsublst.append(fmtdstr_nc);_csublst.append(fmtdstr_c)
      for line in range(lines_for_row):
        dnc,dc = typeset_args2(r)
        fmtdstr_nc,fmtdstr_c = util.typeset(dnc,dc)
        _ncsublst.append(fmtdstr_nc);_csublst.append(fmtdstr_c)
      _ncsublst_as_str = "\n".join(_ncsublst);_csublst_as_str = "\n".join(_csublst)
      _nclst.append(_ncsublst_as_str);_clst.append(_csublst_as_str)
    _retvalnc,_retvalc = "\n".join(_nclst),"\n".join(_clst)
    name_file_tpls = [(f"{filename}.c",_retvalc),(f"{filename}.nc",_retvalnc)]
    write_to_file(name_file_tpls)
    return _retvalnc,_retvalc

  def write_to_file(name_file_tpls):
    for name,filedata in name_file_tpls:
      p = Path(name).resolve()
      if not p.parent.exists():
        p.parent.mkdir(parents=True,exist_ok=True)
      with open(f"{name}.lit.log", 'w') as f:
        f.write(filedata)

  def noco(s):
    rgx1 = re.compile(r"(|\\x1b)\[\d;\d+m")
    rgx2 = re.compile(r"(|\\x1b)\[0m")
    s = rgx1.sub(repl="",string=s)
    s = rgx2.sub(repl="",string=s)
    return s

  sns = SimpleNamespace(entry=entry)
  return sns.entry

write_literate_style_df = _write_literate_style_df()
class BeautifulUtil:
  def __init__(self):
    self.cols_and_widths = [("Index",9),("filepath",20),("line_number",9),("call_data",80),("snoop_data",80)]
    self.columns = ["Index","filepath","line_number","call_data","snoop_data"]
    self.widths = [9,20,9,80,80]
    self.bt_widths = [9,20,9,80 + 9,80 + 9]
    self.textwrapper_width = 80
    self.safecolumns = ["filepath","line_number","symbol","event_kind","call_data","code_data","snoop_data"]

def _create_beautiful_table():
  util = BeautifulUtil()

  def entry(df):
    return create_beautiful_table(df)

  def create_beautiful_table(df):
    table = get_cfgd_table()
    rows = process_df_rows(df)
    for row in rows:
      table.append_row(row)
    return table.get_string(recalculate_width=False)

  def get_cfgd_table():
    nt = new_table = BeautifulTable(
        max_width=200,default_alignment=BeautifulTable.ALIGN_LEFT,default_padding=1
    )
    nt.column_headers,nt.column_widths = util.columns,util.widths
    nt.set_style(BeautifulTable.STYLE_COMPACT)
    return nt

  def process_df_rows(df):
    newrows,i,si = [],0,0
    for rawrow in df[util.safecolumns].itertuples():
      row:namedtuple = compose_left(
          wrapdatalines,
          partial(colorize,clrs=False),
      )(rawrow)
      newrows.append([f"{row.Index}",f"{row.filepath}",f"({row.line_number}):",f"{row.call_data}",f"{row.snoop_data}"])
    return newrows

  def wrapdatalines(rawrow):
    def trunc_func(line): return f"{line[:util.textwrapper_width]}…" if len(line) > util.textwrapper_width else line
    datacells = [rawrow.call_data, rawrow.code_data, rawrow.snoop_data]
    cad,cod,snp = [[trunc_func(elm) for elm in datacell] for datacell in datacells]
    rv = rawrow._make([rawrow.Index,rawrow.filepath,rawrow.line_number,rawrow.symbol,rawrow.event_kind,cad,cod,snp])
    return rv

  def colorize(rowlst,clrs=True):
    if not clrs: return rowlst
    blu,grn,cyn = f'\x1b[0;34m',f'\x1b[0;32m',f'\x1b[0;36m'
    prefixes = iter([f'\x1b[0;34m',f'\x1b[0;32m',f'\x1b[0;36m'])
    suffix = f'\x1b[0m'
    newlst = rowlst[:2] + [f"{next(prefixes)}{elm}{suffix}" for elm in rowlst[-3:]]
    return newlst

  sns = SimpleNamespace(entry=entry)
  return sns.entry
create_beautiful_table = _create_beautiful_table()

class GroupByUtil:
  def __init__(self):
    self.dfpath = ""
    self.gbs_dir = ""

  def write_df_logfiles(self,gbdfs_dct,dfpath):
    assert self.dfpath.exists(), self.dfpath
    self.mk_gbs_dir()
    def get_path_for_gbdf(filename): return self.gbs_dir.joinpath(filename)
    for filename,gbdf in gbdfs_dct.items():
      gbdf_path = get_path_for_gbdf(filename)
      compose_left(
          create_beautiful_table,
          partial(self.write_to_disk,name=gbdf_path)
      )(gbdf)

  def write_to_disk(self,table:str,name:str):
    with open(name,'w') as f:
      f.write(table)

  def mk_gbs_dir(self):
    self.gbs_dir = self.dfpath.parent.joinpath('gbs')
    self.gbs_dir.mkdir(parents=True,exist_ok=True)

  def get_path_for_gbdf(self,filename):
    gbs_dfpath = self.gbs_dir.joinpath(self.filter_type)
    return gbs_dfpath

def _groupby_filename() -> Dict[str,pd.DataFrame]:
  util = GroupByUtil()

  def entry(df,dfpath):
    util.dfpath = dfpath
    dct_o_dfs = group_df_by_filename(df)
    return dct_o_dfs

  def group_df_by_filename(df):
    gbs = get_groups_as_lst_o_dfs(df.copy())
    def filename_from_df(df): return Path(df.iloc[0].filepath).name.replace('.py','')
    dct_o_filename_df_pairs = {filename_from_df(g):g for g in gbs}
    return dct_o_filename_df_pairs
    for gb,filename in zip(gbs,filenames):
      write_df_logfile(gb,filename)
    return gbs

  def get_groups_as_lst_o_dfs(df):
    gb = df.groupby(['filepath'])
    gbs = [gb.get_group(g) for g in gb.groups]
    return gbs

  sns = SimpleNamespace(entry=entry)
  return sns.entry
groupby_filename = _groupby_filename()

class FilterUtil:
  def __init__(self,filter_type):
    self.filter_type = filter_type

  def write_df_logfile(self,fltrd_df,dfpath):
    fltrd_dfpath = self.get_path_for_fltrd_df(dfpath)
    compose_left(
        create_beautiful_table,  # -> str
        partial(self.write_to_disk,name=fltrd_dfpath)
    )(fltrd_df)

  def write_to_disk(self,table:str,name:str):
    with open(name,'w') as f:
      f.write(table)

  def get_path_for_fltrd_df(self,dfpath):
    filter_dir = dfpath.parent.joinpath('fltrd')
    filter_dir.mkdir(parents=True,exist_ok=True)
    filter_dfpath = filter_dir.joinpath(self.filter_type)
    return filter_dfpath

def _filter_line_events():
  util = FilterUtil(filter_type='line')

  def entry(df,dfpath):
    df = df.copy()
    fltrd_df = compose_left(
        get_line_event_mask,
        lambda mask: df[mask]
    )(df)
    return fltrd_df

  def get_line_event_mask(df):
    mask = df.event_kind.str.strip() != 'line'
    return mask

  sns = SimpleNamespace(entry=entry)
  return sns.entry
filter_line_events = _filter_line_events()

class AggregateUtil:
  def __init__(self):
    self.columns = ["filepath","line_number","symbol","event_kind","call_data","code_data","snoop_data"]

  def base_dct_factory(self):
    d = OrderedDict({
        "home": None,
        "interpaths": None,
        "filename": None,
        "line_number": None,
        "symbol": None,
        "event_kind": None,
        "call_data": None,
        "code_data": None,
        "snoop_data": None
    })
    return d

  def process_snoop_data(self, snp_dtacell):
    """snp_dtacell: List[Datum]
      Datum.split(':='): Mapping[str,StrWithBrackets]
      StrWithBrackets[1:-1].split(',') = ValList = List[str]
      "\n".join(ValList): str
    """
    space,cs = "\u0020",iter(['blu','grn','cyn'])
    sublst:str
    snp_dtacell:List
    for sublst in snp_dtacell:
      if (ce:=':=' in sublst) or (c:=':' in sublst):
        def mapfunk(sep): return map(str.strip,sublst.split(sep))
        sublstkey,sublstval = mapfunk(':=') if ce else mapfunk(':') if c else ('ERRR','RRROR')
        sublstval = sublstval.replace("None", "Mome")
        sublstval,sublstvallen = [sublstval] if not (isinstance(sublstval,list)) else sublstval, sublstval.count(',') + 1
        valsplitaslst = sublstval[1:-1].split(',') if ',' in sublstval else [sublstval]
        linestrfmtd = f"{sublstkey}({sublstvallen}): [{valsplitaslst[0][0]:<80.80}{',…' if sublstvallen > 1 else ''}]"
      else:
        print(sublst)
        st()
    return linestrfmtd

def _aggregate_aggdfs():
  util = AggregateUtil()

  def entry(input_dfs,verbose=False):
    # at this point we have 3 input_dfs
    # rename data columns, merge into one df>to_dict,iterate_over_rows,
    assert isinstance(input_dfs[0],pd.DataFrame) and len(input_dfs[0]) > 1, input_dfs
    aggdf = compose_left(
        rename_data_columns,
        merge_dfs_into_one,
    )(input_dfs)
    if verbose:
      return aggdf
    print(aggdf.columns)
    assert all([col in aggdf.columns for col in util.columns]), aggdf.columns
    return aggdf[["filepath","line_number","symbol","event_kind","call_data","code_data","snoop_data",]]

  def rename_data_columns(input_dfs):
    """
    ..input_dfs:: {calldf,codedf,snoopdf}
    ..returns  :: {"call":calldf,"code":codedf,"snoop":snoopdf}`
    """
    def rename(df,name): return df.rename(columns={"source_data":f"{name}_data"},inplace=False)
    dct_o_renamed_dfs = {name:rename(df,name) for name,df in zip(["call","code","snoop"],input_dfs)}
    assert all([(colname in df.columns and len(df) > 1) for colname,df in zip(["call_data","code_data","snoop_data"],dct_o_renamed_dfs.values())])
    return dct_o_renamed_dfs

  def merge_dfs_into_one(dct_o_renamed_dfs):
    aggdf = compose_left(
        iterate_over_rows,
        aggregate_lst_o_merged_rowdcts,
    )(dct_o_renamed_dfs)
    return aggdf

  def colorize_lst(l,bc=None,fc=None,c=False):
    """usage: c=True for colors"""
    if not c: return l
    bgc = intense_background_black = ('\x1b[0;100m','\x1b[0m')
    strt = [bgc[0] for _ in range(len(l))]
    stop = [bgc[1] for _ in range(len(l))]
    zipd = zip(strt,l,stop)
    _jmp = _joinmepls = []
    for rt,txt,op in zipd:
      s = f"{rt}{txt}{op}"
      _jmp.append(s)
    # clrzd_str = "\n".join(_jmp)
    return _jmp

  def create_filepath(home,interpath,filename):
    # from pdb import set_trace as st; st()
    h = home
    i = f"{interpath}/" if interpath else ""
    f = filename
    rv = f"{h}/{i}{f}"
    return rv

  def iterate_over_rows(dct_o_rnd_dfs):
    lst_o_merged_rowdcts = []
    try:
      cadf,codf,sndf = [dct_o_rnd_dfs.get(k) for k in ("call","code","snoop")]
      si,slen,sdone = 0, len(sndf), False
    except BaseException:
      import IPython
      from IPython.core.ultratb import ColorTB,VerboseTB
      from inspect import getfile
      print(getfile(IPython.core.ultratb))
      print(ColorTB().text(*sys.exc_info()))
    for i in range(len(cadf)):
      base_dct = util.base_dct_factory()
      car,cor,snr = cadf.iloc[i],codf.iloc[i],sndf.iloc[si]
      assert (caln:=car.line_number) == (coln:=cor.line_number), f"{caln=},{coln=}"
      cadata,codata = car.call_data,cor.code_data
      if (not sdone and (snr.get('line_number',None) == caln)):
        sndata = snr.snoop_data
        assert isinstance(sndata,list) and isinstance(sndata[0],str), sndata[0]
        # if len(sndata) > 1:
        # st()
        sdone,si = (end:=bool(si == slen)), (si if end else si + 1)
      try:
        base_dct.update({
            "home": car.home,
            "interpaths": car.interpaths,
            "filename": car.filename,
            "filepath": create_filepath(car.home,car.get('interpath',''),car.filename),
            "line_number": car.line_number,
            "event_kind": car.event_kind,
            "symbol": [sym for sym in (getattr(car.symbol,'symbol',None),getattr(cor.symbol,'symbol',None))],
            "call_data": colorize_lst([elm for elm in cadata]),
            "code_data": colorize_lst([elm for elm in codata]),
            # "snoop_data": colorize_lst([util.de_bracketize_snoop_data(elm) for elm in sndata]) if sndata else "<None>",
            # "snoop_data": colorize_lst([elm for elm in sndata]),
            # "snoop_data": colorize_lst([elm for elm in sndata]),
            # "snoop_data": util.process_snoop_data(sndata)
            # "snoop_data": [util.process_snoop_data(sndata)],
            "snoop_data": sndata if sndata else "<None>",
        })
        lst_o_merged_rowdcts.append(base_dct)
      except BaseException:
        from IPython.core.ultratb import ColorTB,VerboseTB
        print(ColorTB().text(*sys.exc_info()))
    assert len(lst_o_merged_rowdcts) > 1, lst_o_merged_rowdcts
    return lst_o_merged_rowdcts

  def aggregate_lst_o_merged_rowdcts(merged_rowdcts):
    aggdf = pd.DataFrame(merged_rowdcts)
    return aggdf

  sns = SimpleNamespace(entry=entry)
  return sns.entry
aggregate_aggdfs = _aggregate_aggdfs()


class TargetFuncUtil:
  def __init__(self):
    self.columns = ["filepath","line_number","symbol","event_kind","call_data","snoop_data"]

  def base_dct_factory(self):
    d = OrderedDict({
        "home": None,
        "interpaths": None,
        "filename": None,
        "line_number": None,
        "symbol": None,
        "event_kind": None,
        "call_data": None,
        "snoop_data": None
    })
    return d

  def process_snoop_data(self, snp_dtacell):
    """snp_dtacell: List[Datum]
      Datum.split(':='): Mapping[str,StrWithBrackets]
      StrWithBrackets[1:-1].split(',') = ValList = List[str]
      "\n".join(ValList): str
    """
    space,cs = "\u0020",iter(['blu','grn','cyn'])
    sublst:str
    snp_dtacell:List
    for sublst in snp_dtacell:
      if (ce:=':=' in sublst) or (c:=':' in sublst):
        def mapfunk(sep): return map(str.strip,sublst.split(sep))
        sublstkey,sublstval = mapfunk(':=') if ce else mapfunk(':') if c else ('ERRR','RRROR')
        sublstval = sublstval.replace("None", "Mome")
        sublstval,sublstvallen = [sublstval] if not (isinstance(sublstval,list)) else sublstval, sublstval.count(',') + 1
        valsplitaslst = sublstval[1:-1].split(',') if ',' in sublstval else [sublstval]
        linestrfmtd = f"{sublstkey}({sublstvallen}): [{valsplitaslst[0][0]:<80.80}{',…' if sublstvallen > 1 else ''}]"
      else:
        print(sublst)
        st()
    return linestrfmtd

def _aggregate_tfdfs():
  util = TargetFuncUtil()

  def entry(input_dfs,verbose=False):
    # at this point we have 3 input_dfs
    # rename data columns, merge into one df>to_dict,iterate_over_rows,
    assert isinstance(input_dfs[0],pd.DataFrame) and len(input_dfs[0]) > 1, input_dfs
    tfdf = compose_left(
        rename_data_columns,
        merge_dfs_into_one,
    )(input_dfs)
    if verbose:
      return tfdf
    print(tfdf.columns)
    assert all([col in tfdf.columns for col in util.columns]), tfdf.columns
    return tfdf[["filepath","line_number","symbol","event_kind","call_data","snoop_data",]]

  def rename_data_columns(input_dfs):
    """
    ..input_dfs:: {calldf,codedf,snoopdf}
    ..returns  :: {"call":calldf,"code":codedf,"snoop":snoopdf}`
    """
    def rename(df,name): return df.rename(columns={"source_data":f"{name}_data"},inplace=False)
    dct_o_renamed_dfs = {name:rename(df,name) for name,df in zip(["call","snoop"],input_dfs)}
    assert all([(colname in df.columns and len(df) > 1) for colname,df in zip(["call_data","snoop_data"],dct_o_renamed_dfs.values())])
    return dct_o_renamed_dfs

  def merge_dfs_into_one(dct_o_renamed_dfs):
    tfdf = compose_left(
        iterate_over_rows,
        aggregate_lst_o_merged_rowdcts,
    )(dct_o_renamed_dfs)
    return tfdf

  def colorize_lst(l,bc=None,fc=None,c=False):
    """usage: c=True for colors"""
    if not c: return l
    bgc = intense_background_black = ('\x1b[0;100m','\x1b[0m')
    strt = [bgc[0] for _ in range(len(l))]
    stop = [bgc[1] for _ in range(len(l))]
    zipd = zip(strt,l,stop)
    _jmp = _joinmepls = []
    for rt,txt,op in zipd:
      s = f"{rt}{txt}{op}"
      _jmp.append(s)
    # clrzd_str = "\n".join(_jmp)
    return _jmp

  def create_filepath(home,interpath,filename):
    # from pdb import set_trace as st; st()
    h = home
    i = f"{interpath}/" if interpath else ""
    f = filename
    rv = f"{h}/{i}{f}"
    return rv

  def iterate_over_rows(dct_o_rnd_dfs):
    lst_o_merged_rowdcts = []
    try:
      cadf,sndf = [dct_o_rnd_dfs.get(k) for k in ("call","snoop")]
      si,slen,sdone = 0, len(sndf), False
    except BaseException:
      import IPython
      from IPython.core.ultratb import ColorTB,VerboseTB
      from inspect import getfile
      print(getfile(IPython.core.ultratb))
      print(ColorTB().text(*sys.exc_info()))
    for i in range(len(cadf)):
      base_dct = util.base_dct_factory()
      car,snr = cadf.iloc[i],sndf.iloc[si]
      cadata = car.call_data
      if (not sdone and (snr.get('line_number',None) == car.line_number)):
        sndata = snr.snoop_data
        assert isinstance(sndata,list) and isinstance(sndata[0],str), sndata[0]
        sdone,si = (end:=bool(si == slen)), (si if end else si + 1)
      try:
        base_dct.update({
            "home": car.home,
            "interpaths": car.interpaths,
            "filename": car.filename,
            "filepath": create_filepath(car.home,car.get('interpath',''),car.filename),
            "line_number": car.line_number,
            "event_kind": car.event_kind,
            "symbol": [sym for sym in (getattr(car.symbol,'symbol',None))] if (getattr(car.symbol,'symbol',None)) else [],
            "call_data": colorize_lst([elm for elm in cadata]),
            "snoop_data": sndata if sndata else "<None>",
        })
        lst_o_merged_rowdcts.append(base_dct)
      except BaseException:
        from IPython.core.ultratb import ColorTB,VerboseTB
        print(ColorTB().text(*sys.exc_info()))
    assert len(lst_o_merged_rowdcts) > 1, lst_o_merged_rowdcts
    return lst_o_merged_rowdcts

  def aggregate_lst_o_merged_rowdcts(merged_rowdcts):
    tfdf = pd.DataFrame(merged_rowdcts)
    return tfdf

  sns = SimpleNamespace(entry=entry)
  return sns.entry
aggregate_tfdfs = _aggregate_tfdfs()

class LitUtil:
  def __init__(self):
    self.row_cols = [
      'filepath', 'line_number', 'symbol', 'event_kind', 'call_data', 'snoop_data'
      ]

def _write_lit_file():
  util = LitUtil()

  def entry(df,tfdfpath):
    df = df.copy()
    writeable_string = compose_left(
        iterate_over_rows,
    )(df)
    return tfdfpath

  def iterate_over_rows(df):
    for row in df.itertuples():
      fmtd = format_line(row.filepath, row.line_number, row.call_data)
    return mask

  def format_line(filename,line_number,call_data):
    rgx = re.compile(r"(?P<funcname>[A-z0-9_]+)\s?=\s?\((?P<funkargs>[A-z0-9_]+)\s?=\s?\(")
    m = re.search(call_data)
    funcname,args = gd = m.groupdict()
    if not isinstance(call_data,FmtdCellData):

      pass
    else:
      funcname = call_data.funcname
      keys = call_data.get_keys
      args = {k:call_data.get_arg(k) for k in keys}

    fn = f'{Path(filename).stem:>10.10}' # len is 8 or 10 'd.__init__'
    ln = f'{line_number:0>3}'
    funk = call_data.funcname
    args = call_data.get_arg('info_dict'),call_data.get_arg('params')
    metadata = f"{fn}:{ln}"

  sns = SimpleNamespace(entry=entry)
  return sns.entry
filter_line_events = _filter_line_events()

write_lit_file = _write_lit_file()
#   ewaf:032 aowejfiewofjaew({aopiwef=aewpfjwejfoewjj,
#     apwiefj=;vseiowf
#     aefawe=24rt23}
# w2ewaf:032 aowejfiewofjaew({aopiwef=aewpfjwejfoewjj,
#     apwiefj=;vseiowf
#     aefawe=24rt23}
