import sys

def t():
  try:
    1/0
  except:
    exc = sys.exc_info()
    return exc

exc = t()
