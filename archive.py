#!/usr/bin/env python3

import argparse
from glob import glob
import os
import sys

from todotxt import TODOFile, todo_from_line


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='todotxt archive script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")

    opts = parser.parse_args()
    print("Archiving in {}".format(opts.dir))
    todo_files = glob(opts.dir + "/*.txt")
    done_file = TODOFile(os.path.join(opts.dir, "done.txt"))
    for fn in todo_files:
        bfn = os.path.basename(fn)
        if bfn == "done.txt":
            continue
        f = TODOFile(fn)
        print("{:<18}: ".format(bfn), end="")
        archived = 0
        for todo in f.get_todos():
            if not todo.done:
                continue
            done_file.add_todo(todo)
            f.delete_todo(todo)
            archived += 1
        try:
            done_file.save()
            f.save()
        except:
            print("error saving.")
            sys.exit(1)
        print("archived {} todos.".format(archived))
