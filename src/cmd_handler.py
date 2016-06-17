import optparse, os, sys
from simple_classifier import Simple_Classifier

def main():
    usage = "Usage: %prog [OPTION]... [FILE]...\n" \
            + "Finds duplicate files in FILEs and outputs them in groups\n" \
            + "Each FILE can a path to a directory or a file\n" \
            + "Given FILEs will not be filtered out given any OPTION"
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
    check_opts(opts)
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
            error_text = "Skipping invalid path: " + path
            print(error_text, file=sys.stderr)
        # FIXME
        if os.path.islink(path):
            error_text = "1. Skipping syslink: " + path
            print(error_text, file=sys.stderr)

        if os.path.isfile(path):
            classifier.insert(path)

        if os.path.isdir(path):
            add_dir_files(path, classifier, opts)

def add_dir_files(dr, classifier, opts):
    if not opts.recurse:
        # Do something cleaner than this try (if else part also need osmething similar)
        try:
            for entry in os.listdir(dr):
                entry_path = os.path.join(dr, entry)
                if (keep_entry(entry, opts) and os.path.isfile(entry_path)):
                    # FIXME Do this in a filtering function
                    # If we need to get size we may aswell pass it to insert (Make adjustments for this)
                    file_size = 0
                    if (opts.min_size > 0):
                        # Nothing changes if opts.min_size == 0 but we want to avoid
                        # the getsize call if possible
                        file_size = os.path.getsize(entry_path)
                        if (file_size < opts.min_size):
                            continue
                    if (opts.max_size > 0):
                        # max_size 0 is ignored. less is not allowed (change to ignore if less?) XXX
                        if not file_size: file_size = os.path.getsize(entry_path)
                        if (file_size > opts.max_size):
                            continue
                    # ########
                    classifier.insert(entry_path)
        except:
            outstr = "Permission denied for " + dr
            print(outstr, file=sys.stderr)

    else:
        for root,dirs,files in os.walk(dr):
            all_dirs = [dr for dr in dirs]

            # TODO Make sure fl or dr cannot be a symlink
            for fl in files:
                if os.path.islink( os.path.join(root, fl) ):
                    error_text = "2. Skipping syslink: " + os.path.join(root, fl)
                    print(error_text, file=sys.stderr)
                    continue
                if keep_entry(fl, opts):
                    # FIXME Same as above try statement. + Obviously repeated code
                    # that belongs in the same place.
                    file_size = 0
                    if (opts.min_size > 0):
                        file_size = os.path.getsize( os.path.join(root, fl) )
                        if (file_size < opts.min_size):
                            continue
                    if (opts.max_size > 0):
                        if not file_size: file_size = os.path.getsize( os.path.join(root, fl) )
                        if (file_size > opts.max_size):
                            continue
                    # ##########
                    classifier.insert( os.path.join(root,fl) )
            for folder in all_dirs:
                if not keep_entry(folder, opts):
                    dirs.remove(folder)

def keep_entry(entry, opts):
    if (not opts.hidden) and entry[0] == '.':
        return False
    return True

def print_result(classifier, opts):
    cur_group = 1
    (outstr, groupstr) = ("", "")
    groups = classifier.get_groups()
    # XXX Temporary. These only work for classifiers with _size in group
    if (opts.sort == "ASCE"):
        groups.sort(key= lambda group: group.size)
    if (opts.sort == "DESC"):
        groups.sort(key= lambda group: (-1)*group.size)
    for group in groups:
        files = group.get_entries()
        if len(files) < 2:
            continue
        # XXX Temporary. This only works of classifier with _size in group
        groupstr = "Group " + str(cur_group)
        if (opts.list_size):
            groupstr += " " + format_filesize(group.size, opts)
        groupstr += ":\n----\n"

        for fpath in files:
            groupstr += fpath + "\n"
        outstr += groupstr + "\n"
        cur_group += 1

    if cur_group == 1:
        outstr = "No Matches found\n"
    print(outstr, end="")

def format_filesize(size, opts):
    if (opts.size_format == "k"):
        return "{0:.2f}".format(size / 1024.0)
    if (opts.size_format == "m"):
        return "{0:.2f}".format(size / 1048576.0)
    return str(size)

def check_opts(opts):
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

