FILENAME_PREFIXES = ["call","code","snoop"]
BASE = "full.log"
FILENAMES = [f"{prefix}.{BASE}" for prefix in FILENAME_PREFIXES]
@dataclass
class Color:
  color_modifiers = {
    'RESET': '\x1b[0m',
    'BRIGHT': '\x1b[1m',
    'DIM': '\x1b[2m',
    'NORMAL': '\x1b[22m',
  }
  segment_colors = {
    'CALL': '\x1b[1m\x1b[34m',
    'LINE': '\x1b[39m',
    'RETURN': '\x1b[1m\x1b[32m',
    'EXCEPTION': '\x1b[1m\x1b[31m',
    'COLON': '\x1b[1m\x1b[30m',
    'LINENO': '\x1b[0m',
    'KIND': '\x1b[36m',
    'CONT': '\x1b[1m\x1b[30m',
    'VARS': '\x1b[1m\x1b[35m',
    'VARS-NAME': '\x1b[22m\x1b[35m',
    'INTERNAL-FAILURE': '\x1b[1m\x1b[41m\x1b[31m',
    'INTERNAL-DETAIL': '\x1b[37m',
    'SOURCE-FAILURE': '\x1b[1m\x1b[43m\x1b[33m',
    'SOURCE-DETAIL': '\x1b[37m',
  }
  fg_colors = {
    'fore(BLACK)': '\x1b[30m',
    'fore(RED)': '\x1b[31m',
    'fore(GREEN)': '\x1b[32m',
    'fore(YELLOW)': '\x1b[33m',
    'fore(BLUE)': '\x1b[34m',
    'fore(MAGENTA)': '\x1b[35m',
    'fore(CYAN)': '\x1b[36m',
    'fore(WHITE)': '\x1b[37m',
    'fore(LIGHTBLACK_EX)': '\x1b[90m',
    'fore(LIGHTRED_EX)': '\x1b[91m',
    'fore(LIGHTGREEN_EX)': '\x1b[92m',
    'fore(LIGHTYELLOW_EX)': '\x1b[93m',
    'fore(LIGHTBLUE_EX)': '\x1b[94m',
    'fore(LIGHTMAGENTA_EX)': '\x1b[95m',
    'fore(LIGHTCYAN_EX)': '\x1b[96m',
    'fore(LIGHTWHITE_EX)': '\x1b[97m',
    'fore(RESET)': '\x1b[39m',
  }
  bg_colors = {
    'back(BLACK)': '\x1b[40m',
    'back(BLUE)': '\x1b[44m',
    'back(CYAN)': '\x1b[46m',
    'back(GREEN)': '\x1b[42m',
    'back(LIGHTBLACK_EX)': '\x1b[100m',
    'back(LIGHTBLUE_EX)': '\x1b[104m',
    'back(LIGHTCYAN_EX)': '\x1b[106m',
    'back(LIGHTGREEN_EX)': '\x1b[102m',
    'back(LIGHTMAGENTA_EX)': '\x1b[105m',
    'back(LIGHTRED_EX)': '\x1b[101m',
    'back(LIGHTWHITE_EX)': '\x1b[107m',
    'back(LIGHTYELLOW_EX)': '\x1b[103m',
    'back(MAGENTA)': '\x1b[45m',
    'back(RED)': '\x1b[41m',
    'back(RESET)': '\x1b[49m',
    'back(WHITE)': '\x1b[47m',
    'back(YELLOW)': '\x1b[43m'
  }

  def fore(self,txt,key=None):
    """..key: segment|color"""
    if sgmt:
      c = self.segment_colors[key]
    else:
      _key = f"{fore}({key})"
      c = self.fg_colors[_key]
    reset = self.color_modifiers['RESET']
    s = (
      f"{c}",
      f"{txt}",
      f"{reset}",
    )
    sj = "".join(s)
    return sj

  def color_test(self):
    for COLORS in [self.fg_colors,self.fg_colors]:
      d = {
        'dict': COLORS['__dict__'],
        'foredict': COLORS['fore(__dict__)'],
        'backdict': COLORS['back(__dict__)'],
      }
      ocs = {k:v for k,v in COLORS.items() if not "__" in k}
      for k,v in COLORS.items():
        print(f"{k}: {v}")
      for k,v in COLORS.items():
        print(f'"{k}": "{repr(v)}"')
      for k,v in d.items():
        print(f"{k}: {v}")
      for k,v in d.items():
        print(f'"{k}": "{repr(v)}"')
