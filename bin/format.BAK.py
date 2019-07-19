import ast
import re
import sys
from .re_devkit import reDevKit
from pdb import set_trace as st
from pathlib import Path


def handle_snoopfile():
  with open('pornhub.snoop.log') as f:
    snooplines = f.readlines()

  newsnoopfile = []
  for en, line in enumerate(snooplines):
    if '{' in line and '\'} => {\'' in line:
      newline = []
      initial_indent, ii = " " * line.index('{'), line.index('{')
      prefix = line[:ii]
      left, right = line.split('=>')
      for dct in [('l', left), ('r', right)]:
        side, dct = dct[0], dct[1]
        dct = dct.strip()
        i = dct.index('{')
        ri = dct.rindex('}')
        strdct = dct[i:ri + 1]
        pyobj = ast.literal_eval(strdct)
        indent = initial_indent  # + (' '*i)
        if side == 'l':
          fmtd = f"{prefix}{{"
        else:
          fmtd = f"\n{indent}{{"
        print(fmtd)
        sq = "'"
        if isinstance(pyobj, dict):
          for k, v in pyobj.items():
            if v in [True, False]:
              fmtd += f"'{k}': {v}, "
            else:
              if len(str(v)) < 40:
                try:
                  v = int(v)
                  fmtd += f"'{k}': {v}, "
                except:
                  fmtd += f"'{k}': '{v}', "
              else:
                fmtd += f"\n {indent}'{k}': {v}"
          newline.append(fmtd)
        elif isinstance(pyobj, set):
          fmtd += f"{pyobj.pop()}"
          if pyobj:
            for item in pyobj:
              fmtd += f"\n {indent}{item}"
          newline.append(fmtd)
      newline[1:1] = f"\n{initial_indent}=>"
      newsnoopfile.append("".join(newline))
    else:
      newsnoopfile.append(line)

  with open('pornhub.newsnoop.log', 'w') as f:
    for line in newsnoopfile:
      f.write(line)


def handle_topfile():
  fmtdlines = []

  def str_builder1(pth1, pth2, pth3, preserved_ws, lineno, evt, data):
    pth = f"{pth1}/{pth2}/{pth3}"
    pws = f"{preserved_ws}"
    lno = f"{lineno}"
    evt = f"{evt}"
    dta = f"{data}"
    rv, ln = f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}{dta}", len(f"{pth:>{(pad:=26)}}:{lno:<{(pad:=6)}}{evt}{pws}")
    return rv, ln

  def str_builder2(type, data):
    pws = " " * fmtdlines[-1][-1]
    elp = "..."
    typ = f"{type}"
    dta = f"{data}"
    rv = f"{pws}{elp}{typ}: {dta}"
    return rv, None

  rgx1 = re.compile(
      r"(?P<pth1>[A-z_]+)/(?P<pth2>[A-z_]+)/(?P<pth3>[A-z_]+\.py):(?P<lineno>\d{1,5})\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)$")
  rgx2 = re.compile(
      r"\s+[.]{3}\s+(?P<type>(return|exception) value):\s+(?P<data>.+)$")
  with open("top.code.log") as f:
    filelines = f.readlines()
  iterablines = iter(filelines)
  while (line := next(iterablines, None)):
    match1 = rgx1.match(line)
    if match1:
      rv, ln = str_builder1(**match1.groupdict())
      fmtdlines.append([rv, ln])
    elif (match2 := rgx2.match(line)):
      rv, _ = str_builder2(**match.groupdict())
      fmtdlines.append([rv, _])
    else:
      opencc(create(make_payload(rgx1, line)))
      opencc(create(make_payload(rgx2, line)))
      print(f"line: {line}\nmatch: {match}")
      print(f"err: {err}")
      print(f"exc_info: {sys.exc_info}")

  basepath = "/Users/alberthan/.pyenv/versions/3.8-dev/envs/vytd/src/youtube-dl/youtube_dl/logs"
  outfilepath = Path(basepath).joinpath("top.code.log.v2")
  with open(outfilepath, "w") as f:
    for line, pws in fmtdlines:
      f.write(line)


if __name__ == '__main__':
  handle_topfile()
