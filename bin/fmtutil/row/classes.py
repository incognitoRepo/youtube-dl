# // vscode-fold=1\
import re,io
import pandas as pd
from pathlib import Path
from itertools import repeat
from collections.abc import MutableMapping
from collections import UserList, UserString
from typing import NamedTuple, List, Dict, Iterable, Union
from youtube_dl.hunterconfig import CallEvent,LineEvent,ReturnEvent,ExceptionEvent
import pandas as pd
from dataclasses import dataclass, InitVar, field
from textwrap import TextWrapper
from pdb import set_trace as st
from prettyprinter import cpprint, pprint
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import Terminal256Formatter

EventKinds = Union[CallEvent,LineEvent,ReturnEvent,ExceptionEvent]

@dataclass
class DataCollections:
  evt_dcts: InitVar
  evt_dcts_df: pd.DataFrame = field(init=False)
  # dcts_grpd

  evts: List[EventKinds] = field(init=False)
  evts_df: pd.DataFrame = field(init=False)
  evts_grpd: Dict[str,List[EventKinds]] = field(init=False)

  def __post_init__(self, evt_dcts):
    """action.get_evt_dcts()"""
    self.evt_dcts = evt_dcts
    self.evt_dcts_df = pd.DataFrame(evt_dcts)

    self.evts = [e['hunter_event'] for e in evt_dcts]
    self.evts_df = pd.DataFrame([e.__dict__ for e in self.evts])

    self.create_evts_df(self.evts)
    self.group_by_evt_kind(self.evts)

  def create_evts_df(self,evts):
    """evts[0].__dataclass_fields__.keys()"""
    lods = []
    for e in evts:
      d = e.__dict__
      d.update({'hunter_monostr':str(e)})
      lods.append(d)
    df = pd.DataFrame(lods)
    self.evts_df = df

  def group_by_evt_kind(self,evts):
    cll_lst,lne_lst,ret_lst,exc_lst = [],[],[],[]
    d = {
      "CallEvent": cll_lst,
      "LineEvent": lne_lst,
      "ReturnEvent": ret_lst,
      "ExceptionEvent": exc_lst,
    }
    for e in evts:
      d[type(e).__name__].append(e)
    self.evts_grpd = d

  def __str__(self):
    join = lambda lst: "\n".join(lst)
    srv = [s0:=[],s1:=[],s2:=[],s3:=[]]
    self.evts
    s0 += (
      f" ..evt_dcts: List[Dict] (len={len(self.evt_dcts)})",
      f"      :keys: ",
      f"({', '.join(list(self.evt_dcts[0].keys()))})"
    )
    s1 += (
      f"     ..evts: List[EventKinds] (len={len(self.evt_dcts_df)})",
      f":EventKinds: Union[CallEvent,LineEvent,ReturnEvent,ExceptionEvent]",
      f"      :keys: ",
      f"({', '.join(list(self.evts[0].__dict__.keys()))})"
    )
    s2 += (
      f"  ..evt_dcts_df: pd.DataFrame (len={len(self.evt_dcts_df)})",
      f"   :columns: ",
      f"{self.evt_dcts_df.columns}"
    )
    s3 += (
      f"  ..evts_df: pd.DataFrame (len={len(self.evts_df)})",
      f"   :columns: ",
      f"{self.evts_df.columns}"
    )
    srvj = join(map(join,srv))
    return srvj

class Parsed:
  def clrz(self, s,t):
    blk,red,grn,ylw,blu,mag,cyn,wht = 30,31,32,33,34,35,36,37
    reset = "\x1b[0m"
    if t == "sym":
      new_s = f"\x1b[0;{blu}m{s}{reset}"
    elif t == "funk":
      new_s = f"\x1b[0;{red}m{s}{reset}"
    elif t == "anm":
      new_s = f"\x1b[0;{ylw}m{s}{reset}"
    elif t == "avl":
      new_s = f"\x1b[0;{grn}m{s}{reset}"
    elif t == "arn":
      new_s = f"\x1b[0;{mag}m{s}{reset}"
    return new_s

  def cpp(self,s) -> str:
    stream = io.StringIO()
    cpprint(s,
      stream=stream,
      indent=2,
      width=220,
      # depth=_UNSET_SENTINEL, # default good
      compact=True, # noef?
      ribbon_width=220,
      max_seq_len=920, # noef?
      sort_dict_keys=True,
      end='\n' # the last line
    )
    stream_value = stream.getvalue()
    cleaned_value = stream_value.strip()
    cleaned_value = cleaned_value.replace("'","")
    return cleaned_value

  def pp(self,s) -> str:
    stream = io.StringIO()
    pprint(s,
      stream=stream,
      indent=2,
      width=220,
      # depth=_UNSET_SENTINEL, # default good
      compact=True, # noef?
      ribbon_width=220,
      max_seq_len=920, # noef?
      sort_dict_keys=True,
      end='\n' # the last line
    )
    stream_value = stream.getvalue()
    cleaned_value = stream_value.strip()
    cleaned_value = cleaned_value.replace("'","")
    return cleaned_value

