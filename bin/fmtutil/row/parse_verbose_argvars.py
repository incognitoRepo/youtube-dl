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
from dataclasses import dataclass
from textwrap import TextWrapper
from collections.abc import MutableMapping
from typing import NamedTuple
from .classes import ParsedTuple, ShortStringDict

def _parse_argvars() -> Tuple:
  firstflag = True
  kstr,vstr = "",""
  keyslst,valslst = [], []
  opnbrc,opnbrkt,opnparen = [],[],[]

  def entry(argvars:str) -> Tuple[List,List]:
    parsed = parse_argvars(argvars)
    return parsed

  def check_start_iterable_symbol(char):
    nonlocal kstr,vstr
    nonlocal opnbrc,opnbrkt,opnparen
    if char == "{":
      vstr += "{"
      opnbrc.append("{")
      return True
    elif char == "[":
      vstr += "["
      opnbrkt.append("[")
      return True
    elif char == "(":
      vstr += "("
      opnparen.append("(")
      return True
    return False

  def check_stop_iterable_symbol(char):
    nonlocal kstr,vstr
    nonlocal opnbrc,opnbrkt,opnparen
    if char == "}":
      vstr += "}"
      opnbrc.pop()
      return True
    elif char == "]":
      vstr += "]"
      opnbrkt.pop()
      return True
    elif char == ")":
      vstr += ")"
      opnparen.pop()
      return True
    return False

  def is_val_char():
    nonlocal opnbrc,opnbrkt,opnparen
    """if any open symbol list has a value, char is valchar"""
    return any([opnbrc,opnbrkt,opnparen]) # no lst has a value

  def is_key_char():
    nonlocal opnbrc,opnbrkt,opnparen
    """if all lists are empty, char=keychar"""
    return not any([opnbrc,opnbrkt,opnparen]) # no lst has a value

  def is_equals_symbol(char):
    return char == "="

  def parse_argvars(argvars):
    nonlocal kstr,vstr
    nonlocal keyslst,valslst
    nonlocal opnbrc,opnbrkt,opnparen
    for char in argvars:
      is_iter_start = check_start_iterable_symbol(char)
      if is_iter_start:
        continue
      is_iter_stop  = check_stop_iterable_symbol(char)
      if is_iter_stop:
        continue
      is_equalsign = is_equals_symbol(char)
      if is_equalsign and not is_val_char():
        continue
      elif is_val_char():
        assert len(keyslst) >= 1, keyslst
        vstr += char
        continue
      elif is_key_char():
        if char in "," or char in " ":
          continue
        assert char in string.ascii_letters+string.digits+"_<>", char
        if vstr:
          vstr = re.sub(r" <youtube_dl.utils.DateRange object at 0x111ed26a0>,",
            r" '<youtube_dl.utils.DateRange object at 0x111ed26a0>', ",
            vstr)
          valslst.append(vstr)
          vstr = ""
        kstr += char
        continue
      else:
        raise
    if vstr: valslst.append(vstr)
    return keyslst,valslst
  sns = SimpleNamespace(entry=entry)
  return sns.entry

parse_argvars = _parse_argvars()

def pargvars(argvars2, prsdtpl, strt=0, rvlst=None, first=False):
  if first:
    argname, argvars = argvars2.split('=',1)
    prsdtpl.argname = argname
    first = False
  rvlst = [] if not rvlst else rvlst
  nest = []
  strt = argvars2.index('{')
  stop = argvars2.rindex('}') + 1 # +1 needed to incl '}'
  prsdtpl.start = strt
  i:int = strt if strt else 0
  for i in range(strt,stop):
    char = argvars2[i]
    if char == '}':
      nest.pop()
      if not nest:
        prsdtpl.stop = i+1 # +1 needed!
        argvars3 = argvars2[strt:prsdtpl.stop]
        d = eval(argvars3)
        assert isinstance(d,dict), d
        prsdtpl.argdct = d
        break
      continue
    if char == '{':
      nest.append('{')
      continue
  rvlst.append(prsdtpl)
  if '=' in argvars2[i:stop]:
    assert argvars2[i] == '}', argvars2[i]
    comma_sep_i = argvars2.find(", ")
    assert comma_sep_i - i < 10, f"{i=}, {comma_sep_i=}\n{argvars2[i-5:comma_sep_i+5]}"
    i += 3
    return pargvars(argvars2=argvars2[i:stop],
        prsdtpl=ParsedTuple(symbol=prsdtpl.symbol,funk=prsdtpl.funk),
        strt=i,
        rvlst=rvlst,
        first=True)
  else:
    print(rvlst)
    return tuple(rvlst)

