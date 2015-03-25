#!/usr/bin/env python3

import argparse
from collections import defaultdict
from datetime import datetime
import os
import sys

from todotxt import TODOFile, DATE_FMT

def todos_grouped_by(alltodos, attr):
    d = defaultdict(list)
    for t in alltodos:
        d[t.__getattribute__(attr)].append(t)
    return d

if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: ...")
        sys.exit()

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
        if len(todos) == 0:
            continue

        todos_by_hour = defaultdict(list)
        for t in todos:
            todos_by_hour[t.done_datetime.hour].append(t)

        hours = sorted(todos_by_hour.keys())
        start_hour = min(7, hours[0])
        end_hour = max(17, hours[-1])

        for hour in range(start_hour, end_hour+1):
            if hour not in todos_by_hour:
                print("  {:0>2}:00 \N{HORIZONTAL ELLIPSIS}".format(hour % 12))
            else:
                for t in todos_by_hour[hour]:
                    print("  {} {}".format(t.done_datetime.strftime("%I:%M"),
                        t.get_string(show_done=False, show_tags=False)))

        print()
