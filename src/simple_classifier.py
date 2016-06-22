import hashlib, os.path, sys
import os
from classifier import Classifier
from simple_group import Simple_Group

class Simple_Classifier(Classifier):

    def __init__(self):
        self._groups = []

    def insert(self, fpath, size):
        file_hash = ""
        cur_idx = 0
        while (cur_idx < len(self._groups)):
            group = self._groups[cur_idx]
            if (group.size == size):
                if group.hash == "":
                    # FIXME The try-except statements below surpress all exceptions
                    # These should be viewable if verbose is enabled.
                    # Shouldn't print errors in this file. (Pass in exception
                    # handling fn?)

                    # (group.hash == "") implies len(group.get_entries()) == 1
                    # Hence we can del the group if try fails without checking
                    # for other entries.
                    try:
                        group.hash = get_hash(group.get_entries()[0])
                    except Exception:
                        del self._groups[cur_idx]
                        continue
                if file_hash == "":
                    # We could just let this exception be raised
                    try:
                        file_hash = get_hash(fpath)
                    except Exception:
                        return
                if group.hash == file_hash:
                    group.add_entry(fpath)
                    return
            cur_idx += 1

        new_group = Simple_Group()
        new_group.add_entry(fpath)
        new_group.size = size
        new_group.hash = file_hash
        self._groups.append(new_group)

    def get_groups(self):
        return self._groups

def get_hash(fpath):
    read_size = 65536
    fl = open(fpath,'rb')
    md5 = hashlib.md5()
    buff = fl.read(read_size)
    while (len(buff) > 0):
        md5.update(buff)
        buff = fl.read(read_size)
    fl.close()
    return md5.digest()

