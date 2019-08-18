import io, re, sys
import string
import pandas as pd
from toolz.functoolz import compose_left
from ast import literal_eval
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Tuple
from pdb import set_trace as st
from prettyprinter import pprint
from prettyprinter import cpprint
from dataclasses import dataclass
from collections import namedtuple
from row.parse_verbose_argvars import parse_argvars

def old_process_call_datum(call_datum):
    rgx1 = re.compile(r"^(?P<indent>\s*)(?P<function>=>\s[A-z0-9_]+)\((?P<argvars>.*)\)$")
    m1 = rgx1.match(call_datum)
    gd1 = m1.groupdict()
    indent,function,argvars = gd1.values()

    print(argvars,type(argvars))

    # rgx2 = re.compile(r"{[^}]+,[^]]+}|(,)") # 562
    # replacement = lambda m: "UniqStr" if m.group(1) else m.group(0)
    # replaced = rgx2.sub(replacement, argvars)
    # splitvars:List = replaced.split("UniqStr")
    # print(f"{splitvars=}")
    # print(f"{len(splitvars)=}")
    # for s in splitvars:
    #   print(s)
    #   print('--++--'*80+'\n\n'+'-**-'*20)
    # splitdct=dict([(elm.split('=',1)) for elm in splitvars]) # keys=info_dict,params
    # splitvals = list(splitdct.values())

    return splitvals

    rgx3 = re.compile(r"(\'[^\']+)(\[\.{3}\])[^\']+,")
    rplcmt = lambda m: r"\1[...]'" if m.group(1) else m.group(0)
    spltvls = [rgx3.sub(r"\1[...]',",splitvals[0])for v in splitvals]
    # re.sub(r"(\'[^\']+)(\[\.{3}\])[^\']+,",r"\1[...]',",splitvals[0])

# def pp(s) -> str:
#   stream = io.StringIO()
#   pprint(s,
#     stream=stream,
#     indent=2,
#     width=220,
#     # depth=_UNSET_SENTINEL, # default good
#     compact=True, # noef?
#     ribbon_width=220,
#     max_seq_len=920, # noef?
#     sort_dict_keys=True,
#     end='\n' # the last line
#   )
#   return stream.getvalue()

# def cp(s) -> str:
#   stream = io.StringIO()
#   cpprint(s,
#     stream=stream,
#     indent=2,
#     width=220,
#     # depth=_UNSET_SENTINEL, # default good
#     compact=True, # noef?
#     ribbon_width=220,
#     max_seq_len=920, # noef?
#     sort_dict_keys=True,
#     end='\n' # the last line
#   )
#   return stream.getvalue()



class FmtdCellData:
  def __init__(self,funcname):
    self.funcname = funcname

  def colorize(self,s) -> str:
    assert isinstance(s,str), s
    _stream = io.StringIO()
    try:
      litval = literal_eval(s)
      cpprint(litval,stream=_stream)
    except:
      cpprint(s,stream=_stream)
    rv = _stream.getvalue()
    _stream.close()
    return rv

class FmtdCallData(FmtdCellData):
  def __init__(self, funcname, keyslst, valslst):
    super().__init__(funcname)
    self.keyslst = keyslst
    self.valslst = valslst
    self.argnames = [k.strip().replace("'","") for k in self.keyslst]
    self.argvalues = [v.strip().replace("'","") for v in self.valslst]

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      d = {k:v for k,v in zip(self.argnames,self.argvalues)}
    if c or c == 'All':
      cz = self.colorize
      cd = {cz(k):cz(v) for k,v in zip(self.argnames,self.argvalues)}
    rv = (d,cd) if c == 'All' else d if not c else d
    return rv

class FmtdVerboseCallData(FmtdCellData):
  def __init__(self, funcname, keyslst, valslst):
    super().__init__(funcname)
    self.keyslst = keyslst
    self.valslst = valslst
    self.argnames = [k.strip().replace("'") for k in self.keyslst]
    self.argvalues = [v.strip().replace("'") for v in self.valslst]

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      d = {k:v for k,v in zip(self.argnames,self.argvalues)}
    if c or c == 'All':
      cz = self.colorize
      cd = {cz(k):cz(v) for k,v in zip(self.argnames,self.argvalues)}
    rv = (d,cd) if c == 'All' else d if not c else d
    return rv

