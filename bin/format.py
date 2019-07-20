import sys,re
from toolz.functoolz import compose_left, pipe
from dataclasses import dataclass, field
from pathlib import Path
from inspect import cleandoc
import traceback
from re_devkit import reDevKit
from pdb import set_trace as st
from typing import Dict, List, Any, Iterable
import fileinput
filename_prefixes, base = ["call", "code", "snoop"], "top.log"
filenames = [f"{prefix}.{base}" for prefix in filename_prefixes]
filehandles = [open(filename).readlines() for filename in filenames]
filelengths = [len(file) for file in filehandles]
callfile, codefile, snoopfile = filehandles
print(filenames)

# code: has the literal source code
# call: has the call level (aka the indentation level), perhaps
#  should create a "indent level" field
# snoop: has eztra variable info

@dataclass
class LogRow:
  line_number: int
  line_continuation: int
  indent_level: int
  filename: str
  event_kind: str
  source_code: str
  variables: Dict[str,Any] = field(default_factory=dict)

  def add_one(self):
    return self.x + 1

def fileline_generator(filename:str):
  with open(filename) as f:
    for line in f:
      yield(line)

gen_ca,gen_co,gen_sn = [fileline_generator(filename) for filename in filenames]

@dataclass
class CallLine:
  """example
[...]c/youtube-dl/youtube_dl/__init__.py:49    call         => _real_main(argv=None)
[...]c/youtube-dl/youtube_dl/__init__.py:51    line            if sys.platform == 'win32':
  """
  raw_string: str
  line_number: int
  line_continuation: field(default=0,init=False) # class var
  indent_level: int
  filename: str
  event_kind: str
  source_code: str

  def __post_init__(self):
    CallLine.initialize_attributes(self.raw_string)

  def str_builder1(self, pth1, pth2, pth3, preserved_ws, lineno, evt, data):
    pth = f"{pth1}/{pth2}/{pth3}"
    pws = f"{preserved_ws}"
    lno = int(f"{lineno}")
    evt = f"{evt}"
    dta = f"{data}"
    return pth,lno,evt,dta

  def str_builder2(self, evt, data):
    pws = " " * fmtdlines[-1][-1]
    elp = "..."
    evt = f"{evt}"
    dta = f"{data}"
    return evt,dta


  def initialize_attributes(self, line:str):
    rgx1 = RGX1
    rgx2 = RGX2
    match1 = rgx1.search(line)
    if match1:
      self.filename, self.line_number, self.event_kind, self.source_code = str_builder1(**match1.groupdict())
    elif (match2 := rgx2.search(line)):
      self.event_kind, self.source_code = str_builder2(**match.groupdict())
      CallLine.line_continuation =+ 1
    else:
      rgx1 = RGX1
      rgx2 = RGX2
      print(rgx1);print(rgx2)
      opencc(create(make_payload(rgx1, line)))
      opencc(create(make_payload(rgx2, line)))
      print(f"line: {line}\nmatch: {match}")
      print(f"err: {err}")
      print(f"exc_info: {sys.exc_info}")



