import hunter
from hunter import Q
from hunter.actions import CallPrinter, CodePrinter, VarsPrinter, VarsSnooper
import io


def patch_filename_prefix(self, event=None):
  """
  Get an aligned and trimmed filename prefix for the given ``event``.

  Returns: string
  """
  if event:
    filename = event.filename or '<???>'
    if len(filename) > self.filename_alignment:
      filename = '[...]{}'.format(filename[5 - self.filename_alignment:])
    return '{:>{}}{COLON}:{LINENO}{:<5} '.format(
        filename, self.filename_alignment, event.lineno, **self.other_colors)
  else:
    return '{:>{}}       '.format('', self.filename_alignment)

# Cap2,Cop2,Vap2,Snp2

QueryDict = {
    "test1":
    Q(
        filename_contains="youtube_dl",
        # filename_endswith="options.py",
        stdlib=False,  # venv editable pkgs are stdlib
        action=CallPrinter()
    ),
    "test2":
    Q(
        filename_contains="youtube_dl",
        stdlib=False,
        action=CodePrinter(stream=io.StringIO())
    ),
    "test3":
    Q(
        filename_contains="youtube_dl",
        stdlib=True,
        actions=[
            CallPrinter(stream=io.StringIO()),
            CodePrinter(stream=io.StringIO()),
            VarsSnooper(stream=io.StringIO())
        ]
    ),
}

# import youtube_dl
# url = 'https://www.pornhub.com/view_video.php?viewkey=ph59348e1c87cd2'
# hunterconfig = QueryDict['test1']
# action = hunterconfig.actions[0]
# out = action.stream
# hunter.trace(hunterconfig)
# x = 3
# x += 1
# youtube_dl.main([__file__, url])
# rv = out.getvalue()
# print(rv)
# handler = h.handler
# actions = handler.actions
# action = handler.actions[0]
# stream = action.stream

# if __name__ == '__main__':
#   print(sys.argv)
