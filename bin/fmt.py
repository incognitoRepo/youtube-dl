import sys
import re
from toolz.functoolz import compose_left
from functools import partial
from pathlib import Path
from fsplit.filesplit import FileSplit
from pdb import set_trace as st
from typing import Dict, List, Any, Iterable, Tuple
import fmtutil.readfile as fur
import fmtutil.dataframe as fud
import fmtutil.exception as fue
import fmtutil.constants as fuc
import fmtutil.utils as fu
import fmtutil.public_goods as fpgs
import fmtutil.row as frow
import pysnooper
import numpy as np
import pandas as pd
from pandas import DataFrame
from collections import OrderedDict
from operator import methodcaller
from pprint import pprint as pp
import pdir
import argparse
from youtube_dl.hunterconfig import QueryConfig
from IPython.display import display, HTML
def pretty_print(df):
  return display(HTML(df.to_html().replace("\\n","<br>")))

def initdf(initdf):
  initdf.iloc[10:14,0].filepath = 'extractor/__init__.py'
  initdf.iloc[14:16,:].filepath = 'downloader/__init__.py'
  initdflst = list(initdf.itertuples())
  idflm4 = initdflst[-4]
  print(idflm4)
  return idflm4

def agg_main():
  query,actions,outputs,filenames,write_func,pkldf = qcfg = QueryConfig().full()
  dfpath = Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/df.pkl')
  dfs = {}
  for filename in filenames:
    df = fur.get_df_from_tracefile(filename)
    assert isinstance(df,pd.DataFrame), df
    dfs[filename] = df
  aggdf = fud.aggregate_aggdfs(list(dfs.values()))
  aggdf.to_pickle(dfpath)
  aggdf = pd.read_pickle(dfpath)
  literate_style = fud.write_literate_style_df(aggdf,filename="agg.full/agg")
  fltrd_noline_df = fud.filter_line_events(aggdf,dfpath)
  lit_style_noline = fud.write_literate_style_df(fltrd_noline_df,filename="agg.full/fltrd/noline")
  dct_o_dfs_by_filename = fud.groupby_filename(fltrd_noline_df,dfpath)
  for k,v in dct_o_dfs_by_filename.items():
    fud.write_literate_style_df(v,filename=f"agg.full/fltrd/grpd/{k}")
  return aggdf

def tf_main():
  query,actions,outputs,filenames,write_func,pkldf = qcfg = QueryConfig().targetfunc()
  dfpath = Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/tfdf/df.pkl')
  dfs = {}
  for filename in filenames:
    df = fur.get_df_from_tracefile(filename)
    assert isinstance(df,pd.DataFrame), df
    dfs[filename] = df
  tfdf = fud.aggregate_tfdfs(list(dfs.values()))
  dfpath.parent.mkdir(parents=True,exist_ok=True)
  tfdf.to_pickle(dfpath)
  tfdf = pd.read_pickle(dfpath)
  literate_style = fud.write_literate_style_df(tfdf,filename="targetfuncs/tfdf")
  fltrd_noline_df = fud.filter_line_events(tfdf,dfpath)
  lit_style_noline = fud.write_literate_style_df(fltrd_noline_df,filename="targetfuncs/fltrd/noline")
  dct_o_dfs_by_filename = fud.groupby_filename(fltrd_noline_df,dfpath)
  for k,v in dct_o_dfs_by_filename.items():
    fud.write_literate_style_df(v,filename=f"targetfuncs/fltrd/grpd/{k}")
  idf = dct_o_dfs_by_filename['__init__']
  idf.to_pickle(dfpath.parent.joinpath('idf.pkl'))
  row = initdf(idf)
  parsed = frow.process_verbose_row(row)
  print(parsed)
  return idf, row, parsed

def cli():
  parser = argparse.ArgumentParser(
    description='Enter a QueryConfig key',
    epilog="e.g., python fmt.py full")
  parser.add_argument('--qckey', type=str, nargs=1,
                      help='the common suffix for each file',
                      default="full.log")
  args = parser.parse_args()
  meth = args.qckey.pop().split('.')[0]
  if len(sys.argv) == 2:
    with fu.methcaller(QueryConfig(),meth) as m:
      filenames = m().filenames
  return filenames

if __name__ == "__main__":
  # aggdf = agg_main()
  idf, row, parsed = tf_main()
  # literate_style = fud.write_literate_style_df(tfdf,filename="tfdf.func/tfdf")


