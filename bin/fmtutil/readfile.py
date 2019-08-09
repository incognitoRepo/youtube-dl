import re,sys,os
from fsplit.filesplit import FileSplit
from math import floor
import pandas as pd
from .re_devkit import reDevKit
from pdb import set_trace as st
from types import SimpleNamespace
from dataclasses import dataclass,field
from typing import Dict, List, Any, Iterable
from .exception import MyException
from .constants import FILENAMES
from toolz.functoolz import compose_left
from collections import OrderedDict
rgxs = [
  re.compile( # regular line
      r"(?P<home>yt_dl)/(?P<interpaths>(?:(?!\s{2}).)+[/]){0,2}(?P<filename>.*?py)"
      r":(?P<line_number>\d{1,5})\s+(?P<event_kind>[a-z][a-z\s]{8})\s" #{event:9} {COLOR}{data}
      r"(?P<source_data>[\s]*.+)$"
  ),
  re.compile( # line continuation line
      r"^\s+"
      r"(?P<symbol>"
      r"(?:\s{3}[|\s]{6})"
      r"|(?:[\s]{3}[*\s]{6})"
      r"|(?:[.]{2}[.\s]{6})"
      r")\s"
      r"(?P<source_data>[\s]*.+)$"
  )
]

def debug_regex(rgxlist,line,excinfo):
  for rgx in rgxlist:
    redk = reDevKit()
    (redk.make_payload(rgx.pattern, line)
      .create()
      .openbrowser())

def dct4df(**kwds) -> Dict:
  got = lambda key: kwds.get(key,None)
  d = {
    "home": got('home'),
    "interpaths": got('interpaths'),
    "filename": got('filename'),
    "line_number": got('line_number'),
    "event_kind": got('event_kind'),
    "symbol": [ got('symbol') ],
    'source_data': [ got('source_data') ]
  }
  return d

def _get_df_from_tracefile():
  def entry(filename):
    df = compose_left(
      read_hunter_trace_file,
      process_lines_for_df,
      get_df
    )(filename)
    return df

  def read_hunter_trace_file(filename):
    with open(filename) as f:
      lines = f.readlines()
    assert len(lines) > 1, f"{filename=}, {lines=}"
    return lines

  def process_lines_for_df(filelines):
    assert len([elm for elm in filelines]) > 1, filelines
    processed_lines = []
    for line in filelines:
      if not line.strip():
        continue
      match = next(m for rgx in rgxs if (m := rgx.search(line) ))
      if len(gd1 := match.groupdict()) == rgxs[0].groups:
        dfdict = dct4df(**gd1)
        processed_lines.append(dfdict)
      elif len(gd2 := match.groupdict()) == rgxs[1].groups:
        dfdict = dct4df(**gd2)
        prev_dfdict = processed_lines[-1]
        prev_dfdict['source_data']+=dfdict['source_data']
        prev_dfdict['symbol'].append(dfdict['symbol'])
      else:
        import IPython
        from IPython.core.ultratb import ColorTB,VerboseTB
        print(ColorTB().text(*sys.exc_info()))
        print(f"{vars()=}")
        debug_regex(rgxs,line,sys.exc_info())
        st(); raise SystemExit; os._exit(-1)
    assert len(processed_lines) > 1, processed_lines
    return processed_lines

  def get_df(processed_filelines):
    assert processed_filelines and len(processed_filelines) > 1, processed_filelines
    df = pd.DataFrame(processed_filelines)
    columns = ['home','interpaths','filename','symbol','event_kind','line_number','source_data']
    return df[columns]

  sns = SimpleNamespace(entry = entry)
  return sns.entry
get_df_from_tracefile = _get_df_from_tracefile()

if __name__ == "__main__":
  filenames = FILENAMES
  for filename in filenames:
    filename = f"../{filename}"
    lines = readfile(filename)
    data4df = process_lines_for_df(lines)
