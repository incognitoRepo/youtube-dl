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


def format_main(filenames):
  dfs = {}
  for filename in filenames:
    df = fur.get_df_from_tracefile(filename)
    assert isinstance(df,pd.DataFrame), df
    dfs[filename] = df
  aggdf = fud.aggregate_dfs(list(dfs.values()))
  return aggdf

if __name__ == "__main__":
  dbg_flag = True
  pd.set_option('max_colwidth', 80)
  query,actions,outputs,filenames,write_func,pkldf = qcfg = QueryConfig().full()
  print(actions)
  dfpath = Path(pkldf.keywords['dfpath']).absolute()
  if dfpath.exists():
    if dbg_flag:
      pkldf(mode='rm')
    else:
      aggdf = pkldf(mode='r')
  if len(sys.argv) > 1:
    parser = argparse.ArgumentParser(
        description='Enter a QueryConfig key',
        epilog="e.g., python fmt.py full")
    parser.add_argument('qckey', type=str, nargs=1,
                        help='the common suffix for each file',
                        default="full.log")
    args = parser.parse_args()
    meth = args.qckey.pop().split('.')[0]
    with fu.methcaller(QueryConfig(),meth) as m:
      filenames = m().filenames
    aggdf = format_main(filenames)
    pkldf(mode='w',df=aggdf)
  if dbg_flag:
    aggdf = format_main(filenames)
    pkldf(mode='w',df=aggdf)
  print(aggdf.head())
  literate_style = fud.write_literate_style_df(aggdf,color=False)
  with open('lit.log', 'w') as f:
    f.write(literate_style)
  print(literate_style)

  fltrd_noline_df = fud.filter_line_events(aggdf,dfpath)
  dct_o_dfs_by_filename = fud.groupby_filename(aggdf,dfpath)
  fpgs.ppd(aggdf.snoop_data,pat='display.max_colwidth')


call_evts = aggdf[aggdf['event_kind'].str.contains('call')]
ca = call_evts.call_data
ca1,ca2,ca3,ca4,ca5,ca6 = ca
exc_evts = aggdf[aggdf['event_kind'].str.contains('exce')]
ex = exc_evts.call_data
ex1,ex2,ex3 = ex
