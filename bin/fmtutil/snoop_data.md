# SNOOP DATA

### aggdf: snoop_data cell

```py
snpcell = aggdf.iloc[-3].snoop_data
assert isinstance(snpcell,list), f'{type(snpcell)=}{snpcell=}'
print(snpcall)
["1filenames := [PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/call.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/code.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/snoop.full.log')]",
 ' 2outputs := [<_io.StringIO object at 0x100a953a0>, <_io.StringIO object at 0x1055995e0>, <_io.StringIO object at 0x105599d30>]',
 ' 2self := <youtube_dl.hunterconfig.QueryConfig object at 0x100b26820>']
```

### loop iteration example

```py
s0,s1,s2 = ss = snpcell[0],snpcell[1],snpcell[2]
assert [isinstance(s,str) for s in ss], ss
s0,s1,s2 = [s.strip() for s in ss]
print(f"{s0=}\n{s1=}\n{s2=}")

s0="1filenames := [PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/call.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/code.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/snoop.full.log')]"
s1='2outputs := [<_io.StringIO object at 0x100a953a0>, <_io.StringIO object at 0x1055995e0>, <_io.StringIO object at 0x105599d30>]'
s2='2self := <youtube_dl.hunterconfig.QueryConfig object at 0x100b26820>'
```

### split each line of the snoop_data cell into a {var:val} mapping

```py
ss0,ss1,ss2 = splitcells = s0.split(':='),s1.split(':='),s2.split(':=')
sskvs = {k:v for k,v in splitcells} # gather into a dictionary
print(f"{ss0}\n{ss1}\n{ss2}")

['1filenames ', " [PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/call.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/code.full.log'), PosixPath('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/agg.full/snoop.full.log')]"]
['2outputs ', ' [<_io.StringIO object at 0x100a953a0>, <_io.StringIO object at 0x1055995e0>, <_io.StringIO object at 0x105599d30>]']
['2self ', ' <youtube_dl.hunterconfig.QueryConfig object at 0x100b26820>']
```

### build the fmtd str
- the first string will be concated to an existing string
  - no initial indent is needed
- the next line will need to be indented to [colWhereFirstStringStarted + 2spaces]

```py
for rawrow in aggdf.iloc[-3:-2].itertuples():
  rtpl = rawrow # has rtpl.Index agttr
r = aggdf.iloc[-3] # r.Index raises error
assert isinstance(rtpl,pd.core.frame.Pandas) & isinstance(r, pd.series.Series), f"{rtpl=}{r=}"

cad,snd = dtacels = rtpl.call_data,rtpl.snoop_data
assert all([isinstance(dtacel,list) for dtacel in dtacels]), r

max_lines_in_row = max(map(len,dtacels))
NEWsublst,space = [],"*"
for line in range(max_lines_in_row):
  genca,gensn = iter(cad), iter(snd)
    if line == 0:
      lst_o_vals = process_lstlike_str()
      lst_o_vals = [f"{r.Index:9}",f"{r.filepath:>20}",f"{r.line_number:<9}",f"{next(genca,'^'):<80.80}",f"{next(gensn,'&'):<80.80}"]
      lst_o_lens = list(accumulate([len(val) for val in lst_o_vals]))  # 9+20+9+80=118 (snp starts on 119)
      s = "".join(lst_o_vals)
    else:
      lst_o_vals = [f"{space:9}",f"{space:>20}",f"{space:<9}",f"{next(genca,'@'):<80.80}",f"{next(gensn,'%'):<80.80}"]
      s = "".join(lst_o_vals)
    NEWsublst.append(s)
    NEWsublst_as_str = "\n".join(NEWsublst)
    NEWlst.append(NEWsublst_as_str)
  RETval = "\n".join(NEWlst)
  return RETval



new_snoopdata_cell,first = [], True
for k,v in sskvs.items():
  k,v = k.strip(),v.strip()
  if v.startswith('['):
    finval,first = process_lstlike_str(v,first)
    new_snoopdata_cell.append(finval)
  else:
    finval,first = process_lstlike_str(v,first)
    new_snoopdata_cell.append(finval)
print("".join(new_snoopdata_cell))

```py
def cycle(iterable):
  # cycle('ABC') --> A B C A B C A B C
  saved = []
  for element in iterable:
    yield element
    saved.append(element)
  while saved:
    for element in saved:
      yield element