if __name__ == "__main__":
  call_data = ["                        => get_suitable_downloader(info_dict={'id': 'ph5d0835267370a', 'uploader': 'SativaSlimedYou', 'upload_date': '20190618', 'title': 'Houston tx sloppy toppy', 'thumbnail': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'duration': 111, 'view_count': 364075, 'like_count': 1715, 'dislike_count': 232, 'comment_count': 69, 'formats': [{'url': 'https://ev.phncdn.com/videos/201906/18/230034052/240P_400K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=40k&burst=1000k&ip=73.11.206.225&hash=CbQ9q9ula6Uwct%2FZGqsGdkd2IxA%3D', 'format_id': '240p', 'height': 240, 'tbr': 400, 'ext': 'mp4', 'format': '240p - 240p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/480P_600K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=65k&burst=1000k&ip=73.11.206.225&hash=2qbRkVXoYpXQHCfufG22vbIpXoI%3D', 'format_id': '480p', 'height': 480, 'tbr': 600, 'ext': 'mp4', 'format': '480p - 480p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}, {'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}}], 'age_limit': 18, 'tags': ['sloppy head', 'head', 'blowjob', 'ebony', 'milf', 'amateur', 'bbc', 'big dick', 'cock sucking', 'ball licking', 'deepthroat', 'mom'], 'categories': ['Amateur', 'Big Dick', 'Blowjob', 'HD Porn', 'MILF'], 'subtitles': {}, 'extractor': 'PornHub', 'webpage_url': 'https://www.pornhub.com/view_video.php?viewkey=ph5d0835267370a', 'webpage_url_basename': 'view_video.php', 'extractor_key': 'PornHub', 'playlist': None, 'playlist_index': None, 'thumbnails': [{'url': 'https://ci.phncdn.com/videos/201906/18/230034052/original/(m=eaAaGwObaaaa)(mh=dnIWa2p3McEp083H)5.jpg', 'id': '0'}], 'display_id': 'ph5d0835267370a', 'requested_subtitles': None, 'url': 'https://ev.phncdn.com/videos/201906/18/230034052/720P_1500K_230034052.mp4?validfrom=1565733286&validto=1565740486&rate=83k&burst=1000k&ip=73.11.206.225&hash=DfQ63H0YGiDIZbxze1tBM4Hu%2BpY%3D', 'format_id': '720p', 'height': 720, 'tbr': 1500, 'ext': 'mp4', 'format': '720p - 720p', 'protocol': 'https', 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3588.0 Safari/537.36', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-us,en;q=0.5'}, 'fulltitle': 'Houston tx sloppy toppy', '_filename': 'Houston tx sloppy toppy-ph5d0835267370a.mp4'}, params={'nocheckcertificate': False, 'usenetrc': False, 'username': None, 'password': None, 'twofactor': None, 'videopassword': None, 'ap_mso': None, 'ap_username': None, 'ap_password': None, 'quiet': False, 'no_warnings': False, 'forceurl': False, 'forcetitle': False, 'forceid': False, 'forcethumbnail': False, 'forcedescription': False, 'forceduration': False, 'forcefilename': False, 'forceformat': False, 'forcejson': False, 'dump_single_json': False, 'simulate': False, 'skip_download': False, 'format': None, 'listformats': None, 'outtmpl': '%(title)s-%(id)s.%(ext)s', 'autonumber_size': None, 'autonumber_start': 1, 'restrictfilenames': False, 'ignoreerrors': False, 'force_generic_extractor': False, 'ratelimit': None, 'nooverwrites': False, 'retries': 10, 'fragment_retries': 10, 'skip_unavailable_fragments': True, 'keep_fragments': False, 'buffersize': 1024, 'noresizebuffer': False, 'http_chunk_size': None, 'continuedl': True, 'noprogress': False, 'progress_with_newline': False, 'playliststart': 1, 'playlistend': None, 'playlistreverse': None, 'playlistrandom': None, 'noplaylist': False, 'logtostderr': False, 'consoletitle': False, 'nopart': False, 'updatetime': True, 'writedescription': False, 'writeannotations': False, 'writeinfojson': False, 'writethumbnail': False, 'write_all_thumbnails': False, 'writesubtitles': False, 'writeautomaticsub': False, 'allsubtitles': False, 'listsubtitles': False, 'subtitlesformat': 'best', 'subtitleslangs': [], 'matchtitle': None, 'rejecttitle': None, 'max_downloads': None, 'prefer_free_formats': False, 'verbose': False, 'dump_intermediate_pages': False, 'write_pages': False, 'test': False, 'keepvideo': False, 'min_filesize': None, 'max_filesize': None, 'min_views': None, 'max_views': None, 'daterange': <youtube_dl.utils.DateRange object at 0x111ed26a0>, 'cachedir': None, 'youtube_print_sig_code': False, 'age_limit': None, 'download_archive': None, 'cookiefile': None, 'prefer_insecure': None, 'proxy': None, 'socket_timeout': None, 'bidi_workaround': None, 'debug_printtraffic': False, 'prefer_ffmpeg': None, 'include_ads': None, 'default_search': None, 'youtube_include_dash_manifest': True, 'encoding': None, 'extract_flat': False, 'mark_watched': False, 'merge_output_format': None, 'postprocessors': [], 'fixup': 'detect_or_warn', 'source_address': None, 'call_home': False, 'sleep_interval': None, 'max_sleep_interval': None, 'external_downloader': None, 'list_thumbnails': False, 'playlist_items': None, 'xattr_set_filesize': None, 'match_filter': None, 'no_color': False, 'ffmpeg_location': None, 'hls_prefer_native': None, 'hls_use_mpegts': None, 'external_downloader_args': None, 'postprocessor_args': None, 'cn_verification_proxy': None, 'geo_verification_proxy': None, 'config_location': None, 'geo_bypass': True, 'geo_bypass_country': None, 'geo_bypass_ip_block': None, 'autonumber': None, 'usetitle': None})"]
  call_datum = call_data[0]
  parsed = par(call_data)
  print(parsed)
