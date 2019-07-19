# @dataclass
# class Test:
#   a: int
#   x: int = field(init=False)
#   y: int = field(default=0,init=False)

#   def __post_init__(self):
#     self.x = 99
#     self.ii()

#   def ii(self):
#     print(self.a)
#     Test.y += 100


# t1 = Test(2)
# print(t1.x,t1.y)
# t2 = Test(5)
# print(t1.x,t1.y)
# import re

# rgx1 = re.compile(
#     r"(?P<pth1>[A-z_]+)/(?P<pth2>[A-z_]+)/(?P<pth3>[A-z_]+\.py):(?P<lineno>\d{1,5})"
#     r"\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)"
#     r"$")
# rgx2 = re.compile(
#     r"(?P<pth1>[A-z_]+)/(?P<pth2>[A-z_]+)/(?P<pth3>[A-z_]+\.py):(?P<lineno>\d{1,5})\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)$"
# )
# print(rgx1,'\n',rgx2)
# assert rgx1 == rgx2


def a():
  re = [r"(?P<pth1>[A-z_]+)/(?P<pth2>[A-z_]+)/(?P<pth3>[A-z_]+\.py):(?P<lineno>\d{1,5})\s+(?P<evt>[a-z]+)(?P<preserved_ws>\s+)(?P<data>[^\s].+)$",
        '9huh9ghohoho']
  print(1)
