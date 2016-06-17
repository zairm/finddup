import optparse, os, sys
#from dummy_classifier import Dummy_Classifier
from simple_classifier import Simple_Classifier

def main():
    usage = "Usage: %prog [OPTION]... [FILE]...\n" \
            + "Finds duplicate FILEs (defaults to current directory)"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(recurse=False, hidden=False, sort="", list_size=False, \
        size_format="")

    parser.add_option("-r", "--recurse", action="store_true", dest="recurse",
        help="Recursively check files in subdirectories")
    parser.add_option("-a", "--all", action="store_true", dest="hidden",
        help="Include directories and files begining with .")
    parser.add_option("-s", "--sort", action="store", type="string", dest="sort",
        help="Sort group by size: ASCE for ascending. DESC for decending")
    parser.add_option("--lsize", action="store_true", dest="list_size",
        help="List file size of a single file in each group along with the groups\n")
    parser.add_option("--lsizef", action="store", type="string", dest="size_format", \
        metavar="MODE", help="List file size in format MODE (defaults to bytes) as follows;" + \
                "k (kilobytes), m (megabytes)")

    (opts, paths) = parser.parse_args()
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
                    classifier.insert(entry_path)
        except:
            outstr = "Permission denied for " + dr
            print(outstr, file=sys.stderr)

    else:
        for root,dirs,files in os.walk(dr):
            all_dirs = [dr for dr in dirs]

            # TODO Make sure fl or dr cannot be a symlink
            for fl in files:
                # FIXME
                if os.path.islink( os.path.join(root, fl) ):
                    error_text = "2. Skipping syslink: " + os.path.join(root, fl)
                    print(error_text, file=sys.stderr)
                    continue
                if keep_entry(fl, opts):
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

if __name__ == "__main__":
    main()
