#!/usr/bin/env python3

import argparse
from collections import defaultdict
from datetime import datetime
import os

from todotxt import TODOFile, DATE_FMT

def todos_grouped_by(alltodos, attr):
    d = defaultdict(list)
    for t in alltodos:
        d[t.__getattribute__(attr)].append(t)
    return d

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='todotxt archive script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument("--days", default=7, type=int,
                        help="Number of days in the past to recap")
    opts = parser.parse_args()

    done_file = TODOFile(os.path.join(opts.dir, "done.txt"))

    todos_by_done_date = todos_grouped_by(done_file.get_todos(),
                                          'done_date')

    for date in sorted(todos_by_done_date.keys())[-opts.days:]:
        todos = todos_by_done_date[date]
        d = datetime.strptime(date, DATE_FMT)
        ds = datetime.strftime(d, "%A, %B %d: ")
        print(ds + "{} completed todos".format(len(todos)))
        print(80 * "-")
        todos_by_project = todos_grouped_by(todos, 'projects_string')
        for p in sorted(todos_by_project.keys()):
            if p == '':
                print(" (No Project)")
            else:
                print(" {}".format(p))
            proj_todos = todos_by_project[p]
            print("\n".join(["   {}".format(t.get_string(show_done=False))
                             for t in proj_todos]))
            print()
        print()
