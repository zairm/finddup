from classifier import Classifier
from group import Group

class Dummy_Classifier(Classifier):
    
    def __init__(self):
        self._groups = []
        self._i = 0
        for i in range(0,5):
            self._groups.append(Group())

    def insert(self, fpath):
        self._groups[self._i].add_entry(fpath)
        self._i = (self._i + 1) % 5

    def get_groups(self):
        return self._groups
