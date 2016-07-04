import hashlib

hash_algs = sorted(hashlib.algorithms_available)

class File_Data:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        self.hash = None

    @staticmethod
    def is_equal(self, other, hash_gen):
        # Because we use a dict for size in the classifier, this comparison is 
        # unnecessary. So we just take a small performance boost
        #if self.size != other.size:
        #    return False

        if other.hash == None:
            other.hash = _get_hash(other.path, hash_gen)
            del other.path
        if self.hash == None:
            self.hash = _get_hash(self.path, hash_gen)
            del self.path
        return self.hash == other.hash


def _get_hash(fpath, hash_gen=None):
    # Help credit: http://stackoverflow.com/a/3431835
    
    # We could place the try in a helper but why have such a simple call
    # negatively touching performance?
    try:
        if hash_gen == None: hash_gen = hashlib.md5
        read_size = 65536 
        fl = open(fpath,'rb')
        hash_fn = hash_gen()    
        # "Pointers" for speed
        fl_read = fl.read
        hash_update = hash_fn.update

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

