_profiling = False
call_counts = {}

def assertEqual(a, b):
  assert a == b, "{} != {}".format(repr(a), repr(b))

def debug (func):
  def debug_shim(*args, **kwargs):
    try:
      ret = func(*args, **kwargs)
    except:
      print "\033[31;1mPre-caught an exception via {}:{}\033[0m".format(func.__module__, func.__name__)
      print "\033[0;1mPositional parameters were:\033[0m"
      print "  {}".format(repr(args))
      print "\033[0;1mNamed parameters were:\033[0m"
      print "  {}".format(repr(kwargs))
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
