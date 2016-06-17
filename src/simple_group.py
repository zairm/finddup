from group import Group

class Simple_Group(Group):
    
    def __init__(self):
        Group.__init__(self)
        self._size = 0
        self._hash = ""
   
    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def hash(self):
        return self._hash

    @hash.setter
    def hash(self, hsh):
        self._hash = hsh