@dataclass
class ShortStringDict(Parsed):
  def __init__(self,dct):
    self._x = dct

  @property
  def x(self):
    """I'm the 'x' property."""
    return self._x

  @x.setter
  def x(self, value):
    assert isinstance(value, property), type(value)
    self._x = value

  @x.deleter
  def x(self):
    del self._x

  def get_cstr(self):
    cstr = self.cpp(self._x)
    return cstr

  def get_str(self):
    ncstr = self.pp(self._x)
    return ncstr

  def __len__(self):
    return len(self._x)

  def __str__(self,c=False,v=False):
    if not c and not v:
      ncstr = self.get_str()
      ncstr2 = f"{ncstr[:10]}..."
      return ncstr2
    if c and v:
      cstr = self.get_cstr()
      return cstr
    if c:
      cstr = self.get_str()
      cstr2 = f"{cstr[:10]}..."
      return cstr2

@dataclass
class ParsedJSON(Parsed):
  symbol: str = None
  funk: str = None
  argdct: Dict
  _argdct: ShortStringDict = field(init=False, repr=False)

  @property
  def argdct(self) -> Dict:
    """I'm the 'argdct' property."""
    return self._argdct

  @argdct.setter
  def argdct(self, argdct: Dict):
    self._argdct = ShortStringDict(argdct)
    assert isinstance(argdct, property) or isinstance(argdct, dict), type(argdct)

  @argdct.deleter
  def argdct(self):
    del self._argdct

  def get_funcname(self,c=False):
    """I'm the 'string' property."""
    if c:
      s = f"{self.clrz(self.symbol,t='sym')} {self.clrz(self.funk,t='funk')}"
    else:
      s = f"{self.symbol} {self.funk}"
    return s

@dataclass
class ParsedHTML(Parsed):
  symbol: str = None
  funk: str = None
  argdct: Dict
  _argdct: ShortStringDict = field(init=False, repr=False)

  @property
  def argdct(self) -> Dict:
    """I'm the 'argdct' property."""
    return self._argdct

  @argdct.setter
  def argdct(self, argdct: Dict):
    self._argdct = ShortStringDict(argdct)
    assert isinstance(argdct, property) or isinstance(argdct, dict), type(argdct)

  @argdct.deleter
  def argdct(self):
    del self._argdct

  def get_funcname(self,c=False):
    """I'm the 'string' property."""
    if c:
      s = f"{self.clrz(self.symbol,t='sym')} {self.clrz(self.funk,t='funk')}"
    else:
      s = f"{self.symbol} {self.funk}"
    return s

  def get_args(self,c=False):
    if not self.argname:
      return "None"
    else:
      if c:
        s = f"{self.clrz(self.argname,t='anm')} {self.clrz(self.argval,t='avl')}"
      else:
        s = f"{self.argname} {self.argval}"
    return s

@dataclass
class ParsedTuple(Parsed):
  symbol: str = None
  funk: str = None
  start: str = None
  stop: str = None
  argname: str = None
  argdct: Dict
  _argdct: ShortStringDict = field(init=False, repr=False)

  @property
  def argdct(self) -> Dict:
    """I'm the 'argdct' property."""
    return self._argdct

  @argdct.setter
  def argdct(self, argdct: Dict):
    self._argdct = ShortStringDict(argdct)
    assert isinstance(argdct, property) or isinstance(argdct, dict), type(argdct)

  @argdct.deleter
  def argdct(self):
    del self._argdct

  def get_funcname(self,c=False):
    """I'm the 'string' property."""
    if c:
      s = f"{self.clrz(self.symbol,t='sym')} {self.clrz(self.funk,t='funk')}"
    else:
      s = f"{self.symbol} {self.funk}"
    return s

  def get_argname(self,c=False):
    if c:
      s = f"{self.clrz(self.argname,t='arn')}"
    else:
      s = f"{self.argname}"
    return s

  def get_argdct(self,c=False):
    if c:
      s = self._argdct.get_cstr()
    else:
      s = self._argdct.get_str()
    return s

  def __iter__(self):
    idr = iter([self.start,self.stop,self._argdct])
    yield next(idr)

  def __len__(self):
    return len(self._argdct)

  def __str__(self):
    symbol,funcname = self.symbol,self.funk
    start,stop,SSDict = self.start,self.stop,self._argdct
    wrapper = TextWrapper(subsequent_indent="  * ")
    w = wrapper.wrap(str(SSDict)) # TODO!! WAS THIS THE CHANGE?
    f = wrapper.fill(str(SSDict)) # TODO!! WAS THIS THE CHANGE?
    s = f"ParsedTuple: {symbol=} {funcname=} {start=}, {stop=}\n  {SSDict}\n"
    return s

  def __repr__(self):
    argname,symbol,funcname = self.argname,self.symbol,self.funk
    start,stop,SSDict = self.start,self.stop,self._argdct
    SSDct = str(SSDict)
    s = f"ParsedTuple:\n {symbol=} {funcname=} {start=}, {stop=}\n  {argname=} {SSDct}\n"
    return s

