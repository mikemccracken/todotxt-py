#!/usr/bin/env python3

import argparse
from collections import defaultdict
from datetime import datetime
import os
import sys

from todotxt import TODOFile, DATE_FMT

if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: ...")
        sys.exit()

    parser = argparse.ArgumentParser(description='todotxt \'DO\' script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument("N", type=int,
                        metavar='line number',
                        help="line number of todo to edit (starting at 1)")

    opts = parser.parse_args()

    todo_file = TODOFile(os.path.join(opts.dir, "todo.txt"))

    todos = todo_file.get_todos()

    num = opts.N - 1
    if num > len(todos):
        print("Error: there are only {} todos in {}".format(len(todos),
                                                            filename))
        print("they are: \n{}".format(list(map(str, f.get_todos()))))
        sys.exit(1)

    t = todos[num]
    if t.done:
        print("Already done!")
        sys.exit()

    t.done = True
    print("done: {}".format(str(t)))
    todo_file.save()
