import hashlib, os.path, sys
import os
from classifier import Classifier
from simple_group import Simple_Group

class Simple_Classifier(Classifier):

    def __init__(self):
        self._groups = []

    def insert(self, fpath):
        # TODO Shouldn't be error handling here. Fix it.
        try:
            size = os.path.getsize(fpath)
        except FileNotFoundError:
            outstr = "Skipping not-found file: " + fpath
            print(outstr, file=sys.stdout)
            return
        file_hash = ""
        for group in self._groups:
            if (group.size == size):
                if group.hash == "":
                    group.hash = get_hash(group.get_entries()[0])
                if file_hash == "":
                    file_hash = get_hash(fpath)
                if (group.hash == file_hash):
                    group.add_entry(fpath)
                    return
        
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
    return md5.digest()