def handle_codefile():
  RGX  = re.compile(
    r"(?P<home>yt_dl)/(?P<interpaths>.+[/])*(?P<filename>.*py)"
    r":(?P<lineno>\d{1,5})\s+(?P<event_kind>[a-z]+)\s+"
    r"(?P<data>[^\s].+)$"
  )
  RGX1 = re.compile(
        r"(?P<pth1>.*be_dl)/(?P<pth2>.*)?/?(?P<pth3>.*py):(?P<lineno>\d{1,5})"
        r"\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)"
        r"$")
  RGX2 = re.compile(
        r"\s+[.]{3}\s+(?P<evt>(return|exception) value):\s+(?P<data>.+)$"
    )
  RGX3 = re.compile(
    r"\s+[*]\s+(?P<data>def.*)$"
  )
  RGX4 = re.compile(
      r"(?P<uncooperativepth>\[(?:...)\].*)(?P<pth3>.*py):(?P<lineno>\d{1,5})"
      r"\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)"
      r"$")
  RGX5 = re.compile(
    r"\s+(?P<symbol>[|]|[*])(?P<preservedws>\s+)(?P<data>.*)"
  )

  def iterable_from_file(filename: str):
    with open(filename) as f:
      filelines = f.readlines()
    iterablines = iter(filelines)
    return iterablines

  def str_builder1(pth1, pth2, pth3, preserved_ws, lineno, evt, data):
    pth = f"{pth1}/{pth2}/{pth3}"
    pws = f"{preserved_ws}"
    lno = f"{lineno}"
    evt = f"{evt}"
    dta = f"{data}"
    rv, ln = f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}{dta}", len(f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}")
    return rv, ln

  def str_builder2(fmtdlines,evt, data):
    pws = " " * fmtdlines[-1][-1]
    elp = "..."
    evt = f"{evt}"
    dta = f"{data}"
    rv = f"{pws}{elp}{evt}: {dta}"
    return rv, pws

  def str_builder3(fmtdlines,data):
    pws = " " * fmtdlines[-1][-1]
    sta = "  *"
    dta = f"{data}"
    rv = f"{pws[:-1]}{sta}{dta}"
    return rv,pws

  def str_builder4(uncooperativepth, pth3, preserved_ws, lineno, evt, data):
    pth = f"{uncooperativepth}/{pth3}"
    pws = f"{preserved_ws}"
    lno = f"{lineno}"
    evt = f"{evt}"
    dta = f"{data}"
    rv, ln = f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}{dta}", len(f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}")
    return rv, ln

  def str_builder5(fmtdlines, symbol, preservedws, data):
    pws = 51
    sym = f"{symbol}"
    dta = f"{data}"
    rv = f"{pws}{sym}{preservedws}{dta}"
    return rv, preservedws

  def formatted_lines_from_iterable(iterablines: Iterable):
    fmtdlines = []
    rgx1 = RGX1
    rgx2 = RGX2
    rgx3 = RGX3
    rgx4 = RGX4
    rgx5 = RGX5
    while (line := next(iterablines, None)):
      match1 = rgx1.search(line)
      if match1:
        rv, ln = str_builder1(**match1.groupdict())
        fmtdlines.append([rv, ln])
      elif (match2 := rgx2.search(line)):
        rv, _ = str_builder2(fmtdlines,**match2.groupdict())
        fmtdlines.append([rv, _])
      elif (match3 := rgx3.search(line)):
        rv, _ = str_builder3(fmtdlines,**match3.groupdict())
        fmtdlines.append([rv,_])
      elif (match4 := rgx4.search(line)):
        rv, _ = str_builder4(**match4.groupdict())
        fmtdlines.append([rv,_])
      elif (match5 := rgx5.search(line)):
        rv, _ = str_builder5(fmtdlines, **match5.groupdict())
        fmtdlines.append([rv,_])
      else:
        st()
        redk = reDevKit()
        (redk.make_payload(rgx1, line)
            .create()
            .openbrowser())
        (redk.make_payload(rgx2, line)
            .create()
            .openbrowser())
        print(f"line: {line}\nmatch: {match}")
        print(f"err: {err}")
        print(f"exc_info: {sys.exc_info}")
    return fmtdlines

  def write_fmtdlines_to_file(fmtdlines: list):
    dirpath = Path(__file__).absolute().parent
    basepath = "/Users/alberthan/.pyenv/versions/3.8-dev/envs/vytd/src/youtube-dl/youtube_dl/logs"
    outfilepath = Path(basepath).joinpath("top.code.fmtd.log")
    with open(outfilepath, "w") as f:
      for line, pws in fmtdlines:
        f.write(line)
  try:
    compose_left(
      iterable_from_file,
      formatted_lines_from_iterable,
      write_fmtdlines_to_file
      )("code.top.log")
  except Exception as exc:
    exc_info = sys.exc_info()
    print(exc_info[2])
    print(traceback.print_exc())

# try:
#   handle_codefile()
# except:
#   exc = sys.exc_info()
#   print(34234234234)
#   print(exc)
#   print(traceback(exc.traceback())
#   # st()
# handle_codefile()
