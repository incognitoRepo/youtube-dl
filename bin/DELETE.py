from textwrap import TextWrapper
presyms = [" 𝑡¹", "   "]
tw=TextWrapper(width=120,
  tabsize=2,
  # initial_indent=presyms[0],
  subsequent_indent=presyms[1],
  drop_whitespace=False,
)
def implies_iterable_is_str_len1(v):
  if (v[0] in ("{","[","(")
      and isinstance(v[0],str)
      and len(v) > 1
      and len(v[0]) == 1):
    return True
  else:
    return False
header = ''
monostr = (
  '__init__:(00023|00381)return          <= (gen_extractor_classes                      '
  '                           <class youtube_dl.extractor.abc.ABCIE>\n'
  '<class youtube_dl.extractor.abc.ABCIViewIE>,\n                                 '
  '               <class youtube_dl.extractor.abcnews.AbcNewsIE>,\n   '
)
monostr = (
'(["<class \'youtube_dl.extractor.abc.ABCIE\'>", '
'"<class \'youtube_dl.extractor.abc.ABCIViewIE\'>", '
'"<class \'youtube_dl.extractor.abcnews.AbcNewsIE\'>", '
'"<class \'youtube_dl.extractor.abcnews.AbcNewsVideoIE\'>"])'
)
monostr = (
'["<class \'youtube_dl.extractor.abc.ABCIE\'>", '
'"<class \'youtube_dl.extractor.abc.ABCIViewIE\'>", '
'"<class \'youtube_dl.extractor.abcnews.AbcNewsIE\'>", '
'"<class \'youtube_dl.extractor.abcnews.AbcNewsVideoIE\'>"]'
)
lst = (
  ['0'],
  ['true'],
  ['true'],
  ['https://www.pornhub.com/video/problems/241448241'],
  ['true'],
  ['false'],
  ['false'],
  [''],
  [''],
  ['<iframe src="https://www.pornhub.com/embed/ph5d5270a4e3bca" frameborder="0" width="560" height="340" scrolling="no" allowfullscreen></iframe>'],
  ['False'],
  ['true'],
  ['22'],
  [''],
  ['https://www.pornhub.com/view_video.php?viewkey=ph5d5270a4e3bca'],
  ['https://www.pornhub.com/video/player_related_datas?id=241448241'],
  ['https://di.phncdn.com/videos/201908/13/241448241/original/(m=eaAaGwObaaaa)(mh=lDfryy7mj2erKQHp)8.jpg'],
  ["Thot gets fingered by her bfs best friend while he's in the gas station"],
  ['[720, 480, 240, 1080]'],
  ['/svvt/add?stype=svv&svalue=241448241&snonce=qfslvvpheqt3nbju&skey=6fc592d8b01ceefe76ce534a5d5c6d473189f959732cebea424d94432ad859e3&stime=1569381173'],
  ["[{'defaultQuality': True, 'format': 'mp4', 'quality': '720', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/720P_1500K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=116k&burst=1000k&hash=a8tMqQT3yY%2FgneG55DKhy6bVL3o%3D'}, {'defaultQuality': False, 'format': 'mp4', 'quality': '480', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/480P_600K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=84k&burst=1000k&hash=wGrSZFKQIDs5V%2F2rEy35P%2FiRuAk%3D'}, {'defaultQuality': False, 'format': 'mp4', 'quality': '240', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/240P_400K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=59k&burst=1000k&hash=l7ZSaTqLd1%2BQgz7WjM5gVeJ%2BRYA%3D'}]"],
  ['true'],
  ['false'],
  ['ms'],
  ["['1835445', '6785', '5606', '4961']"],
  ['https://www.pornhub.com/video?o=tr&t=m'],
  ['https://www.pornhub.com/video?o=mv&t=m'],
  ['show'],
  ['haproxy'],
  ['1000'],
  ['2000'],
  ['1111'],
  ['protrack'],
  ['ht'],
  ['new'],
  ['[]'],
  ["{'samplingFrequency': '1', 'type': 'normal', 'cdnType': 'regular', 'urlPattern': 'https://di.phncdn.com/videos/201908/13/241448241/timeline/160x90/(m=eGCaiCObaaaa)(mh=k_60LlxmyzmwX65A)S{0}.jpg', 'thumbHeight': '90', 'thumbWidth': '160'}"],
  ["{'thumb': 'https://di.phncdn.com/videos/201811/28/194118691/original/(m=ecuKGgaaaa)(mh=WkSwKoygrrxCT8pJ)6.jpg', 'duration': '47', 'title': 'Teen Lesbian Step-Sister Begs To Fuck Me', 'isHD': '1', 'nextUrl': '/view_video.php?viewkey=ph5bfe20e000b51', 'video': 'https://cw.phncdn.com/videos/201811/28/194118691/180P_225K_194118691.webm?vQWxE2Cpd0LOsfVGyATuFJljde50-38u_IRNmTHEimwatIfExj5QSh5R1Wz6z0zr-vj3Tesw0vBfbJU8NmepV80A89hp7IpC1E0s-D-H96LNf6ELqS_BWhY7RosCqmYTWaE6MsbybWJWwnM14BCdPqx1tdoAyKrnnzSdwzzLP9iPb-M1xOfm9qwSOsEatQDt3N9ol3gxGU4'}"],
  ['en'],
  ["<class 'youtube_dl.extractor.abc.ABCIE'>",
   "<class 'youtube_dl.extractor.abc.ABCIViewIE'>",
   "<class 'youtube_dl.extractor.abcnews.AbcNewsIE'>",
   "<class 'youtube_dl.extractor.abcnews.AbcNewsVideoIE'>",
   "<class 'youtube_dl.extractor.abcotvs.ABCOTVSIE'>",
   "<class 'youtube_dl.extractor.abcotvs.ABCOTVSClipsIE'>",
   "<class 'youtube_dl.extractor.academicearth.AcademicEarthCourseIE'>",
  "<class 'youtube_dl.extractor.acast.ACastIE'>",
   "<class 'youtube_dl.extractor.acast.ACastChannelIE'>",
   "<class 'youtube_dl.extractor.addanime.AddAnimeIE'>",
   "<class 'youtube_dl.extractor.adn.ADNIE'>"],
   ['tubes_cdn_service,protrack'],
)
lst2 = {
  'k1':['0'],
  'k2':['true'],
  'k3':['true'],
  'k4':['https://www.pornhub.com/video/problems/241448241'],
  'k5':['true'],
  'k6':['false'],
  'k7':['false'],
  'k8':[''],
  'k9':[''],
  'k10':['<iframe src="https://www.pornhub.com/embed/ph5d5270a4e3bca" frameborder="0" width="560" height="340" scrolling="no" allowfullscreen></iframe>'],
  'k11':['False'],
  'k12':['true'],
  'k13':['22'],
  'k14':[''],
  'k15':['https://www.pornhub.com/view_video.php?viewkey=ph5d5270a4e3bca'],
  'k16':['https://www.pornhub.com/video/player_related_datas?id=241448241'],
  'k17':['https://di.phncdn.com/videos/201908/13/241448241/original/(m=eaAaGwObaaaa)(mh=lDfryy7mj2erKQHp)8.jpg'],
  'k18':["Thot gets fingered by her bfs best friend while he's in the gas station"],
  'k19':['[720, 480, 240, 1080]'],
  'k20':['/svvt/add?stype=svv&svalue=241448241&snonce=qfslvvpheqt3nbju&skey=6fc592d8b01ceefe76ce534a5d5c6d473189f959732cebea424d94432ad859e3&stime=1569381173'],
  'k21':["[{'defaultQuality': True, 'format': 'mp4', 'quality': '720', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/720P_1500K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=116k&burst=1000k&hash=a8tMqQT3yY%2FgneG55DKhy6bVL3o%3D'}, {'defaultQuality': False, 'format': 'mp4', 'quality': '480', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/480P_600K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=84k&burst=1000k&hash=wGrSZFKQIDs5V%2F2rEy35P%2FiRuAk%3D'}, {'defaultQuality': False, 'format': 'mp4', 'quality': '240', 'videoUrl': 'https://ev.phncdn.com/videos/201908/13/241448241/240P_400K_241448241.mp4?validfrom=1569377573&validto=1569384773&rate=59k&burst=1000k&hash=l7ZSaTqLd1%2BQgz7WjM5gVeJ%2BRYA%3D'}]"],
  'k22':['true'],
  'k23':['false'],
  'k24':['ms'],
  'k25':["['1835445', '6785', '5606', '4961']"],
  'k26':['https://www.pornhub.com/video?o=tr&t=m'],
  'k27':['https://www.pornhub.com/video?o=mv&t=m'],
  'k28':['show'],
  'k29':['haproxy'],
  'k30':['1000'],
  'k31':['2000'],
  'k32':['1111'],
  'k33':['protrack'],
  'k34':['ht'],
  'k35':['new'],
  'k36':['[]'],
  'k37':["{'samplingFrequency': '1', 'type': 'normal', 'cdnType': 'regular', 'urlPattern': 'https://di.phncdn.com/videos/201908/13/241448241/timeline/160x90/(m=eGCaiCObaaaa)(mh=k_60LlxmyzmwX65A)S{0}.jpg', 'thumbHeight': '90', 'thumbWidth': '160'}"],
  'k38':["{'thumb': 'https://di.phncdn.com/videos/201811/28/194118691/original/(m=ecuKGgaaaa)(mh=WkSwKoygrrxCT8pJ)6.jpg', 'duration': '47', 'title': 'Teen Lesbian Step-Sister Begs To Fuck Me', 'isHD': '1', 'nextUrl': '/view_video.php?viewkey=ph5bfe20e000b51', 'video': 'https://cw.phncdn.com/videos/201811/28/194118691/180P_225K_194118691.webm?vQWxE2Cpd0LOsfVGyATuFJljde50-38u_IRNmTHEimwatIfExj5QSh5R1Wz6z0zr-vj3Tesw0vBfbJU8NmepV80A89hp7IpC1E0s-D-H96LNf6ELqS_BWhY7RosCqmYTWaE6MsbybWJWwnM14BCdPqx1tdoAyKrnnzSdwzzLP9iPb-M1xOfm9qwSOsEatQDt3N9ol3gxGU4'}"],
  'k39':['en'],
  'k40':["<class 'youtube_dl.extractor.abc.ABCIE'>",
   "<class 'youtube_dl.extractor.abc.ABCIViewIE'>",
   "<class 'youtube_dl.extractor.abcnews.AbcNewsIE'>",
   "<class 'youtube_dl.extractor.abcnews.AbcNewsVideoIE'>",
   "<class 'youtube_dl.extractor.abcotvs.ABCOTVSIE'>",
   "<class 'youtube_dl.extractor.abcotvs.ABCOTVSClipsIE'>",
   "<class 'youtube_dl.extractor.academicearth.AcademicEarthCourseIE'>",
  "<class 'youtube_dl.extractor.acast.ACastIE'>",
   "<class 'youtube_dl.extractor.acast.ACastChannelIE'>",
   "<class 'youtube_dl.extractor.addanime.AddAnimeIE'>",
   "<class 'youtube_dl.extractor.adn.ADNIE'>"],
   'k41':['tubes_cdn_service,protrack'],
}
"typ(l)='list',len(l)=1170 | typ(l[0])='str',len(l[0])=40"
lst3=["<class 'youtube_dl.extractor.abc.ABCIE'>",
"<class 'youtube_dl.extractor.abc.ABCIViewIE'>",
"<class 'youtube_dl.extractor.abcnews.AbcNewsIE'>",
"<class 'youtube_dl.extractor.abcnews.AbcNewsVideoIE'>",
"<class 'youtube_dl.extractor.abcotvs.ABCOTVSIE'>",
"<class 'youtube_dl.extractor.abcotvs.ABCOTVSClipsIE'>",
"<class 'youtube_dl.extractor.academicearth.AcademicEarthCourseIE'>",
 "<class 'youtube_dl.extractor.acast.ACastIE'>",
"<class 'youtube_dl.extractor.acast.ACastChannelIE'>",
"<class 'youtube_dl.extractor.addanime.AddAnimeIE'>",
"<class 'youtube_dl.extractor.adn.ADNIE'>"]

