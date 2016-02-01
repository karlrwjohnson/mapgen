_profiling = False
call_counts = {}

def assertEqual(a, b):
  assert a == b, "{} != {}".format(repr(a), repr(b))

def debug (func):
  def debug_shim(*args, **kwargs):
    try:
      ret = func(*args, **kwargs)
    except:
      print func
      print args
      print kwargs
      raise
    else:
      return ret

  return debug_shim

def enable_profiling ():
  global _profiling
  _profiling = True

def profile (func):
  def profile_shim(*args, **kwargs):
    if _profiling:
      if func in call_counts:
        call_counts[func] += 1
      else:
        call_counts[func] = 1
    return func(*args, **kwargs)
  return profile_shim
