import re,sys,os
import cgitb;cgitb.enable(format='text')
from re_devkit import reDevKit
from pdb import set_trace as st
from dataclasses import dataclass,field
from typing import Dict, List, Any, Iterable
from exception import MyException
filename_prefixes, base = ["cap", "cop", "snp"], "top.log"
filenames = [f"{prefix}.{base}" for prefix in filename_prefixes]
rgxs = [
  re.compile(
      r"(?P<home>yt_dl)/(?P<interpaths>.+[/]){0,2}(?P<filename>.*py)"
      r":(?P<line_number>\d{1,5})\s+(?P<event_kind>[a-z]+)\s+"
      r"(?P<source_data>[^\s].+)$"
  ),
  re.compile(
      r"\s+"
      r"(?P<symbol>[|]|[*]|[.]{3})\s+"
      r"(?P<source_data>[^\s].+)$"
  )
]
def debug_regex(rgxlist,line,excinfo):
  for rgx in rgxlist:
    redk = reDevKit()
    (redk.make_payload(rgx.pattern, line)
      .create()
      .openbrowser())

def iterable_from_file(filename: str):
  with open(filename) as f:
    filelines = f.readlines()
  iterablines = iter(filelines)
  return iterablines

def code_dfdict(**kwds) -> Dict:
  if 'symbol' in kwds:
    kwds['line_continuation'] = (kwds['symbol'],kwds['source_data'])
    del kwds['source_data']
  rv = codeline_dictfact()
  rv.update(kwds)
  return rv

def codeline_dictfact():
  d = {
    "filename": None,
    "line_number": None,
    "line_continuation": None, #tuple(symbol,source_data)
    "indent_level": None,
    "event_kind": None,
    "source_data": None
  }
  return d


@dataclass
class FileProcesspr:
  raw_input: Dict[str,Any] #output from iterable_from_file
  output_for_df: List[Dict] = field(default_factory=list,init=False) # class var

  def __post_init__(self):
    self.prepare_lines_for_df(self.raw_input)

  def prepare_lines_for_df(self, filelines:List[str]):
    while (line := next(filelines, None)):
      try:
        match = next(m for rgx in rgxs if (m := rgx.search(line) ))
        if len(gd1 := match.groupdict()) == 6:
          dfdict:Dict = code_dfdict(**gd1)
          self.output_for_df.append(dfdict)
        elif len(gd2 := match.groupdict()) == 3:
          dfdict:Dict = code_dfdict(**gd2)
          prev_dfdict:Dict = self.output_for_df[-1]
          lst4linecont_entries:List = prev_dfdict['line_continuation']
          lst4linecont_entries.append(dfdict['line_continuation'])
      except StopIteration as exc:
        from pdb import set_trace as st
        from IPython.core.ultratb import ColorTB,VerboseTB
        print(ColorTB().text(*sys.exc_info()))
        debug_regex(rgxs,line,sys.exc_info())
        raise MyException(f"rgx{rgx}\nline{line}\nmatch{match}", bad_value=rgx)


def readfile(filename):
  lines = iterable_from_file(filename)
  return lines

def process_lines_for_df(filelines):
  processed_file = FileProcessor(filelines)
  data4df = processed_file.output_for_df
  return data4df

if __name__ == "__main__":
  for filename in filenames:
    filename = f"../{filename}"
    lines = readfile(filename)
    data4df = process_lines_for_df(lines)
    print(data4df)

