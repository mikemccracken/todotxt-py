
from pprint import pformat
import sys

from todotxt import TODOFile

if __name__ == '__main__':
    for fn in sys.argv[1:]:
        print('='*80)
        print(fn)
        f = TODOFile(fn)
        print(f)
        print("projects: {}".format(pformat(f.projects)))
        print("contexts: {}".format(pformat(f.contexts)))