v = monostr
p = print
im=implies_iterable_is_str_len1
p(len(v));p(len(v[0]));p(len(v[0][0]))
v = lst[20]
if im(v[0][0]):
  p(im(v[0][0]))
  p('c')
  p(eval(v[0][0]))
if im(v[0]):
  p(im(v[0]))
  p('b')
  p(eval(v[0]))
if im(v):
  p(im(v))
  p('a')
  p(eval(v))

from urllib.parse import urlparse

def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False


d = {"k":lst}


for lst in (lst,lst2):
  lst = v
  vlst = []
  for l in lst:
    l = l
    fv = None
    print(f"{typ(l)=},{len(l)=} | {typ(l[0])=},{len(l[0])=}")
    print(f"{l=}")
    assert isinstance(l,list), f"{l=}"
    l0 = l[0]
    if isinstance(l0,str) and l0.lower() in ('true','false'): # bool
      if l0.lower() == 'true':
        fv = True
      else:
        fv = False
    elif len(l) > 100:
      fv = l
    elif "," not in l0: # not container
      if l0.isnumeric():
        fv = int(l0)
      elif is_url(l0):
        fv = urlparse(l0).geturl()
      elif not l0:
        fv = "()"
      else:
        fv = l0
    else:
      fv = eval(l0)
    print('fv:',pformat(fv),'\n')
    vlst.append(pformat(fv))
  nd = {k: vlst}
  s = "\n".join([str(eval(v)) for v in vlst])
  with open('D','w') as f:
    f.write(s)
  print(pformat(str(nd).encode().decode("unicode-escape")))


