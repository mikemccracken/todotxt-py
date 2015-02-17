
from glob import glob
import os
from pprint import pformat
import sys

from todotxt import TODOFile


if __name__ == '__main__':
    todo_dir = os.environ['TODO_DIR']
    todo_files = glob(todo_dir + "/*.txt")
    for fn in todo_files:
        print(80*'=')
        print(fn)
        f = TODOFile(fn)

        for todo in sorted(f.todos):
            print(todo)
            cmd = input("? ")
            
