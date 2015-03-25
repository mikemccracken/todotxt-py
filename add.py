#!/usr/bin/env python3

import argparse
from collections import defaultdict
from datetime import datetime
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
    parser.add_argument("text", nargs=argparse.REMAINDER,
                        help='text of new todo')

    opts = parser.parse_args()

    todo_file = TODOFile(os.path.join(opts.dir, "todo.txt"))

    t = todo_from_line(" ".join(opts.text))
    t.set_created_now()
    todo_file.add_todo(t)
    todo_file.save()
