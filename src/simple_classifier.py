import hashlib
from classifier import Classifier
from simple_group import Simple_Group

class Simple_Classifier(Classifier):

    def __init__(self):
        self._groups = []

    def insert(self, fpath, size, exc_handler=None):
        """
        Inserts file path refered to by 'fpath' (with size 'size') into the
        classifier. Throws an exception if cannot read file at 'fpath' if a read
        was required.

        An exception might occour when reading a different file whose path has
        already been added to the classifier. If this happens, the exception is
        handled here and the path is removed from the classifier.
        exc_handler(Exception) may be provided to perform an action on such an
        exception.
        """
        file_hash = ""
        cur_idx = 0
        while (cur_idx < len(self._groups)):
            group = self._groups[cur_idx]
            if (group.size == size):
                if group.hash == "":
                    # (group.hash == "") implies len(group.get_entries()) == 1
                    # Hence we can del the group if try fails without checking
                    # for other entries.
                    try:
                        group.hash = get_hash(group.get_entries()[0])
                    except Exception as e:
                        del self._groups[cur_idx]
                        if not (exc_handler == None):
                            exc_handler(e)
                        continue
                if file_hash == "":
                    file_hash = get_hash(fpath)
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

# TODO Instead of throwing exception due to method calls inside, throw a new
# more useful exception that informs of the path for which file access
# resulted in an exception
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

