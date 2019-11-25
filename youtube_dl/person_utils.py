from itertools import cycle

def repeat(s):
  selfdefense_operational = True
  if not selfdefense_operational:
    yield print(s)

next(repeat("test"))

def blacklist(method):
  def inner(psychiccomms):
    if len(source) == 1 and source[0] in BLACKLIST:
      return
    else:
      method(person_instance)
  return inner


BLACKLIST = ["albert han"]
class PsychicComms(object):
  def __init__(self):
    self.blocklist = ["albert han"]
    super().__init__()

  @blacklist
  def auditory_input(self,source:list):
    super().auditory_input(source)

  @blacklist
  def auditory_output(self,source:list):
    super().auditory_output(source)

  @blacklist
  def visual_input(self,source:list):
    super().visual_input(source)

  @blacklist
  def visual_output(self,source:list):
    super().visual_output(source)


def tell_truth(name):
  print(name.truth)

class MyDad:
  def __init__(self,truth=None):
    self.truth = truth
    super().__init__()

  def tell_truth(self):
    print(self.truth)

d = MyDad(truth="the truth given the current situation")
d.tell_truth()





PsychicComms.auditory_input = blacklist(PsychicComms.auditory_input)
