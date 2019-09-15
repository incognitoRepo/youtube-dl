import argparse

def cli():
  parser = argparse.ArgumentParser(
    description='Enter a QueryConfig key',
    epilog="e.g., python fmt.py full")
  parser.add_argument('--qckey', type=str, nargs=1,
                      help='the common suffix for each file',
                      default="full.log")
  args = parser.parse_args()
  meth = args.qckey.pop().split('.')[0]
  if len(sys.argv) == 2:
    with fu.methcaller(QueryConfig(),meth) as m:
      filenames = m().filenames
  return filenames


def make_LEold():
  """Line Event & Header"""
  sym1,sym2 = syms = ["≡","⏐"]
  idts = indents = [2,3]
  le_syms = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  LE = get_fold_symbol(sym=le_sym,indent=3)
  return LE


def make_VLold(nargs:int):
  """VerboseList"""
  # sym1a,sym1b = "⫴","⏐"
  # sym2 = "𝑡"
  vl1_first = get_fold_symbol(sym=sym1a,indent=2)
  vl1_rest = get_fold_symbol(sym=sym1b,indent=2)
  first = f"{WHITESPACE}{vl1_first}"
  rest  = repeat(f"{WHITESPACE}{vl1_rest}",nargs)
  vl1 = iter([first] + list(vl1_rest))
  # vl2 = get_fold_symbol(sym=sym2,indent=2)
  return vl1,vl2


def make_PTold(nargs:int):
  """ParsedTuple"""
  sym1a, sym1b = "⭵", "⏐"
  sym2 = "⩣"
  pt1_first = get_fold_symbol(sym=sym1a,indent=1)
  pt1_rest = get_fold_symbol(sym=sym1b,indent=2)
  first = f"{WHITESPACE}{pt1_first}"
  rest  = repeat(f"{WHITESPACE}{pt1_rest}",nargs)
  pt1 = iter([first] + list(rest))
  pt2 = get_fold_symbol(sym=sym2,indent=2)
  return pt1,pt2



def make_MS():
  """MutableStr"""
  sym = "≡"
  return sym

def make_US():
  """UserString"""
  us_sym = "𝑢"
  US = get_fold_symbol(sym=us_sym,indent=2)
  return US

def make_SFWA():
  """SimpleFunkWithArgs
  is used to create the symbols passed to structure1
  returns sf1,sf2"""
  sym1,sym2 = syms = ["𝑠","⫝"]
  idts = [1,2]
  sf1,sf2 = sfs = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  return sf1,sf2

def make_PJ():
  """ParsedJSON
  is used to create the symbols passed to structure2
  returns pj1,pj2"""
  sym1,sym2 = syms = ["𝑗","⫱"]
  idts = [1,2]
  pj1,pj2 = pjs = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  return pj1,pj2

def make_PH():
  """ParsedHTML
  is used to create the symbols passed to structure2
  returns ph1,ph2"""
  sym1,sym2 = syms = ["ℎ","∵"]
  idts = [1,2]
  ph1,ph2 = phs = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  return ph1,ph2

def make_LE():
  """Line Event & Header"""
  sym1,sym2 = syms = ["≡","⏐"]
  idts = indents = [2,3]
  le_syms = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  le1,le2 = le_syms
  return le1,le2

def make_VL(nargs:int):
  """VerboseList"""
  sym1,sym2,sym3 = syms = ["𝑡","⫴","⏐"]
  idts = indents = [2,2,2]
  vl_syms = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  vl1 = get_fold_symbol(sym=vl_syms[0],indent=2)
  vl2 = iter([vl_syms[1]] + list(repeat(vl_syms[2],nargs)))
  return vl1,vl2

def make_PT(nargs:int):
  """ParsedTuple"""
  sym1,sym2,sym3 = syms = ["⩣","⭵","⏐"]
  idts = indents = [2,2,2]
  pt_syms = [get_fold_symbol(s,i) for s,i in zip(syms,idts)]
  pt1 = get_fold_symbol(sym=pt_syms[0],indent=2)
  pt2 = iter([pt_syms[1]] + list(repeat(pt_syms[2],nargs)))
  return pt1,pt2


def agg_main():
  query,actions,outputs,filenames,write_func,pkldf = qcfg = QueryConfig().full()
  dfpath = basepath.joinpath('src/youtube-dl/bin/agg.full/df.pkl')
  dfs = {}
  for filename in filenames:
    df = fur.get_df_from_tracefile(filename)
    assert isinstance(df,pd.DataFrame), df
    dfs[filename] = df
  aggdf = fud.aggregate_aggdfs(list(dfs.values()))
  aggdf.to_pickle(dfpath)
  aggdf = pd.read_pickle(dfpath)
  literate_style = fud.write_literate_style_df(aggdf,filename="agg.full/agg")
  fltrd_noline_df = fud.filter_line_events(aggdf,dfpath)
  lit_style_noline = fud.write_literate_style_df(fltrd_noline_df,filename="agg.full/fltrd/noline")
  dct_o_dfs_by_filename = fud.groupby_filename(fltrd_noline_df,dfpath)
  for k,v in dct_o_dfs_by_filename.items():
    fud.write_literate_style_df(v,filename=f"agg.full/fltrd/grpd/{k}")
  return aggdf

