import hashlib


hash_algs = sorted(list(hashlib.algorithms_available))

class File_Data:
    
    def __init__(self, path, hasher, size=None, hash=None):
        self._path = path
        self._size = size
        self._hash = hash

    def reset_hasher(self, hasher):
        self._hasher = hasher
        self._hash = None

    def __eq__(self, other):
        if self.size != other.size:
            return False
        if self.hash != other.hash:
            return False
        return True

    def __ne__(self, other):
        return not (self == other)

    @property
    def size(self):
        if (self._size == None):
            self._size = os.path.getsize(self.path)
        return self._size

    @property
    def hash(self):
        if (self._hash == None):
            self._hash = self._hasher(self.path)
            # del self._hasher
        return self._hash

    @property
    def path(self):
        return self._path


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

