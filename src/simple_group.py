from group import Group

class Simple_Group(Group):
    
    def __init__(self):
        Group.__init__(self)
        self._file_size = None
        self._hash = None
   
    @property
    def file_size(self):
        return self._file_size

    @file_size.setter
    def file_size(self, file_size):
        self._file_size = file_size

    @property
    def hash(self):
        return self._hash

    @hash.setter
    def hash(self, hsh):
        self._hash = hsh