class FmtdReturnData(FmtdCellData):
  def __init__(self, funcname, retvalslst):
    super().__init__(funcname)
    self.retvalslst = retvalslst

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      t =(self.funcname, self.retvalslst)
    if c or c == 'All':
      cz = self.colorize
      ct =(cz(self.funcname), cz(self.retvalslst))
    rv = (t,ct) if c == 'All' else t if not c else ct
    return rv
class FmtdExceptionData(FmtdCellData):
  def __init__(self, funcname, retvalslst):
    super().__init__(funcname)
    self.retvalslst = retvalslst

  def get_fmtd_str(self,c=False):
    """..c:: (True|False|'All')"""
    if not c or c == 'All':
      t =(self.funcname, self.retvalslst)
    if c or c == 'All':
      cz = self.colorize
      ct =(cz(self.funcname), cz(self.retvalslst))
    rv = (t,ct) if c == 'All' else t if not c else ct
    return rv

def process_verbose_row(row):
  print(1)

  def process_verbose_args(indented_function,argvars):
    keyslst,valslst = parsed = parse_argvars(argvars)
    fmtd_cell_data = FmtdVerboseCellData(function,keyslst,valslst)
    return fmtd_cell_data

  def process_regular_args(indented_function,argvars):
    parse_argvars_ez = lambda s: map(str.strip,s.split('='))
    print(argvars)
    keys,vals = parsed = parse_argvars_ez(argvars)
    # print(indent,function,argvars)
    keylst,vallst = [keys],colorize_string(vals,e=True) # keep consistent with verbose
    fmtd_cell_data = FmtdCellData(f"{indent}{function}",keylst,vallst)
    return fmtd_cell_data

  def classify_whether_argvars_verbose(indented_function,argvars):
    assert isinstance(argvars,str), argvars
    if len(argvars[1]) > 2000:
      return process_verbose_args(indented_function,argvars)
    else:
      return process_regular_args(indented_function,argvars)

  def prep_clean_classify_format(call_datum):
    # calrgx = re.compile(r"(?P<indented_function>^\s*=\>\s[<>A-z0-9_-]+)\((?P<argname>\.\d+)=(?P<argval><[^>]+>)\)$")
    calrgx = re.compile(r"(?P<indented_function>^\s*=\>\s[<>A-z0-9_-]+)\((?P<argvars>.*?)\)$")
    excrgx = re.compile(r"(?P<indented_function>^\s*\<=\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
    retrgx = re.compile(r"(?P<indented_function>^\s*\s!\s[<>A-z0-9_-]+):\s\[(?P<retvals>[^]]+)\]$")
    print(11)
    if '=>' in call_datum:
      print(22)
      #      call: '{COLOR}=>{NORMAL} {}({}{COLOR}{NORMAL}){RESET}\n'
      m = calrgx.match(call_datum)
      gd = m.groupdict()
      indented_function,argvars = gd.values()
      # print(f'{call_datum=}')
      # print(f"{indented_function=}")
      fmtd_cell_data = classify_whether_argvars_verbose(indented_function, argvars)
      return fmtd_cell_data
      # if m1 := calrgx1.match(call_datum):
      #   print('a')
      #   gd1 = m1.groupdict()
      #   indented_function,argvars = gd1.values()
      #   keyslst,valslst = [argname],[argval] # keep consistent with verbose
      #   fmtd_cell_data = FmtdCallData(indented_function,keyslst,valslst)
      #   return fmtd_cell_data
      #   print('b')
    elif '<=' in call_datum:
      print(33)
      #    return: '{COLOR}<={NORMAL} {}: {RESET}{}\n',
      if m2 := excrgx.match(call_datum):
        gd2 = m2.groupdict()
        indented_function,retvals = gd2.values()
        retvalslst = [retvals] # keep consistent with verbose
        fmtd_cell_data = FmtdReturnData(indented_function,retvalslst)
        return fmtd_cell_data
    elif ' !' in call_datum:
      print(44)
      # exception: '{COLOR} !{NORMAL} {}: {RESET}{}\n',
      if m3 := retrgx.match(call_datum):
        gd3 = m3.groupdict()
        indented_function,retvals = gd3.values()
        retvalslst = [retvals] # keep consistent with verbose
        fmtd_cell_data = FmtdExceptionData(indented_function,retvalslst)
        return fmtd_cell_data
    print(55)
    return fmtd_cell_data

  print(2)
  Index,filepath,line_number,symbol,event_kind,call_data,snoop_data = row
  call_datum = call_data[0]
  print(3)
  fmtd_data = prep_clean_classify_format(call_datum)
  print(4)
  assert isinstance(call_data,list), type(call_data)
  return fmtd_data

def initdf(initdf):
  initdf.iloc[10:14,0].filepath = 'extractor/__init__.py'
  initdf.iloc[14:16,:].filepath = 'downloader/__init__.py'
  initdflst = list(initdf.itertuples())
  idflm4 = initdflst[-4]
  # print(idflm4)
  return idflm4







def par(cd):
  call_data = row.call_data
  call_datum = call_data[0]
  rgx=re.compile(r"^(?P<indented_filename>\s+=\>\s[A-z0-9-_]+)\((?P<argvars>.*)\)$")
  m = rgx.match(call_datum)
  gd = m.groupdict()
  indented_filename, argvars = gd.values()
  argvars2 = re.sub(r" <youtube_dl.utils.DateRange object at 0x111ed26a0>,",
                    r" '<youtube_dl.utils.DateRange object at 0x111ed26a0>', ",
                    argvars)
  pargDvars = pargvars(argvars2)
  argvars3 = parse_argvars(argvars2)

cdsub1="{'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}"

eval(cdsub1)



  # import regex # if you like good times
  # intended to replace `re`, the regex module has many advanced
  # features for regex lovers. http://pypi.python.org/pypi/regex
  subject = 'Jane"" ""Tarzan12"" Tarzan11@Tarzan22 {4 Tarzan34}'
  regex = re.compile(r'{[^}]+}|"Tarzan\d+"|(Tarzan\d+)')
  # put Group 1 captures in a list
  matches = [group for group in re.findall(regex, subject) if group]

  ######## The six main tasks we're likely to have ########

  # Task 1: Is there a match?
  print("*** Is there a Match? ***")
  if len(matches)>0:
    print ("Yes")
  else:
    print ("No")

  # Task 2: How many matches are there?
  print("\n" + "*** Number of Matches ***")
  print(len(matches))

  # Task 3: What is the first match?
  print("\n" + "*** First Match ***")
  if len(matches)>0:
    print (matches[0])

  # Task 4: What are all the matches?
  print("\n" + "*** Matches ***")
  if len(matches)>0:
    for match in matches:
        print (match)

  # Task 5: Replace the matches
  def myreplacement(m):
      if m.group(1):
          return "Superman"
      else:
          return m.group(0)
  replaced = regex.sub(myreplacement, subject)
  print("\n" + "*** Replacements ***")
  print(replaced)

  # Task 6: Split
  # Start by replacing by something distinctive,
  # as in Step 5. Then split.
  splits = replaced.split('Superman')
  print("\n" + "*** Splits ***")
  for split in splits:
        print (split)




if __name__ == "__main__":
  # dfpath = Path('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/tfdf/idf.pkl')
  # idf = pd.read_pickle(dfpath)
  # row = initdf(idf)
  # call_data = row.call_data
  call_data = ["                        => get_suitable_downloader(info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}, params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': <youtube_dl.utils.DateRange object at 0x111ed26a0>, 'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None})"]
  call_datum = call_data[0]
  cd2 = "(info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}, params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': <youtube_dl.utils.DateRange object at 0x111ed26a0>, 'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None})"
  cd3 = "info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}, params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': <youtube_dl.utils.DateRange object at 0x111ed26a0>, 'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None})"
  kl,vl = parsed = par(call_datum)
  print(f"{len(kl)=}");print(f"{len(vl)=}")
  print(f"{kl=}")
  print(f"{len(kl[0])=}");print(f"{len(vl[0])=}")
  # print(parsed[0]) # ['', '>get_suitable_downloader']
  # print(parsed[1][0]
  # """
  # print(parsed[1][1])
  # """

  # """
  # st()
  # parsed = process_verbose_row(row)
  # # print(dir(parsed))
  # # print(parsed.funcname)
  # # print(parsed.fmtd_data)
  # # print(parsed.fmtd_datac)
  # print(parsed.args_keys)
  # info_dict, idval= parsed.get_arg('info_dict')
  # params, parval= parsed.get_arg('params')
  # print(idval)
  # print(parval)
  # info_dict, idval= parsed.get_arg('info_dict',color=True)
  # params, parval= parsed.get_arg('params',color=True)
  # print(idval)
  # print(parval)


cd1 = "info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}, params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': <youtube_dl.utils.DateRange object at 0x111ed26a0>, 'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None}"