@dataclass
class VerboseList(Parsed):
    rgxf = re.compile(r"(?P<symbol>(\<=|=\>| !)) (?P<funk>[A-z][A-z-0-9-_]*)")
    raw_tuple: InitVar

    symbol: str = None
    funk: str = None
    argname: str = None
    argval: str = None

    def __post_init__(self, raw_tuple):
      if raw_tuple is not None:
        symbol, funcname = raw_tuple[0].rsplit(" ",1)
        assert isinstance(raw_tuple[1],list), raw_tuple[1]
      self.symbol,self.funk = symbol, funcname
      try:
        self.argname,self.argval = argname, raw_tuple[1]
      except:
        assert self.argname == None
        self.argval = raw_tuple[1]

    def __iter__(self):
      idr = iter([self.argval])
      yield next(idr)

    def __len__(self):
      return len(self.argval)

    def __getitem__(self, item):
        return self.argval[item]

    def cpp(self,s) -> str:
      stream = io.StringIO()
      cpprint(s,
        stream=stream,
        indent=2,
        width=220,
        # depth=_UNSET_SENTINEL, # default good
        compact=True, # noef?
        ribbon_width=220,
        max_seq_len=920, # noef?
        sort_dict_keys=True,
        end='\n' # the last line
      )
      return stream.getvalue()

    def pp(self,s) -> str:
      stream = io.StringIO()
      pprint(s,
        stream=stream,
        indent=2,
        width=220,
        # depth=_UNSET_SENTINEL, # default good
        compact=True, # noef?
        ribbon_width=220,
        max_seq_len=920, # noef?
        sort_dict_keys=True,
        end='\n' # the last line
      )
      return stream.getvalue()

    def get_funcname(self,c=False):
      """I'm the 'string' property."""
      if c:
        s = f"{self.clrz(self.symbol,t='sym')} {self.clrz(self.funk,t='funk')}"
      else:
        s = f"{self.symbol} {self.funk}"
      return s

    def get_args(self,c=False):
      if c:
        if self.argname:
          s = f"{self.clrz(self.argname,t='anm')} {self.cpp(self.argval)}"
        else:
          s = self.cpp(self.argval)
      else:
        if self.argname:
          s = f"{self.argname} {self.pp(self.argval)}"
        else:
          s = self.pp(self.argval)
      return s

@dataclass
class LineEvent(Parsed):
  line_nc: str = None
  # calculated fields
  line_c: str = field(init=False)

  def __post_init__(self):
    stream = io.StringIO()
    print(highlight(self.line_nc, PythonLexer(), Terminal256Formatter()),file=stream,flush=True)
    self.line_c = stream.getvalue()
    stream.close()

class SimpleFormatters():
  def single_arg(self,e):
    pass

