# finddup
Python script to find and manage duplicate files

Written for python3


## Usage
~~~~
Usage: cmd_handler.py [OPTION]... [FILE]...
Finds duplicate FILEs (defaults to current directory)

Options:
  -h, --help            show this help message and exit
  -r, --recurse         Recursively check files in subdirectories
  -a, --all             Include directories and files begining with .
  -s SORT, --sort=SORT  Sort group by size: ASCE for ascending. DESC for
                        decending
  --lsize               List file size of a single file in each group along
                        with the groups
  --lsizef=MODE         List file size in format MODE (defaults to bytes) as
                        follows;k (kilobytes), m (megabytes)
~~~~
