import hunter,re
from hunter import Q
from hunter.actions import CallPrinter, CodePrinter, VarsPrinter, VarsSnooper
import io

def process_match(pth1,pth2,pth3):
    """
    pth1: "youtube_dl"
    pth2: [None, f"{string}/", f"{string}/{string}/"]
    pth3: filename
    """
    new1 = "yt_dl"
    if not pth2:
        new2 = ""
    else:
        tmp = pth2.split("/")
        assert len(tmp) == 2 or len(tmp) == 3
        new2 = tmp[0][0] if len(tmp) == 2 else f"{tmp[0][0]}/{tmp[1][0]}"
    return f"{new1}/{new2}/{pth3}"

def patch_filename_prefix(self, event=None):
  """
  Get an aligned and trimmed filename prefix for the given ``event``.

  Returns: string
  """
  rgx = re.compile(r"/(?P<pth1>youtube_dl)/(?P<pth2>.+[/])*(?P<pth3>.*py)")
  test = [
      "/youtube_dl/YoutubeDL.py",
      "/youtube_dl/extractor/common.py",
      "/youtube_dl/somedir/someother/filename.py",
      "/youtube-dl/youtube_dl/filename.py"
  ]
  if event:
    filename = event.filename or '<???>'
    match = rgx.search(filename)
    pth1,pth2,pth3=match.groupdict().values()
    filename = process_match(match.groupdict().values())
    self.filename_alignment = 25
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