@dataclass
class SimpleFunkWithArgs(Parsed):
    """Represents a 2-length tuple, a single cell of parsed call_data
    This class is a catchall call for rows that are not in other classes.

    Arguments:a
        funk {[str]} = symbol, white_space, funcname | comprehension ;
          symbol = "=>" | "<=" | " !" ;
          white_space = ? white_space characters ? ;
          funcname = re.compile(r"[A-z_][A-z0-9-_]*")
          comprehension = "<", re.compile(r"(list|dict)comp"), ">"
        args {[str]} = argname, "=", argvalue
          argname = re.compile(r"^[A-z_][A-z0-9-_]*")
          argvalue = re.compile(r"[A-z0-9-_]+")
    """
    bracket_symbols = ["{","[","("]
    rgxf = re.compile(r"(?P<symbol>(\<=|=\>| !)) (?P<funk>[A-z][A-z-0-9-_]*)")
    raw_tuple: InitVar
    raw: str = ""

    symbol: str = None
    funk: str = None
    argname: str = None
    argval: str = None

    def __post_init__(self, raw_tuple):
      self.raw = str(raw_tuple)
      if raw_tuple is not None:
        symbol, funcname = raw_tuple[0].rsplit(" ",1)
        if "=" in raw_tuple[1]:
          argname,argval = raw_tuple[1].split("=",1)
        else:
          # assert raw_tuple[1] == "None", raw_tuple[1]
          argname,argval = "None", raw_tuple[1]
      self.symbol,self.funk = symbol, funcname
      try:
        self.argname,self.argval = argname, argval
      except:
        assert self.argname == None

    def get_funcname(self,c=False):
      """I'm the 'string' property."""
      if c:
        s = f"{self.cpp(self.symbol)} {self.cpp(self.funk)}"
      else:
        s = f"{self.pp(self.symbol)} {self.pp(self.funk)}"
      return s

    def simple_switchboard(self):
      def zero_args():
        # return not (cd.argval_exists() and cd.argname_exists())
        return not self.argval_exists()
      def only_one_arg():
        return ',' not in x # comma has the proxy for single arg
      if zero_args():
        # there are no args return nothing
        return "()"
      # from this point: we are sure we are returning something
      # self.argval exists
      elif only_one_arg():
        return "\n".join(self.raw)
      elif 'None' in self.argval:
        pass

    def argval_exists(self):
      return self.argval and self.argval != 'None'

    def argname_exists(self):
      return self.argname and self.argname != 'None'

    def get_args(self,c=False):
      # no argname but argval
      # argname and argval
      # # argval is a collection
      def errsub(self,un_eval_able): return re.sub(
        r"(?P<left>^[^<]+)(?P<unquoted><[^>]+>)(?P<right>.+)$",
        r"\g<left>'\g<unquoted>'\g<right>",
        un_eval_able)
      if not self.argval_exists():
        return ''
      elif not self.argname_exists():
        argname = ''
        str1 = self.argval
      else:
        argname = self.argname
        str1 = self.argval
      try:
        argval = eval(str1)
      except SyntaxError:
        # invalid syntax
        str2 = errsub(str1)
        argval = eval(str2)
      if c:
        if argname:
          s = f"{self.cpp(argname)} {self.cpp(argval)}"
        else:
          s = f"{self.cpp(argval)}"
      else:
        if argname:
          s = f"{self.pp(argname)} {self.pp(argval)}"
        else:
          s = f"{self.pp(argval)}"
      st()
      return s

@dataclass
class SymbolList(UserList):
  """symbols for metainfo
  header: math alphanumeric symbols
  lines_indictor: (supplemental) math operators
  first_line: misc technical symbols
  """
  header: str
  lines_indicator: str
  first_line: str

  def __iter__(self):
    l = [self.header,self.lines_indicator,self.first_line]
    i = iter(l)
    return i

SymbolTier1,SymbolTier2 = SymbolList,SymbolList

@dataclass
class ArrowList(UserList):
  """arrow symbols
  args1: arrows "\u21B3"
  args2: arrows "\u21AA"
  placeholder: ??
  """
  args1: str
  args2: str
  placeholder: str

  def __iter__(self):
    l = [self.args1,self.args2,self.placeholder]
    i = iter(l)
    return i

