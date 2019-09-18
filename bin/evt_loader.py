import pickle
from fmtutil.row.classes import DataCollections

import sys
import stackprinter
stackprinter.set_excepthook(
  style='darkbg3',
  source_lines=5,
  show_signature=True,
  show_vals='like_source',
  truncate_vals=500)

with open('/Users/alberthan/VSCodeProjects/vytd/src/youtube-dl/bin/eventpickle/evtdcts_pklpth.pkl','rb') as f:
  evt_dcts = pickle.load(f)

e0,e1,e2 = evt_dcts[:3]
dc = DataCollections(evt_dcts)
epdf, evts, evts_df = dc.evt_dcts_df, dc.evts, dc.evts_df

"""
 style: string
        'plaintext' (default): Output just text
        'darkbg', 'darkbg2', 'darkbg3', 'lightbg', 'lightbg2', 'lightbg3':
            Enable colors, for use in terminals that support 256 ansi
            colors or in jupyter notebooks (or even with `ansi2html`)
    source_lines: int or 'all'
        Select how much source code context will be shown.
        int 0: Don't include a source listing.
        int n > 0: Show n lines of code. (default: 5)
        string 'all': Show the whole scope of the frame.
    show_signature: bool (default True)
        Always include the function header in the source code listing.
    show_vals: str or None
        Select which variable values will be shown.
        'line': Show only the variables on the highlighted line.
        'like_source' (default): Show only those visible in the source listing
        'all': Show every variable in the scope of the frame.
        None: Don't show any variable values.
    truncate_vals: int
        Maximum number of characters to be used for each variable value.
        Default: 500
    suppressed_paths: list of regex patterns
        Set less verbose formatting for frames whose code lives in certain paths
        (e.g. library code). Files whose path matches any of the given regex
        patterns will be considered boring. The first call to boring code is
        rendered with fewer code lines (but with argument values still visible),
        while deeper calls within boring code get a single line and no variable
        values.
        Example: To hide numpy internals from the traceback, set
        `suppressed_paths=[r"lib/python.*/site-packages/numpy"]`
"""
