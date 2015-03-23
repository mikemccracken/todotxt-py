#!/usr/bin/env python3

import argparse
import os
import readline
import sys

readline.parse_and_bind("TAB: complete")

#libedit style
#readline.parse_and_bind("bind -e")

from todotxt import TODOFile, todo_from_line

# NOTE -- copied and pasted from archive.py, should consolidate at some point

def completer(text, idx):
    print("text is '{}'".format(text))
    print("startswith? {}".format(text.startswith('@')))
    if text.startswith('@'):
        print("huh")
        cs = ['foo', 'bar', 'baz']
        cs.append('yearch')
        print('cs is {}'.format(cs))
        if idx < len(cs):
            return cs[idx]
        else:
            return None
    return None

def do_edit(todo, f):
    "Edit the todo"
    def hook():
        readline.insert_text(str(todo))
    readline.set_startup_hook(hook)
    old_delims = readline.get_completer_delims()
    new_delims = old_delims.replace('@', '')
    new_delims = new_delims.replace('+', '')
    new_delims = new_delims.replace('#', '')
    readline.set_completer_delims(new_delims)
    readline.set_completer(completer)
    newval = input("editing: ")
    readline.set_startup_hook(None)
    readline.set_completer(None)
    readline.set_completer_delims(old_delims)
    if newval != str(todo):
        newtodo = todo_from_line(newval)
        f.replace_todo(todo,
                       newtodo)
        f.save()
        print("Saved :'{}'".format(str(newtodo)))


if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: ...")
        sys.exit()


    parser = argparse.ArgumentParser(description='todotxt single edit script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument('--filename', default='todo.txt',
                        help="Which file to edit")
    parser.add_argument("N", type=int,
                        metavar='line number',
                        help="line number of todo to edit (starting at 1)")
    opts = parser.parse_args()

    filename = os.path.join(opts.dir, opts.filename)
    
    f = TODOFile(filename)
    todos = f.get_todos()

    num = opts.N - 1
    if num > len(todos):
        print("Error: there are only {} todos in {}".format(len(todos),
                                                            filename))
        print("they are: \n{}".format(list(map(str, f.get_todos()))))
        sys.exit(1)
        
    do_edit(todos[num], f)

