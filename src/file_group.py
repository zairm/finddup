
class File_Group(list):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "\n".join(self)

