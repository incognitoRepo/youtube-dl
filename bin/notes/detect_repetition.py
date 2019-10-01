from hypothesis import given, event, example, composite
from hypothesis import strategies as st
from hypothesis.strategies import text

@given(text())
@example("")
def test_decode_inverts_encode(s):
  assert decode(encode(s)) == s

def encode(input_string):
  if not input_string:
    return []
  count = 1
  prev = ''
  lst = []
  for character in input_string:
    if character != prev:
      if prev:
        entry = (prev, count)
        lst.append(entry)
      count = 1
      prev = character
    else:
      count += 1
  entry = (character, count)
  lst.append(entry)
  return lst

def decode(lst):
  q = ''
  for character, count in lst:
    q += character * count
  return q

@given(st.integers())
def test_integers(i):
  pass

@given(st.integers().filter(lambda x: x % 2 == 0))
def test_even_integers(i):
  pass

@given(st.integers().filter(lambda x: x % 2 == 0))
def test_even_integers(i):
  event("i mod 3 = %d" % (i % 3,))


@st.composite
def list_and_index(draw, elements=st.integers()):
  xs = draw(st.lists(elements, min_size=1))
  i = draw(st.integers(min_value=0, max_value=len(xs) - 1))
  second(xs,i)
  return (xs, i)

def second(xs,i):
  print('xs')
  print(xs)
  print('i')
  print(i)

import shutil
import tempfile

from collections import defaultdict
import hypothesis.strategies as st
from hypothesis.database import DirectoryBasedExampleDatabase
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule


class DatabaseComparison(RuleBasedStateMachine):
  def __init__(self):
    super(DatabaseComparison, self).__init__()
    self.tempd = tempfile.mkdtemp()
    self.database = DirectoryBasedExampleDatabase(self.tempd)
    self.model = defaultdict(set)

  keys = Bundle('keys')
  values = Bundle('values')

  @rule(target=keys, k=st.binary())
  def add_key(self, k):
    return k

  @rule(target=values, v=st.binary())
  def add_value(self, v):
    return v

  @rule(k=keys, v=values)
  def save(self, k, v):
    self.model[k].add(v)
    self.database.save(k, v)

  @rule(k=keys, v=values)
  def delete(self, k, v):
    self.model[k].discard(v)
    self.database.delete(k, v)

  @rule(k=keys)
  def values_agree(self, k):
    assert set(self.database.fetch(k)) == self.model[k]

  def teardown(self):=
    shutil.rmtree(self.tempd)


TestDBComparison = DatabaseComparison.TestCase