def get_tfdf(dfs,dfpath):
  tfdf = fud.aggregate_tfdfs(list(dfs.values()))
  dfpath.parent.mkdir(parents=True,exist_ok=True)
  tfdf.to_pickle(dfpath)
  tfdf = pd.read_pickle(dfpath)
  return tfdf

def fiesta(tfdf,dfpath):
  idf_w_lines = tfdf[tfdf.filepath.str.contains('__init__')]
  literate_style = fud.write_literate_style_df(tfdf,filename="targetfuncs/tfdf")
  fltrd_noline_df = fud.filter_line_events(tfdf,dfpath)
  lit_style_noline = fud.write_literate_style_df(fltrd_noline_df,filename="targetfuncs/fltrd/noline")
  dct_o_dfs_by_filename = fud.groupby_filename(fltrd_noline_df,dfpath)
  for k,v in dct_o_dfs_by_filename.items():
    fud.write_literate_style_df(v,filename=f"targetfuncs/fltrd/grpd/{k}")
  return literate_style, fltrd_noline_df, lit_style_noline, idf_w_lines, dct_o_dfs_by_filename

def get_targeted_df(filename):
  idf = dfs_by_filename[filename]
  idf.to_pickle(dfpath.parent.joinpath(f'idf_{filename}.pkl'))
  idf2 = idf.copy()
  idf2.call_data = pd.Series(idf.apply(process_row,axis=1))
  idf2.to_pickle(dfpath.parent.joinpath(f'idf2_{filename}.pkl'))
  return idf2

def tf_main():
  query,actions,outputs,filenames,write_func,pkldf = qcfg = QueryConfig().targetfunc()
  dfpath = basepath.joinpath('src/youtube-dl/bin/tfdf/df.pkl')
  dfs = {}
  for filename in filenames:
    df = fur.get_df_from_tracefile(filename)
    assert isinstance(df,pd.DataFrame), df
    dfs[filename] = df
  tfdf = get_tfdf(dfs, dfpath)
  lit_style, fltrd_noline_df, lit_style_noline, idf_w_lines, dfs_by_filename = fiesta(tfdf,dfpath)
  idf = get_targeted_df(filename="__init__")
  tfdfpath = dfpath.parent
  lit_idf = fud.write_lit_file(idf2,tfdfpath)
  return idf, lit_idf

def short():
  dfpath = basepath.joinpath('src/youtube-dl/bin/tfdf/idf.pkl')
  idf = pd.read_pickle(dfpath)
  idf2 = idf.copy()
  call_data_series = idf.apply(process_row,axis=1)
  call_data_lst = [SimpleFunkWithArgs(cd)
                   if not (
      isinstance(cd,LineEvent)
      or isinstance(cd,VerboseList)
      or isinstance(cd[0], ParsedTuple)
  )
      else cd for cd in call_data_series]
  idf2.call_data = call_data_lst
  assert isinstance(idf2.iloc[0].call_data,SimpleFunkWithArgs), type(idf2.iloc[0].call_data)
  return idf2, call_data_lst

def short_tfdf(whichdf):
  dfpath = basepath.joinpath('src/youtube-dl/bin/tfdf/df.pkl')
  tfdf = pd.read_pickle(dfpath)
  if whichdf == "idf_w_lines":
    idf = idf_w_lines = tfdf[tfdf.filepath.str.contains('__init__')]
  line_events = list(idf[idf.event_kind.str.contains('line')].call_data)
  line_events_as_str = [str(elm)[2:-2] for elm in line_events]
  with open(dfpath.parent.joinpath('line_events.txt'), 'w') as f:
    f.write("\n".join(line_events_as_str))
  call_data_series = idf.apply(process_row,axis=1)
  call_data_lst = [SimpleFunkWithArgs(cd)
                   if not (
      isinstance(cd,LineEvent)
      or isinstance(cd,VerboseList)
      or isinstance(cd[0], ParsedTuple)
  )
      else cd for cd in call_data_series]
  idf.call_data = call_data_lst
  return idf, call_data_lst

def load_idf(loadidf,whichload="short",whichdf=None):
  if loadidf:
    if whichload == "short":
      idf2, cds = short()
    elif whichload == "short_tfdf":
      idf2, cds = short_tfdf(whichdf)
    else:
      idf2, cds = load_tfdf()
  return idf2, cds
