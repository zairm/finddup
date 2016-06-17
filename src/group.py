"""
Groups for files to fall under
"""

class Group:
    
    def __init__(self):
        self.fpaths = []

    def add_entry(self,fpath):
        self.fpaths.append(fpath)

    def get_entries(self):
        return self.fpaths

