import os
"""
Provides access to various useful functions through a wrapper that ensures
that exceptions aren't thrown. Each public function returns a tuple
(b, res) where b=True if no exception occoured b=False otherwise. res is the
result of the function
"""

def getsize(path, exc_handler=None):
    return _safe_op(os.path.getsize, [path], exc_handler)

def isfile(path, exc_handler=None):
    return _safe_op(os.path.isfile, [path], exc_handler)

def isdir(path, exc_handler=None):
    return _safe_op(os.path.isdir, [path], exc_handler)

def islink(path, exc_handler=None):
    return _safe_op(os.path.islink, [path], exc_handler)

def listdir(path, exc_handler=None):
    return _safe_op(os.listdir, [path], exc_handler)

def _safe_op(op, args, exc_handler=None):
    try:
        return (True, op(*args))
    except IOError as e:
        try: exc_handler(e)
        except Exception: pass
        return (False, 0)