@dataclass
class FormatSymbols:
  symbols_map = {
           'Tier1':    SymbolTier1(*["¹","¹","¹"]),
           'Tier2':    SymbolTier2(*["²","²","²"]),
      'MutableStr':     SymbolList(*["𝑚","≖","⌕"]),
      'UserString':     SymbolList(*["𝑢","∺","⌖"]),
  'SimpleFunkWithArgs': SymbolList(*["𝑠","≻","⌙"]),
      'ParsedJSON':     SymbolList(*["𝑗","≽","⌮"]),
      'ParsedHTML':     SymbolList(*["𝒉","⊍","⌞"]),
      'LineEvent':      SymbolList(*["𝑙","⋽","⌯"]),
      'VerboseList':    SymbolList(*["𝐿","≞","⍆"]),
      'ParsedTuple':    SymbolList(*["𝐷","∿","⌭"]),
         'Bullets':                 ["•"],
         'Arrows':      SymbolList(*["↳","↪","?"]),
         'Call'  :      "𝑐",
         'Return':      "𝑟",
  }
  def add_ws(self,sym,indent=0):
    """ws: whitespace"""
    num_tiers = 2
    relative_idt = indent + num_tiers
    whitespace = "\u0020"
    if sym:
      relative_idt -= 1
      ws = relative_idt*whitespace
      retstr = f"{ws}{sym}"
    else:
      ws = relative_idt*whitespace
      retstr = f"{ws}"
    return retstr

  def get_Tier(self,tier_lvl):
    tier_key = f"Tier{tier_lvl}"
    t1,t2,t3 = self.symbols_map[tier_key]
    return t1,t2,t3

  def get_Tier1(self):
    """Tier1 Symbol
    Whitespace for tiers are absolute
    and are added manually"""
    t1,t2,t3 = self.symbols_map['Tier1']
    return t1,t2,t3

  def get_Tier2(self):
    """Tier2 Symbol
    Whitespace for tiers are absolute
    and are added manually"""
    t1,t2,t3 = ts = self.symbols_map['Tier2']
    t1,t2,t3 = [f" {t}" for t in ts]
    return t1,t2,t3

  def get_MS(self):
    """MutableStr ≡"""
    s1,s2,s3 = ss = self.symbols_map['MutableStr']
    return s1,s2,s3

  def get_US(self,presym=None):
    """UserString 𝑢"""
    s1,s2,s3 = ss = self.symbols_map['UserString']
    if presym:
      s1,s2,s3 = [f"{presym}{s}" for s in ss]
    idts = [2,2,2]
    us1,us2,us3 = uss = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    return us1,us2,us3

  def get_SFWA(self,presym=None):
    """SimpleFunkWithArgs
    is used to create the symbols passed to structure1
    returns sf1,sf2"""
    s1,s2,s3 = ss = self.symbols_map['SimpleFunkWithArgs']
    if presym:
      s1,s2,s3 = [f"{presym}{s}" for s in ss]
    idts = [3,2,2]
    sf1,sf2,sf3 = sfs = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    return sf1,sf2,sf3

  def get_PJ(self,presym=None):
    """ParsedJSON
    is used to create the symbols passed to structure2
    returns pj1,pj2"""
    s1,s2,s3 = ss = self.symbols_map['ParsedJSON']
    if presym:
      s1,s2,s3 = [f"{presym}{s}" for s in ss]
    idts = [1,2,2]
    pj1,pj2,pj3 = pjs = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    return pj1,pj2,pj3

  def get_PH(self,presym=None):
    """ParsedHTML
    is used to create the symbols passed to structure2
    returns ph1,ph2"""
    s1,s2,s3 = ss = self.symbols_map['ParsedHTML']
    if presym:
      s1,s2,s3 = [f"{presym}{s}" for s in ss]
    idts = [1,2,2]
    ph1,ph2,ph3 = phs = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    return ph1,ph2,ph3

  def get_LE(self):
    """LineEvent & Header"""
    s1,s2,s3 = ss = self.symbols_map['LineEvent']
    idts = [2,3,3]
    le1,le2,le3 = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    return le1,le2,le3

  def get_VL(self,nargs:int):
    """VerboseList"""
    s1,s2,s3 = ss = self.symbols_map['VerboseList']
    idts = [2,2,2]
    vl1,vl2,vl3 = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    vl1 = self.add_ws(sym=s1,indent=2)
    vl2 = iter([s2] + list(repeat(s3,nargs)))
    return vl1,vl2

  def get_PT(self,nargs:int):
    """ParsedTuple"""
    s1,s2,s3 = ss = self.symbols_map['ParsedTuple']
    idts = [2,2,3]
    pt1,pt2,pt3 = [self.add_ws(s,i) for s,i in zip(ss,idts)]
    pt1 = self.add_ws(sym=s1,indent=2)
    pt2 = iter([pt2] + list(repeat(pt3,nargs)))
    return pt1,pt2

  def get_BLTS(self):
    blt1 = self.symbols_map['Bullets']
    return blt1

  def get_Arrows(self):
    a1,a2,a3 = arrs = self.symbols_map['Arrows']
    return a1,a2,a3

  def get_call(self):
    return self.symbols_map["Call"]

  def get_return(self):
    return self.symbols_map["Return"]

class MutableStr(UserString):
  def modify_inplace(self,s):
    self.data = self.data + s

if __name__ == "__main__":
  info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}
  params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': '<youtube_dl.utils.DateRange object at 0x111ed26a0>',  'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None}
  prsdtpl = ParsedTuple()
  prsdtpl.strt = 2
  prsdtpl.stop = 128
  prsdtpl.string = info_dict
  print(prsdtpl)

