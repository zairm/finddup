from file_group import File_Group
from file_data import File_Data, get_hash_generator, hash_algs

class File_Classifier:

    def __init__(self, hash_alg):
        self._groups = {}
        self._hash_gen = get_hash_generator(hash_alg)

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
        fl_data = File_Data(fpath, size)
        cur_idx = 0
        
        # "Pointers" for speed
        iseq = File_Data.is_equal
        groups = self._groups
        hash_gen = self._hash_gen

        try:
            groups = groups[size]
        except KeyError:
            group = File_Group(fl_data)
            group.append(fpath)
            groups[size] = [group]
            return

        while (cur_idx < len(groups)):
            try:
                group = groups[cur_idx]
                if (iseq(group.data, fl_data, hash_gen)):
                    group.append(fpath)
                    return
            except OSError as e:
                if exc_handler != None: exc_handler(e)
                if e.filename == fpath:
                    return
                del groups[cur_idx]
                cur_idx -= 1
            cur_idx += 1
        
        group = File_Group(fl_data)
        group.append(fpath)
        groups.append(group)

    #***************#
    # Other methods #
    #***************#
    def get_groups(self):
        res = []
        for sub_groups in iter(self._groups.values()):
            res.extend(sub_groups)
        return res

