import optparse, os, sys
import safefn
import simple_classifier
import time
# import file_data

# TODO Most (if not all) permission exceptions seem to occour in classifier's
# insert. Check permissions before senselessly adding a file to claissifier

def main():
    def empty_fn(e):
        pass
    def verbose_callback(option, opt, value, parser):
        def verbose_msgr(e):
            if e.strerror == None or e.filename == None:
                raise Exception("Unexcpected exception encountered")
            err_msg = e.strerror + ": '" + e.filename + "'"
            print(err_msg, file=sys.stderr)
        parser.values.err_msgr = verbose_msgr

    usage = "Usage: %prog [OPTION]... [FILE]...\n" \
            + "Finds duplicate files in FILEs and outputs them in groups\n" \
            + "Each FILE can a path to a directory or a file\n" \
            + "If no FILE is provided current working directory is used\n" \
            + "Given FILEs will not be filtered out given any OPTION\n" \
            + "Ignores all symlinks"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(recurse=False, hidden=False, sort=None, list_size=False, \
        size_format="b", min_size=0, max_size=0, err_msgr=None, hash_alg="md5")

    parser.add_option("-r", "--recurse", action="store_true", dest="recurse",
        help="Recursively check files in subdirectories")
    parser.add_option("-a", "--all", action="store_true", dest="hidden",
        help="Include directories and files begining with .")
    parser.add_option("-v", "--verbose", action="callback", callback=verbose_callback,
        help="Output all errors to stderr as they occour (disabled by default)")
    sort_opts = ["ASCE", "DESC"]
    parser.add_option("-s", "--sort", action="store", type="choice", choices=sort_opts,
        dest="sort", help="Sort group by size: ASCE for ascending. DESC for decending")
    parser.add_option("--lsize", action="store_true", dest="list_size",
        help="List file size of a single file in each group along with the groups\n")
    sizef_opts = ["b", "k", "m"]
    parser.add_option("--lsizef", action="store", type="choice", choices=sizef_opts,
        dest="size_format", metavar="MODE", 
        help="If --lsize if given; list file size in format " \
        + "MODE as follows; b (bytes - default), k (kilobytes), m (megabytes)")
    parser.add_option("--minsize", action="store", type="int", dest="min_size",
        help="Only check files with byte size atleast MIN (MIN = 0 is ignored)")
    parser.add_option("--maxsize", action="store", type="int", dest="max_size",
        help="Only check files with byte size at most MAX (MAX = 0 is ignored)")
    parser.add_option("--alg", action="store", type="choice", 
        choices=simple_classifier.hash_algs, dest="hash_alg", metavar="ALG",
        help="Use one of the following algorithms to establish file " \
        + "equivalence (defaults to md5): " + " ".join(simple_classifier.hash_algs))

    (opts, paths) = parser.parse_args()
    _check_opts(opts)
    if (not paths):
        paths = [os.getcwd()]
    hash_gen = simple_classifier.get_hash_generator(opts.hash_alg)
    classifier = simple_classifier.Simple_Classifier(hash_gen)
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
        (succ, islink) = _is_symlink(path, opts)
        if (not succ) or islink:
            continue

        (succ, isfile) = safefn.isfile(path, opts.err_msgr)
        if succ and isfile:
            (succ, file_size) = safefn.getsize(path, opts.err_msgr)
            if (not succ):
                continue
            _insert_file((path, file_size), classifier, opts)

        (succ, isdir) = safefn.isdir(path, opts.err_msgr)
        if succ and isdir:
            add_dir_files(path, classifier, opts)

def add_dir_files(dr, classifier, opts):
    # "Pointers" for speed
    os_path_join = os.path.join
    safefn_getsize = safefn.getsize


    if not opts.recurse:
        entries = []
        (succ, entries) = safefn.listdir(dr, opts.err_msgr)
        if (not succ):
            return
        
        for entry in entries:
            entry_path = os_path_join(dr, entry)
            (succ, islink) = _is_symlink(entry_path, opts)
            if (not succ) or islink:
                continue
            (succ, isfile) = safefn.isfile(entry_path, opts.err_msgr)
            if (_keep_entry(entry, opts) and succ and isfile):
                (succ, file_size) = safefn_getsize(entry_path, opts.err_msgr)
                if (not succ) or (not _is_right_size(file_size, opts)):
                    continue
                _insert_file((entry_path, file_size), classifier, opts)

    else:
        for root,dirs,files in os.walk(dr):
            all_dirs = [dr for dr in dirs]

            for fl in files:
                fl_path = os_path_join(root, fl)
                (succ, islink) = _is_symlink(fl_path, opts)
                if (not succ) or islink:
                    continue
                if _keep_entry(fl, opts):
                    (succ, file_size) = safefn_getsize(fl_path, opts.err_msgr)
                    if (not succ) or (not _is_right_size(file_size, opts)):
                        continue
                    _insert_file((fl_path, file_size), classifier, opts)
            for folder in all_dirs:
                # os.walk avoids symlinks
                if not _keep_entry(folder, opts):
                    dirs.remove(folder)

def _is_symlink(path, opts):
    (succ, res) = safefn.islink(path, opts.err_msgr)
    if succ and res:
        e = Exception()
        e.strerror = "Skipping symlink"
        e.filename = path
        if opts.err_msgr != None: opts.err_msgr(e)
    return (succ, res)

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
        groups.sort(key= lambda group: group.data.size)
    if (opts.sort == "DESC"):
        groups.sort(key= lambda group: (-1)*group.data.size)

    for group in groups:
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
        header += " " + _format_filesize(group.data.size, opts)
    header += ":\n----\n"
    return header

def _group_file_paths(group, opts):
    paths_str = ""
    for fpath in group.get_entries():
        paths_str += fpath + "\n"
    return paths_str

# TODO Make format precision an option?
def _format_filesize(size, opts):
    prec = str(0)
    formatter = "{0:." + prec + "f}"
    divs = {"b" : 1.0,
            "k"  : 1024.0,
            "m"  : 1048576.0}
    return formatter.format(size/divs[opts.size_format]) 

def _check_opts(opts):
    outstr = ""
    if (opts.max_size < 0):
        outstr += "ERROR: --maxsize cannot be set to a negative number\n"
    if (opts.max_size > 0 and opts.min_size > 0 and opts.max_size < opts.min_size):
        outstr += "ERROR: --maxsize num may not be less than --minsize num" 
    if (outstr != ""):
        print(outstr, file=sys.stderr)
        sys.exit()

# TODO Handle the exceptions in a more elegant way. Probably need to change
# classifier.insert a bit
def _insert_file(file_data, classifier, opts):
    classifier.insert(file_data[0], file_data[1], opts.err_msgr)

if __name__ == "__main__":
    t0 = time.time()
    main()
    t1 = time.time()
    print("\n" + str(t1-t0) + "\n")

