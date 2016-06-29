from file_data import File_Data
class Group:
    
    def __init__(self, group_data):
        self._entries = [group_data.path]
        self._group_data = group_data

    def add_entry(self, entry_data):
        #if (self._group_data == entry_data):
            # XXX
            # entry_data should really have a method to return the "Object" for
            # which it contains data (which, in general, we should make a copy
            # of here). We just keep dependancy on File_Data (as opposed to a
            # more general "Object_data" that the interface allows for)
            # because it's sufficient for our purposes atm.
            #
            # "Group" really shouldn't depend on File_Data as it currently does
            self._entries.append(entry_data.path)
        #    return True
        #return False

    def get_entries(self):
        return self._entries

    @property
    def data(self):
        return self._group_data

