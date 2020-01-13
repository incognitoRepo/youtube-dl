import inspect, dis


def func(a,b=[]):
  print(f"{a=}")
  try:
    frame = inspect.currentframe()
    code = frame.f_code
    avs = inspect.getargvalues(frame)
    return avs
    argcount = code.co_argcount # 2
    freevars = code.co_freevars # ()
    cellvars = code.co_cellvars # ()
    nlocals = code.co_nlocals # 6
    stacksize = code.co_stacksize # 6
    consts = code.co_consts # (None, 'a=', 2, 0, ('set_trace',))
    flags = code.co_flags # 67
    lnotab = code.co_lnotab # b'\x00\x01\x0e\x01\x02\x01\x08\x01\n\x01\x04\x01\x0c\x00\x06\x01\x06\x01\x06\x01'
    names = code.co_names # ('print', 'inspect', 'currentframe', 'getargvalues', 'ipdb', 'set_trace')

    gls,lcs = frame.f_globals, frame.f_locals


    funcname = frame.f_code.co_name # func
    funcscope = frame.f_back
    func = funcscope[funcname]

    filename = code.co_filename # '/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/DELETE.py'
    funclineno = code.co_firstlineno # 4
    line = linecache.get(filename,funclineno)

    empty_tuple_or_zero = [
      code.co_freevars, code.co_posonlyargcount,
      code.co_kwonlyargcount,
    ]

    x = 1+1
    from ipdb import set_trace as st; st()
    return x
  except:
    return b



# fullargspec
# inspect.getfullargspect()

# getargvalues
# avs = inspect.getargvalues(frame)

# f = frame
# c = frame.f_code