vlst = []
for l in lst:
  l = l # l = v
  fv = None
  print(f"{typ(l)=},{len(l)=} | {typ(l[0])=},{len(l[0])=}\n")
  # print(f"{l=}\n")
  assert isinstance(l,list), f"{l=}"
  l0 = l[0]
  if isinstance(l0,str) and l0.lower() in ('true','false'): # bool
    if l0.lower() == 'true':
      fv = True
    else:
      fv = False
  elif len(l) > 10:
    fv = l
  elif "," not in l0: # not container
    if l0.isnumeric():
      fv = int(l0)
    elif is_url(l0):
      fv = urlparse(l0).geturl()
    elif isinstance(l0,ParseResult):
      fv = urlparse(l0).geturl()
    elif not l0:
      fv = "()"
    else:
      fv = l0
  else:
    fv = eval(l0)
  # print(f"{typ(fv)=}")
  # print('fv:',pformat(fv),'\n')
  print('------===-------')
  if isinstance(fv,list) and isinstance(fv[0],str) and (len(fv) > 5):
    pfv = f",\n{'+'*8}".join(fv)
    print("a",pfv)
  elif isinstance(fv,dict):
    splt = pformat(d).split('\n')
    pfv = f",\n{'+'*8}".join(splt)
    print("b",pfv)
  else:
    pfv = pformat(fv)
    print("c",pfv)
  print(pfv)
  vlst.append(pfv)
