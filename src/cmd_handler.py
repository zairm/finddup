import optparse, os, sys
from simple_classifier import Simple_Classifier

def main():
    usage = "Usage: %prog [OPTION]... [FILE]...\n" \
            + "Finds duplicate files in FILEs and outputs them in groups\n" \
            + "Each FILE can a path to a directory or a file\n" \
            + "Given FILEs will not be filtered out given any OPTION\n" \
            + "Ignores all symlinks"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(recurse=False, hidden=False, sort="", list_size=False, \
        size_format="", min_size=0, max_size=0)

    parser.add_option("-r", "--recurse", action="store_true", dest="recurse",
        help="Recursively check files in subdirectories")
    parser.add_option("-a", "--all", action="store_true", dest="hidden",
        help="Include directories and files begining with .")
    parser.add_option("-s", "--sort", action="store", type="string", dest="sort",
        help="Sort group by size: ASCE for ascending. DESC for decending")
    parser.add_option("--lsize", action="store_true", dest="list_size",
        help="List file size of a single file in each group along with the groups\n")
    parser.add_option("--lsizef", action="store", type="string", dest="size_format", \
        metavar="MODE", help="If --lsize if given; list file size in format " \
        + "MODE (defaults to bytes) as follows; k (kilobytes), m (megabytes)")
    parser.add_option("--minsize", action="store", type="int", dest="min_size",
        help="Only check files with byte size atleast MIN (MIN = 0 is ignored)")
    parser.add_option("--maxsize", action="store", type="int", dest="max_size",
        help="Only check files with byte size at most MAX (MAX = 0 is ignored)")

    (opts, paths) = parser.parse_args()
    _check_opts(opts)
    if (not paths):
        # TODO Replace this with a more helpful error message
        parser.print_help()
        return
    classifier = Simple_Classifier()
    add_files(paths, classifier, opts)
    print_result(classifier, opts)


def add_files(paths, classifier, opts):

    for path in paths:
        if not os.path.lexists(path):
            # The path is invalid (broken symlinks are considered valid)
            # This is too useful to require verbose
            error_text = "Skipping invalid path: " + path
            print(error_text, file=sys.stderr)
            continue

        if _is_symlink(path, opts):
            continue

        if os.path.isfile(path):
            (succ, file_size) = _file_size(path, opts)
            if (not succ):
                continue
            _insert_file((path, file_size), classifier, opts)

        if os.path.isdir(path):
            add_dir_files(path, classifier, opts)

def add_dir_files(dr, classifier, opts):
    if not opts.recurse:
        entries = []
        (succ, entries) = _safe_op(os.listdir, [dr], opts)
        if (not succ):
            return
        
        for entry in entries:
            entry_path = os.path.join(dr, entry)
            if _is_symlink(entry_path, opts):
                continue
            if (_keep_entry(entry, opts) and os.path.isfile(entry_path)):
                (succ, file_size) = _file_size(entry_path, opts)
                if (not succ) or (not _is_right_size(file_size, opts)):
                    continue
                _insert_file((entry_path, file_size), classifier, opts)

    else:
        for root,dirs,files in os.walk(dr):
            all_dirs = [dr for dr in dirs]

            for fl in files:
                if _is_symlink(os.path.join(root, fl), opts):
                    continue
                if _keep_entry(fl, opts):
                    fl_path = os.path.join(root, fl)
                    (succ, file_size) = _file_size(fl_path, opts)
                    if (not succ) or (not _is_right_size(file_size, opts)):
                        continue
                    _insert_file((fl_path, file_size), classifier, opts)
            for folder in all_dirs:
                # os.walk avoids symlinks
                if not _keep_entry(folder, opts):
                    dirs.remove(folder)

def _file_size(fpath, opts):
    return _safe_op(os.path.getsize, [fpath], opts)


def _is_symlink(path, opts):
    if os.path.islink(path):
        # TODO If verbose
        if (True):
            error_text = "Skipping symlink: '" + path + "'"
            print(error_text, file=sys.stderr)
        return True
    return False

def _is_right_size(size, opts):
    if (opts.min_size > 0 and size < opts.min_size):
        return False
    if (opts.max_size > 0 and size > opts.max_size):
        return False
    return True

def _keep_entry(entry, opts):
    if (not opts.hidden) and entry[0] == '.':
        return False
    return True

def print_result(classifier, opts):
    cur_group = 1
    (outstr, groupstr) = ("", "")
    groups = classifier.get_groups()
    if (opts.sort == "ASCE"):
        groups.sort(key= lambda group: group.size)
    if (opts.sort == "DESC"):
        groups.sort(key= lambda group: (-1)*group.size)

    for group in groups:
        # TODO make number of entries (len(group.get_entries()) a property
        if len(group.get_entries()) < 2:
            continue
        groupstr = _group_header(cur_group, group, opts)
        groupstr += _group_file_paths(group, opts) + "\n"
        outstr += groupstr
        cur_group += 1

    if cur_group == 1:
        outstr = "No Matches found\n"
    print(outstr, end="")

def _group_header(g_num, group, opts):
    header = "Group " + str(g_num)
    if (opts.list_size):
        header += " " + _format_filesize(group.size, opts)
    header += ":\n----\n"
    return header

def _group_file_paths(group, opts):
    paths_str = ""
    for fpath in group.get_entries():
        paths_str += fpath + "\n"
    return paths_str

def _format_filesize(size, opts):
    if (opts.size_format == "k"):
        return "{0:.2f}".format(size / 1024.0)
    if (opts.size_format == "m"):
        return "{0:.2f}".format(size / 1048576.0)
    return str(size)

def _check_opts(opts):
    outstr = ""
    if (opts.max_size < 0):
        outstr += "ERROR: --maxsize cannot be set to a negative number\n"
    if (opts.max_size > 0 and opts.min_size > 0 and opts.max_size < opts.min_size):
        outstr += "ERROR: --maxsize num may not be less than --minsize num" 
    if (outstr != ""):
        print(outstr, file=sys.stderr)
        sys.exit()

def _insert_file(file_data, classifier, opts):
    # FIXME if this fails due to computation of a hash, the hash might be of a
    # file already added, not the one refering to fpath
    try:
        classifier.insert(file_data[0], file_data[1])
    except Exception as e:
        _exception_msg(e, opts)

# TODO Use _safe_op for os and os.path fns as a defense against exceptions
# (make sure add returns, continue, or whatever as needed)
def _safe_op(op, args, opts):
    try:
        return (True, op(*args))
    except Exception as e:
        _exception_msg(e, opts)
        return (False, 0)

def _exception_msg(e, opts):
    # TODO If verbose
    if (True):
        err_msg = ' '.join(str(e).split(' ')[2:])
        print(err_msg, file=sys.stderr)

if __name__ == "__main__":
    main()

