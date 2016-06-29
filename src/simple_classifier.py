import hashlib
#from simple_group import Simple_Group

hash_algs = sorted(list(hashlib.algorithms_available))

class Simple_Classifier:

    def __init__(self, hash_gen):
        self._groups = {}
        self._hash_gen = hash_gen

    #***************#
    # insert method #
    #***************#
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
        fl_data = _File_Data(fpath, size)
        cur_idx = 0
        
        # "Pointers" for speed
        iseq = _File_Data.is_equal
        groups = self._groups
        hash_gen = self._hash_gen

        try:
            groups = groups[size]
        except KeyError:
            group = _Group(fl_data)
            group.add_entry(fpath)
            groups[size] = [group]
            return

        while (cur_idx < len(groups)):
            try:
                group = groups[cur_idx]
                if (iseq(group.data, fl_data, hash_gen)):
                    group.add_entry(fpath)
                    return
            except OSError as e:
                if exc_handler != None: exc_handler(e)
                if e.filename == fpath:
                    return
                del groups[cur_idx]
                cur_idx -= 1
            cur_idx += 1
        
        group = _Group(fl_data)
        group.add_entry(fpath)
        groups.append(group)

    #***************#
    # Other methods #
    #***************#
    def get_groups(self):
        res = []
        groups = list(self._groups.values())
        for sub_groups in groups:
            for group in sub_groups:
                res.append(group)
        return res

class _Group:
    def __init__(self, data):
        self.data = data
        self.entries = []
    
    def add_entry(self, entry):
        self.entries.append(entry)
    
    def get_entries(self):
        return self.entries

class _File_Data:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        self.hash = None

    @staticmethod
    def is_equal(self, other, hash_gen):
        if self.size != other.size:
            return False
        if other.hash == None:
            other.hash = _get_hash(other.path, hash_gen)
        if self.hash == None:
            self.hash = _get_hash(self.path, hash_gen)
        return self.hash == other.hash

def _get_hash(fpath, hash_gen=None):
    try:
        if hash_gen == None: hash_gen = hashlib.md5
        read_size = 65536
        fl = open(fpath,'rb')
        hash_fn = hash_gen()
        
        # "Pointers" for speed
        fl_read = fl.read
        hash_update = hash_fn.update

        buff = fl_read(read_size)
        while (len(buff) > 0): 
            hash_update(buff)
            buff = fl_read(read_size)
        fl.close()
        return hash_fn.digest()
    except OSError as e:
        if (e.filename == None):
            msg = "Hashing failure (" + e.strerror + ")" 
            raise OSError(None, msg, fpath)
        raise e

def get_hash_generator(hash_alg):
    # "Pointers" for speed
    hashlib_new = hashlib.new

    def constructor():
        return hashlib_new(hash_alg)
    if hash_alg in hashlib.algorithms_guaranteed:
        constructor = getattr(hashlib, hash_alg)
    return constructor