def line0():
  """the 1st line, in which all variables have values"""
  [f"{r.Index:9}",f"{r.filepath:>20}",f"{r.line_number:<9}",f"{next(genca,'^'):<80.80}",f"{next(gensn,'&'):<80.80}"]

def line1_plus():
  """the rest of the lines, where only call_data and/or snoop_data may have values"""
  lst_o_vals = [f"{space:9}",f"{space:>20}",f"{space:<9}",f"{next(genca,'@'):<80.80}",f"{next(gensn,'%'):<80.80}"]
  s = "".join(lst_o_vals)

def str_implies_iter():
  """the value of the line implies an iterable"""
  a=2

def str_implies_str():
  """the value of the line implies nothing"""
  pass




def line0_lstlikestr(s):
  space = "\u0020"
  vlstlen = s.count(',')+1
  v_aslst = s[1:-1].split(',')
  eg_val,n_rest = v_aslst[0], vlstlen-1 # n_rest = number of the rest of args
  assert vlstlen == len(v_aslst), f"{v=}, {vlstlen=}"
  if first:
    finval = f"{k}:{eg_val}, +({n_rest})…,\n"
    first = False
  else:
    finval = f"{k}:{eg_val}, +({n_rest})…,\n"
  return finval, first

def line12n_lstlikestr(s):
  space = "\u0020"
  vlstlen = s.count(',')+1
  v_aslst = s[1:-1].split(',')
  eg_val,n_rest = v_aslst[0], vlstlen-1 # n_rest = number of the rest of args
  assert vlstlen == len(v_aslst), f"{v=}, {vlstlen=}"
  if first:
    finval = f"{k}:{eg_val}, +({n_rest})…,\n"
    first = False
  else:
    finval = f"{space*30}{k}:{eg_val}, +({n_rest})…,\n"
  return finval, first

def line0_str():
  space = "\u0020"
  vlstlen = v.count(',')
  if first:
    finval = f"{k}:{v[1:-1]}, +({vlstlen})…,\n"
    first = False
  else:
    finval = f"{k}:{v[1:-1]}, +({vlstlen})…,\n"

def line12n_str():
  space = "\u0020"
  vlstlen = v.count(',')
  if first:
    finval = f"{k}:{v[1:-1]}, +({vlstlen})…,\n"
    first = False
  else:
    finval = f"{space*30}{k}:{v[1:-1]}, +({vlstlen})…,\n"

```
   NEWsublst,space = [],"*"
    for line in range(max_lines_in_row):
      print(f"{line=}")
      genca,gensn = iter(cad),iter(snd)
      if line == 0:
        lst_o_vals = [f"{r.Index:9}",f"{r.filepath:>20}",f"{r.line_number:<9}",f"{next(genca,'^'):<80.80}",f"{next(gensn,'&'):<80.80}"]
        lst_o_lens = list(accumulate([len(val) for val in lst_o_vals]))  # 9+20+9+80=118 (snp starts on 119)
        s = "".join(lst_o_vals)
      else:
        lst_o_vals = [f"{space:9}",f"{space:>20}",f"{space:<9}",f"{next(genca,'@'):<80.80}",f"{next(gensn,'%'):<80.80}"]
        s = "".join(lst_o_vals)
      NEWsublst.append(s)
    NEWsublst_as_str = "\n".join(NEWsublst)
    NEWlst.append(NEWsublst_as_str)
  RETval = "\n".join(NEWlst)
  return RETval
```
