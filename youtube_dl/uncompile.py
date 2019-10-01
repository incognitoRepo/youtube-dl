import struct

def show_file(fname):
  f = open(fname, "rb")
  file = f.read()
  magic = f.read(16)
  f.read(4)
  moddate = f.read(8)
  modtime = time.asctime(time.localtime(struct.unpack('L', moddate)[0]))
  print("magic %s" % (magic.encode('hex')))
  print("moddate %s (%s)" % (moddate.encode('hex'), modtime))
  code = marshal.load(f)
  show_code(code)

def show_code(code, indent=''):
    print("%scode" % indent)
    indent += '   '
    print("%sargcount %d" % (indent, code.co_argcount))
    print("%snlocals %d" % (indent, code.co_nlocals))
    print("%sstacksize %d" % (indent, code.co_stacksize))
    print("%sflags %04x" % (indent, code.co_flags))
    show_hex("code", code.co_code, indent=indent)
    dis.disassemble(code)
    for const in code.co_consts:
      if type(const) == types.CodeType: show_code(const, indent+'   ')
      else: print("   %s%r" % (indent, const))
    print("%snames %r" % (indent, code.co_names))
    print("%svarnames %r" % (indent, code.co_varnames))
    print("%sfreevars %r" % (indent, code.co_freevars))
    print("%scellvars %r" % (indent, code.co_cellvars))
    print("%sfilename %r" % (indent, code.co_filename))
    print("%sname %r" % (indent, code.co_name))
    print("%sfirstlineno %d" % (indent, code.co_firstlineno))
    show_hex("lnotab", code.co_lnotab, indent=indent)

def show_hex(label, h, indent):
    h = h.encode('hex')
    if len(h) < 60:
      print("%s%s %s" % (indent, label, h))
    else:
      print("%s%s" % (indent, label))
      for i in range(0, len(h), 60):
        print("%s   %s" % (indent, h[i:i+60]))


def magic2int(magic):
  """Given a magic byte string, e.g. b'\x03\xf3\r\n', compute the
  corresponding magic integer, e.g. 62211, using the conversion
  method that does this.

  See also dictionary magic2nt2version which has precomputed these values
  for knonwn magic_int's.

  """
  return struct.unpack("<Hcc", magic)[0]

show_file('__main__.cpython-38.pyc')


magic = importlib.util.MAGIC_NUMBER  # b'\S\r\r\n'
# v3.8.0b2:21dd01dad7
import dis, marshal, sys
fname = '__main__.cpython-38.pyc'
header_size = 16 if sys.version_info >= (3, 3) else 8
with open(fname, "rb") as f:
  magic_and_timestamp = f.read(header_size)  # first 8 or 12 bytes are metadata
  code = marshal.load(f)                     # rest is a marshalled code object

dis.disassemble(code)

f = open(fname, "rb")
file = f.read()
magic = f.read(16)
f.read(4)
moddate = f.read(8)
modtime = time.asctime(time.localtime(struct.unpack('L', moddate)[0]))
