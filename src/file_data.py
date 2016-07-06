import hashlib

hash_algs = sorted(hashlib.algorithms_available)
_HASH_READ_SIZE = 65536

class File_Data:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        self._hash = None
        self._partial = None

    @staticmethod
    def is_equal_hash(self, other, hash_gen):
        if other._partial == None:
            other._partial = _get_hash(other.path, hash_gen, _HASH_READ_SIZE, True)
            if other.size <= _HASH_READ_SIZE:
                other._hash = other._partial
                del other.path
        if self._partial == None:
            self._partial = _get_hash(self.path, hash_gen, _HASH_READ_SIZE, True)
            if self.size <= _HASH_READ_SIZE:
                self._hash = self._partial
                del self.path
        if self._partial != other._partial: return False
        if other._hash == None:
            other._hash = _get_hash(other.path, hash_gen)
            del other.path
        if self._hash == None:
            self._hash = _get_hash(self.path, hash_gen)
            del self.path
        return self._hash == other._hash

def _get_hash(fpath, hash_gen=None, read_size=65536, partial=False):
    # Help credit: http://stackoverflow.com/a/3431835
    
    # We could place the try in a helper but why have such a simple call
    # negatively touching performance?
    try:
        if hash_gen == None: hash_gen = hashlib.md5
        fl = open(fpath,'rb')
        hash_fn = hash_gen()
        
        if partial:
            hash_fn.update(fl.read(read_size))
        else:
            # "Pointers" for speed
            fl_read, hash_update = fl.read, hash_fn.update
    
            buff = fl_read(read_size)
            while (buff):
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

