#!/usr/bin/env python3

import argparse
from collections import defaultdict
from datetime import datetime
from glob import glob
import os
import sys

from todotxt import TODOFile, DATE_FMT, todo_from_line

if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: ...")
        sys.exit()

    parser = argparse.ArgumentParser(description='todotxt \'ADD\' script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument('-f', dest='fnpat',
                        default="todo.txt",
                        help="filename prefix to save to")
    parser.add_argument("text", nargs=argparse.REMAINDER,
                        help='text of new todo')

    opts = parser.parse_args()

    if opts.fnpat.endswith(".txt"):
        wildcard = ''
    else:
        wildcard = '*.txt'
    fnl = glob(os.path.join(opts.dir, "{}{}".format(opts.fnpat,
                                                    wildcard)))
    if len(fnl) > 1:
        print("Too many matches for -f: {}".format(", ".join(fnl)))
        sys.exit(1)
    
    todo_file = TODOFile(fnl[0])

    t = todo_from_line(" ".join(opts.text))
    t.set_created_now()
    todo_file.add_todo(t)
    todo_file.save()
