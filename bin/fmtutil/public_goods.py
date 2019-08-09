import pandas as pd

def ppd(series,pat,val=-1):
  """wsage: ppd(df.snoop_data, pat='display.max_colwidth')"""
  with pd.option_context(pat, val):
    print(series)

