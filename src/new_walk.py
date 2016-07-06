from os import scandir, path

# Credit
# https://hg.python.org/cpython/file/3.5/Lib/os.py
# On changeset 102257:127569004538 (Python 3.5)
def new_walk(top, on_error=None, followlinks=False):
    """
    Unix-only version of os.walk with topdown=False. Instead of the standard
    dirs yielded by os.walk, the dirs here is a list of tuples, where the first
    element of the tuple is the entry name as with os.walk, and second is the
    inode number of the corresponding file.

    This function was created to avoid an additional call to os.lstat which
    results in a syscall (on top of the syscall from os.walk)
    """
    dirs = []
    nondirs = []

    try:
        scandir_it = scandir(top)
        entries = list(scandir_it)
    except OSError as e:
        try: on_error(e)
        except Exception: pass
        return

    for entry in entries:
        try:
            if(entry.is_dir()):
                dirs.append((entry.name, entry.inode()))
            else:
                nondirs.append(entry.name)
        except OSError:
            nondirs.append(entry.name)
    
    yield top, dirs, nondirs

    islink, join = path.islink, path.join
    for (dirname, inode) in dirs:
        new_path = join(top, dirname)

        if followlinks or not islink(new_path):
            yield from new_walk(new_path, on_error, followlinks)

