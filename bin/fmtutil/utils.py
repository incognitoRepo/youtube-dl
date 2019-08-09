class hof(object):
    def __init__(self, file_name, method):
        self.file_obj = open(file_name, method)
    def __enter__(self):
        return self.file_obj
    def __exit__(self, type, value, traceback):
        self.file_obj.close()

from contextlib import contextmanager
from operator import methodcaller

@contextmanager
def methcaller(instance,method):
    # Code to acquire resource, e.g.:
    res = getattr(instance,method)
    try:
        yield res
    finally:
        # Code to release resource, e.g.:
        if res in globals().keys():
          del globals()[key]
