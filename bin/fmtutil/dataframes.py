import pandas as pd
import numpy as np
rgxs = [
  re.compile(
      r"(?P<home>yt_dl)/(?P<interpaths>.+[/]){0,2}(?P<filename>.*py)"
      r":(?P<lineno>\d{1,5})\s+(?P<event_kind>[a-z]+)\s+"
      r"(?P<data>[^\s].+)$"
  ),
  re.compile(
      r"\s+"
      r"(?P<symbol>[|]|[*]|[.]{3})\s+"
      r"(?P<data>[^\s].+)$"
  )
]

@dataclass
class Capfile:
  """example
[...]c/youtube-dl/youtube_dl/__init__.py:49    call         => _real_main(argv=None)
[...]c/youtube-dl/youtube_dl/__init__.py:51    line            if sys.platform == 'win32':
  """
  raw_string: str
  line_number: int
  line_continuation: List[str] = field(default_factory=list,init=False) # class var
  indent_level: int
  filename: str
  event_kind: str
  source_code: str

  def __post_init__(self):
    CallLine.initialize_attributes(self.raw_string)



df = pd.DataFrame()
# A structured array
my_array = np.array(dtype=([('foo', int), ('bar', float)]))
# Print the structured array
_____(my_array['foo'])

# A record array
my_array2 = my_array.view(np.recarray)
# Print the record array
_____(my_array2.foo)

dtypes = np.dtype([
          ('filename', str),
          ('line_number', int),
          ('line_continuation', tuple),
          ('indent_level', int),
          ('event_kind', str),
          ('source_data', str)
          ])
data = np.empty(0, dtype=dtypes)
df = pd.DataFrame(data)
df.add(['qewr',3,43.6])

d1 = {
    "filename": 'qwer',
    "line_number": 23,
    "line_continuation": None, #tuple(symbol,source_data)
    "indent_level": None,
    "event_kind": 'call',
    "source_data": "my_array = np.array(dtype=([('foo', int), ('bar', float)]))"
  }
d2 ={
    "filename": None,
    "line_number": None,
    "line_continuation": ("[...]","self.prepare_lines_for_df(self.raw_input)"), #tuple(symbol,source_data)
    "indent_level": None,
    "event_kind": None,
    "source_data": None
  }
l1 = [d1,d2]
df = pd.DataFrame(l1)

def formatted_lines_from_iterable(iterablines: Iterable):
  def str_builder1(pth1, pth2, pth3, lineno, evt, data):
    pth = f"{pth1}/{pth2}/{pth3}"
    lno = f"{lineno}"
    evt = f"{evt}"
    dta = f"{data}"
    rv, ln = f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt:9} {dta}", len(f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt:9} ")
    return rv, ln

  def str_builder2(fmtdlines,evt, data):
    pws = " " * fmtdlines[-1][-1] #TODO
    elp = "..."
    evt = f"{evt}"
    dta = f"{data}"
    rv = f"{pws}{elp}{evt}: {dta}"
    return rv, pws
  fmtdlines = []

  #   match1 = rgx1.search(line)
  #   if match1:
  #     rv, ln = str_builder1(**match1.groupdict())
  #     fmtdlines.append([rv, ln])
  #   elif (match2 := rgx2.search(line)):
  #     rv, _ = str_builder2(fmtdlines,**match2.groupdict())
  #     fmtdlines.append([rv, _])
  #   else:
  #     st()
  #     redk = reDevKit()
  #     (redk.make_payload(rgx1, line)
  #         .create()
  #         .openbrowser())
  #     (redk.make_payload(rgx2, line)
  #         .create()
  #         .openbrowser())
  #     print(f"line: {line}\nmatch: {match}")
  #     print(f"err: {err}")
  #     print(f"exc_info: {sys.exc_info}")
  # return fmtdlines
