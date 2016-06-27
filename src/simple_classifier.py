import hashlib
from simple_group import Simple_Group

hash_algs = sorted(list(hashlib.algorithms_available))

class Simple_Classifier:

    def __init__(self, hash_gen):
        self._groups = []
        self._hash_gen = hash_gen

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
        file_hash = None
        cur_idx = 0
        while (cur_idx < len(self._groups)):
            group = self._groups[cur_idx]
            if (group.file_size == size):
                if group.hash == None:
                    # (group.hash == None) implies len(group.get_entries()) == 1
                    # Hence we can del the group if try fails without checking
                    # for other entries.
                    try:
                        group.hash = _get_hash(group.get_entries()[0], self._hash_gen)
                    except Exception as e:
                        del self._groups[cur_idx]
                        if not (exc_handler == None):
                            exc_handler(e)
                        continue
                if file_hash == None:
                    file_hash = _get_hash(fpath, self._hash_gen)
                if group.hash == file_hash:
                    group.add_entry(fpath)
                    return
            cur_idx += 1

        new_group = Simple_Group()
        new_group.add_entry(fpath)
        new_group.file_size = size
        new_group.hash = file_hash
        self._groups.append(new_group)

    def get_groups(self):
        return self._groups

def _get_hash(fpath, hash_gen=None):
    try:
        if hash_gen == None: hash_gen = hashlib.md5
        read_size = 65536
        fl = open(fpath,'rb')
        hash_fn = hash_gen()
        buff = fl.read(read_size)
        while (len(buff) > 0):
            hash_fn.update(buff)
            buff = fl.read(read_size)
        fl.close()
        return hash_fn.digest()
    except OSError as e:
        if (e.filename == None):
            msg = "Hashing failure (" + e.strerror + ")"
            raise OSError(None, msg, fpath)
        raise e

def get_hash_generator(hash_alg):
    def constructor():
        return hashlib.new(hash_alg)
    if hash_alg in hashlib.algorithms_guaranteed:
        constructor = getattr(hashlib, hash_alg)
    return constructor