mavs = "\n".join(vlst)
with open('D','w') as f:
  f.write(mavs)


lms1 = 4
vlst = []
first = True
for k,v in lst2.items():
  l = v
  fv = None
  print(f"{typ(l)=},{len(l)=} | {typ(l[0])=},{len(l[0])=}\n")
  print(f"{l=}\n")
  assert isinstance(l,list), f"{l=}"
  l0 = l[0]
  print(f"{l0=}")
  if isinstance(l0,str) and l0.lower() in ('true','false'): # bool
    if l0.lower() == 'true':
      fv = True
    else:
      fv = False
  elif len(l) > 10:
    fv = l
  elif isinstance(l0,list):
    fv = eval(l0)
  elif "," not in l0: # not container
    if l0.isnumeric():
      fv = int(l0)
    elif is_url(l0):
      fv = urlparse(l0).geturl()
    elif isinstance(l0,ParseResult):
      fv = urlparse(l0).geturl()
    elif not l0:
      fv = "()"
    else:
      fv = l0
  else:
    try:
      fv = eval(l0)
    except:
      fv = l0

  if isinstance(fv,list) and isinstance(fv[0],str) and (len(fv) > 5):
    # _pfv = f"\n{' '*lms1}".join(fv)
    pfv = ""
    f_flag = True
    for elm in fv:
      if f_flag:
        pfv += elm
        f_flag = False
      else:
        pfv += f"\n{'-'*lms1}" + elm
  elif isinstance(fv,list):
    l = []
    pfv = ""
    if fv[0] == "{" or isinstance(fv[0],dict):
      for i,elm in enumerate(fv[0]):
        if i == 1:
          l.append(pformat(k+elm))
        else:
          l.append(pformat(k+elm))
      pfv =  f"\n{'+'*lms1}".join(l)
    else:
      pfv = f"\n{'7'*lms1}" + k + ": " + str(fv)

  elif isinstance(fv,dict):
    splt = pformat(fv).split('\n')
    pfv = ""
    for line in splt:
      if first:
        pfv += f"\n{'1'*lms1}" + ": " + line
        first = False
      else:
        pfv += f"\n{'2'*lms1}" + k + ": " + line
  else:
    if isinstance(fv,bool) or isinstance(fv,int):
      if first:
        pfv = f"{'6'*lms1}" + k + ": " + str(fv)
        first = False
      else:
        pfv = f"{'$'*lms1}" + k + ": " + str(fv)
    elif fv[0].startswith("{"):
      if first:
        pfv = f"\n{'5'*lms1}".join(fv[0])
        first = False
      else:
        pfv = f"\n{'5'*lms1}".join(fv[0])
    else:
      if first:
        pfv = f"{'3'*lms1}" + k + ": " + pformat(fv)
        first = False
      else:
        pfv = f"{'@'*lms1}" + k + ": " + pformat(fv)
  vlst.append(pfv)
mavs = "\n".join(vlst)
mavs = "(" + mavs + ")"
with open('D','a') as f:
  f.write(mavs)



from pprint import pformat
typ = lambda o: type(o).__name__
for l in lst:
  l = l
  fv = None
  print(f"{typ(l)=},{len(l)=} | {typ(l[0])=},{len(l[0])=}")
  print(f"{l=}")
  assert isinstance(l,list), f"{l=}"
  l0 = l[0]
  if isinstance(l0,str) and l0.lower() in ('true','false'): # bool
    if l0.lower() == 'true':
      fv = True
    else:
      fv = False
  elif "," not in l0: # not container
    if l0.isnumeric():
      fv = int(l0)
    elif is_url(l0):
      fv = urlparse(l0).geturl()
    else:
      fv = l0
  else:
    fv = eval(l0)
  print('fv:',pformat(fv),'\n')
