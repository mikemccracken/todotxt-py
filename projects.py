from todotxt.project import ProjectFile

import argparse
import os
import sys

if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: review script. use -h for real usage")
        sys.exit()

    parser = argparse.ArgumentParser(description='todotxt review script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument('-f', dest='filename', default='projects',
                        help="Path to projects file")
    opts = parser.parse_args()

    fn = os.path.join(opts.dir, opts.filename)
    pf = ProjectFile(fn)
    pf.save()
    print("saved project list that looked like this:")
    print(str(pf))

    print("sort tuples like this:")
    for p in pf._projects.values():
        print (p._get_sort_tuple(p))
