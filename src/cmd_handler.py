import optparse, os, sys
from file_classifier import File_Classifier, hash_algs as fc_hash_algs
import stat

# TODO Most (if not all) permission exceptions seem to occour in classifier's
# insert. Check permissions before senselessly adding a file to claissifier

def main():
    def verbose_callback(option, opt, value, parser):
        def verbose_msgr(e):
            try:
                err_msg = e.strerror + ": '" + e.filename + "'"
                print(err_msg, file=sys.stderr)
            except Exception as e:
                raise e
        parser.values.err_msgr = verbose_msgr

    usage = "Usage: %prog [OPTION]... [FILE]...\n" \
            + "Finds duplicate regular files in FILEs and outputs them in groups\n" \
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
        choices=fc_hash_algs, dest="hash_alg", metavar="ALG",
        help="Use one of the following algorithms to establish file " \
        + "equivalence (defaults to md5): " + " ".join(fc_hash_algs))

    (opts, paths) = parser.parse_args()
    _check_size(opts)
    if (not paths):
        paths = [os.getcwd()]
    classifier = File_Classifier(opts.hash_alg)
    opts.visited = set()
    add_files(paths, classifier, opts)
    print_result(classifier, opts)


############################
# Duplicate file detection #
############################

def add_files(paths, classifier, opts):
    for path in paths:
        try:
            p_stat = os.lstat(path)
        except OSError as e:
            try: opts.err_msgr(e)
            except Exception: pass
            continue
        if stat.S_ISLNK(p_stat.st_mode):
            continue
        if stat.S_ISDIR(p_stat.st_mode):
            if p_stat.st_ino in opts.visited:
                continue
            opts.visited.add(p_stat.st_ino)
            add_dir_files(path, classifier, opts)
        if stat.S_ISREG(p_stat.st_mode):
            classifier.insert(path, p_stat.st_size)

def add_dir_files(dr, classifier, opts): 
    if opts.recurse:
        for root,dirs,files in os.walk(dr):
            # os.walk avoids symlinks
            _hidden_entryname_filter(opts, files, dirs)
            
            all_dirs = [dr for dr in dirs]
            for dr in all_dirs:
                try:
                    d_stat = os.lstat(os.path.join(root, dr))
                except OSError as e:
                    try: opts.err_msgr(e)
                    except Exception: pass
                    dirs.remove(dr)
                    continue
                if d_stat.st_ino in opts.visited:
                    dirs.remove(dr)
                else:
                    opts.visited.add(d_stat.st_ino)

            for fl in files:
                fl_path = os.path.join(root, fl)
                _add_file(fl_path, classifier, opts)
    else:
        try:
            entries = os.listdir(dr)
        except OSError as e:
            try: opts.err_msgr(e)
            except Exception: pass
            return
        
        _hidden_entryname_filter(opts, entries)
        for entry in entries:
            entry_path = os.path.join(dr, entry)
            _add_file(entry_path, classifier, opts)

def _add_file(fl_path, classifier, opts):
    try:
        fl_stat = os.lstat(fl_path)
    except OSError as e:
        try: opts.err_msgr(e)
        except Exception: pass
        return
    fl_size = fl_stat.st_size
    # Must be a regular, non-symlink file with appropriate size
    if (stat.S_ISREG(fl_stat.st_mode) and (not stat.S_ISLNK(fl_stat.st_mode)) \
        and _filesize_filter(fl_size, opts)):
            classifier.insert(fl_path, fl_size, opts.err_msgr)

# -------------------------------
# "Filter" helpers for the above
#--------------------------------

def _hidden_entryname_filter(opts, *entryname_arrays):
    if opts.hidden:
        return
    for entries in entryname_arrays:
        new_entries = [entry for entry in entries]
        for entry in new_entries:
            if entry[0] == '.':
                entries.remove(entry)

def _filesize_filter(size, opts):
    if (opts.min_size > 0 and size < opts.min_size):
        return False
    if (opts.max_size > 0 and size > opts.max_size):
        return False
    return True


#########################
# Result printing logic #
#########################

def print_result(classifier, opts):
    cur_group = 1
    (outstr, groupstr) = ("", "")
    
    nontrival_group = lambda group: len(group) > 1
    groups = list(filter(nontrival_group,  classifier.get_groups()))
    
    if (opts.sort in ["DESC", "ASCE"]):
        rev = opts.sort == "DESC"
        key = lambda group: group.data.size
        groups = sorted(groups, key=key, reverse=rev)

    
    group_str = lambda idx, group: "%s%s" % (_group_header(idx, group, opts), str(group))
    groups = map(group_str, range(1, len(groups)+1), groups)
    outstr = "\n\n".join(groups)
    
    if outstr == "": outstr = "No Matches found"
    print(outstr)

def _group_header(g_num, group, opts):
    header = "G " + str(g_num)
    if (opts.list_size):
        header += " - " + _format_filesize(group.data.size, opts)
    header += "\n"
    return header

def _group_file_paths(group, opts):
    paths_str = ""
    for fpath in group.get_entries():
        paths_str += fpath + "\n"
    return paths_str

# TODO Make format precision an option?
divs = {"b" : 1.0,
        "k"  : 1024.0,
        "m"  : 1048576.0}
def _format_filesize(size, opts):
    prec = str(0)
    formatter = "{0:." + prec + "f}"
    return formatter.format(size/divs[opts.size_format]) 

def _check_size(opts):
    outstr = ""
    if (opts.max_size < 0):
        outstr += "ERROR: --maxsize cannot be set to a negative number\n"
    if (opts.max_size > 0 and opts.min_size > 0 and opts.max_size < opts.min_size):
        outstr += "ERROR: --maxsize num may not be less than --minsize num" 
    if (outstr != ""):
        print(outstr, file=sys.stderr)
        sys.exit()

if __name__ == "__main__":
    main()

