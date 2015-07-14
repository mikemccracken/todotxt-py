#!/usr/bin/env python3

import argparse
import cmd
from collections import OrderedDict
from glob import glob
import os
import readline
import sys

readline.parse_and_bind("TAB: complete")

#libedit style
#readline.parse_and_bind("bind -e")

from todotxt import TODO, TODOFile, todo_from_line

IDXCHAR = "\N{ELECTRIC LIGHT BULB}  "


class ReviewShell(cmd.Cmd):
    prompt = "\N{HOT BEVERAGE}  "

    def __init__(self, todo_dir, review_type='daily'):
        super().__init__()
        todo_files = glob(todo_dir + "/*.txt")
        self.all_files = {}
        for fn in todo_files:
            f = TODOFile(fn)
            self.all_files[os.path.basename(fn)] = f
        self.completed_files = []

        files = [('todo.txt',
                  IDXCHAR + "Review current todos and mark as done or defer "
                  "to later."),
                 ('waiting.txt',
                  IDXCHAR + "Review waiting tasks and mark as received or "
                  "move to todo."),
                 ('next-week.txt',
                  IDXCHAR + "Review tasks deferred from last week and move "
                  "to todo as they become urgent."),
                 ('someday-maybe.txt',
                  IDXCHAR + "Review someday ideas. "
                  "Time to schedule something?")]
        self.to_review = OrderedDict(files)
        for fn in self.to_review.keys():
            if fn not in self.all_files.keys():
                del self.to_review[fn]

        if review_type == 'daily':
            for fn in ['next-week.txt', 'someday-maybe.txt']:
                if fn in self.to_review:
                    del self.to_review[fn]

        self.current_file_index = 0
        self.refresh_current_todos()
        self.current_todo_index = 0
        self.dirty = False

        # get started:
        print("Welcome to your {} review!"
              " Type help or ? to list commands.\n".format(review_type))
        print("You will be reviewing "
              "{}\n".format(", ".join(self.to_review.keys())))
        self.show_file_info()
        print("\n")
        self.show_todo(self.current_todo)

    @property
    def current_todo(self):
        return self.current_todos[self.current_todo_index]

    @property
    def current_filename(self):
        return list(self.to_review.keys())[self.current_file_index]

    @property
    def current_file(self):
        return self.all_files[self.current_filename]

    def show_message(self, message):
        print("\N{WHITE RIGHT POINTING INDEX} {}\n".format(message))

    def show_file_info(self, f=None):
        try:
            if f is None:
                f = self.current_file
        except:
            print("No current file.")
            return
        instr = self.to_review[os.path.basename(f.filename)]
        print(f.summary())
        print(instr)

    def show_todo(self, todo):
        n = self.current_todos.index(todo) + 1
        tot = len(self.current_todos)
        if todo.done:
            icon = "\N{CHECK MARK}"
        else:
            icon = "\N{BALLOT BOX}"
        print("{pad}{n}/{tot}\n"
              "{pad}{icon} {todo}".format(pad=4*" ", n=n, tot=tot,
                                          icon=icon, todo=todo))

    def refresh_current_todos(self):
        self.current_todos = sorted(self.current_file.get_todos())

    def goto_next_file(self):
        """returns False if no next file exists.

        leaves current_file_index pointing at a valid file
        """
        self.current_file_index += 1
        if self.current_file_index >= len(self.to_review):
            self.current_file_index -= 1
            return False

        self.refresh_current_todos()
        self.current_todo_index = 0
        return True

    def show_next(self, increment=True, ):
        "prints next todo. returns false if at end."
        if increment:
            self.current_todo_index += 1
        while self.current_todo_index >= len(self.current_todos):
            if not self.goto_next_file():
                return False
            self.show_file_info()
            print("\n")
        self.show_todo(self.current_todo)
        return True

    def show_prev(self):
        if self.current_todo_index == 0:
            return False
        self.current_todo_index -= 1
        self.show_todo(self.current_todo)
        return True

    def do_where(self, rest):
        "Show current todo"
        self.show_file_info()
        print("\n")
        try:
            t = self.current_todo
        except:
            print("No current todo. All done?")
            return
        self.show_todo(t)

    def emptyline(self):
        self.do_next('')

    def do_listfiles(self, rest):
        for fn in self.to_review:
            if fn in self.all_files:
                self.show_file_info(self.all_files[fn])
            else:
                print("{} not found in dir.".format(fn))

    def do_next(self, rest):
        "Do nothing with the current todo and move on"
        if not self.show_next():
            print("At end of todos and files.")
    do_n = do_next

    def do_prev(self, rest):
        "Do nothing with the current todo and go to previous"
        if not self.show_prev():
            print("At first todo already:")
            self.show_todo(self.current_todo)
    do_p = do_prev

    def do_prio(self, rest):
        "Set priority A-Z for current todo ('0' to clear) and go to next."
        if (rest != '0' and not rest.isalpha()) or len(rest) != 1:
            print("'{}' not a valid priority. Use A-Z.".format(rest))
            return
        if rest != self.current_todo.priority:
            if rest == '0':
                self.current_todo.priority = None
            else:
                self.current_todo.priority = rest.upper()
            self.current_file.replace_todo(self.current_todo,
                                           self.current_todo)
            self.dirty = True
        self.show_next()

    def todo_completer(self, text, idx):
        "not currently used."
        return text + 'foo'

    def completer(self, text, idx):
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

    def edit_todo_string(self, todo_string):
        "Edit a string representing a todo, return edited string"
        def hook():
            readline.insert_text(todo_string)
        readline.set_startup_hook(hook)
        old_delims = readline.get_completer_delims()
        new_delims = old_delims.replace('@', '')
        new_delims = new_delims.replace('+', '')
        new_delims = new_delims.replace('#', '')
        readline.set_completer_delims(new_delims)
        readline.set_completer(self.completer)
        newval = input("editing: ")
        readline.set_startup_hook(None)
        readline.set_completer(None)
        readline.set_completer_delims(old_delims)
        return newval

    def do_edit(self, rest):
        "Edit the current todo"
        newval = self.edit_todo_string(str(self.current_todo))
        if newval != str(self.current_todo):
            self.dirty = True
            newtodo = todo_from_line(newval)
            self.current_file.replace_todo(self.current_todo,
                                           newtodo)
            self.current_todos[self.current_todo_index] = newtodo
        self.show_next()
    do_e = do_edit

    def do_done(self, rest):
        "Mark todo as done."
        self.current_todo.done = True
        self.show_todo(self.current_todo)
        print()
        n_next = self.show_upcoming(self.current_todo)
        if n_next == 0 and len(self.current_todo.projects) > 0:
            yn = input("No next actions for '{}'. "
                       "Add a new one? [y]/n ".format(self.current_todo.projects))
            if yn in ['Y', 'y', '']:
                self.add_related_todo(self.current_todo, "")
        self.dirty = True
        self.show_next()
    do_x = do_done

    def show_upcoming(self, todo):
        "show what's next in this todo's projects"
        num_upcoming = 0
        if len(todo.projects) == 0:
            return num_upcoming

        print("\nUpcoming in related projects:")

        for project in todo.projects:
            print("# Project: {}".format(project))
            upcoming_todos = [t for t in self.current_file.get_todos()
                              if project in t.projects and t.done == False]
            print("\n## ".join(sorted(map(str, upcoming_todos))))
            print("\n\n")
            num_upcoming == len(upcoming_todos)
        return num_upcoming

    def do_new(self, rest):
        "Add new todo to file (or file prefix) given as first arg."
        if len(rest.split(' ', 1)) == 1:
            print("usage: new <fileprefix> <todotxt>")
            return
        fileprefix, todotxt = rest.split(' ', 1)
        matching_filenames = [fn for fn in self.all_files.keys()
                              if fn.startswith(fileprefix)]
        if len(matching_filenames) == 0:
            print("no files match '{}'".format(fileprefix))
            return
        elif len(matching_filenames) > 1:
            print("too many matches for '{}' - "
                  "add characters".format(fileprefix))
            return

        f = self.all_files[matching_filenames[0]]
        t = todo_from_line(todotxt)
        t.set_created_now()
        f.add_todo(t)
        self.refresh_current_todos()

    def do_delete(self, rest):
        "Delete the todo"
        self.current_file.delete_todo(self.current_todo)
        self.refresh_current_todos()
        self.show_message("deleted.")
        self.show_next(increment=False)
        self.dirty = True
    do_d = do_delete

    def move_to(self, todo, to_file):
        assert(self.current_file != to_file)
        print('moving to {}'.format(to_file.summary()))
        to_file.add_todo(todo)
        self.current_file.delete_todo(todo)
        self.refresh_current_todos()
        # print('after move, cur_file has "{}" \n'
        #       'and to_file has "{}"'.format(self.current_file,
        #                                     to_file))

    def move_current_to(self, filename):
        "moves current todo to a file"
        to_file = self.all_files[filename]
        if self.current_file == to_file:
            self.show_message("\N{INTERROBANG} Can't move to same file")
            return False
        self.move_to(self.current_todo, to_file)
        self.show_message("moved to {}".format(filename))
        self.dirty = True
        self.show_next(increment=False)

    def do_later(self, rest):
        "Move TODO to next-week.txt to re-evaluate at next weekly review."
        self.move_current_to('next-week.txt')
    do_l = do_later

    def do_someday(self, rest):
        "Move TODO to someday-maybe.txt to re-evaluate at next weekly review."
        self.move_current_to('someday-maybe.txt')

    def do_wait(self, rest):
        "Move TODO to waiting.txt to track and check daily."
        self.move_current_to('waiting.txt')
    do_w = do_wait

    def do_now(self, rest):
        "Move current todo to todo.txt"
        self.move_current_to('todo.txt')

    def do_first(self, rest):
        "Add and edit a new todo in the same project that needs to be done before the current one."
        c = self.current_todo
        c.priority = None
        self.add_related_todo(c, rest)
        self.show_next()

    def add_related_todo(self, t, rest):
        todostr = t.get_string_excluding(['text', 'cdstr'])
        text = " {}".format(rest)
        newval = self.edit_todo_string(todostr + text)
        self.dirty = True
        newtodo = todo_from_line(newval)
        self.current_file.add_todo(newtodo)

    def do_quit(self, rest):
        "Quit"
        if self.dirty:
            yn = input("Save changes? [y]/n ")
            if yn in ['Y', 'y', '']:
                print("Saving...")
                self.do_save(None)
        self.show_message("Adios")
        return True
    do_q = do_quit

    def do_skipfile(self, rest):
        "Skip remaining todos in the file and move to next."
        if self.current_file_index >= len(self.to_review):
            print("at end of files.")
            return

        nskip = len(self.current_todos) - self.current_todo_index
        self.show_message("Skipping {} todos in "
                          "{}.".format(nskip, self.current_file.filename))

        while True:
            if not self.goto_next_file():
                print("at end of files.")
                return

            self.show_file_info()
            if len(self.current_todos) > 0:
                print("\n")
                break
            else:
                print("    (Skipping)\n")

        self.show_todo(self.current_todo)

    def do_save(self, rest):
        "Write out all changes"
        for f in self.all_files.values():
            f.save()
        self.show_message("Saved.")
        self.dirty = False

    def completedefault(self, **args):
        return ['foo', 'bar']

    def complete_dbg(self, **args):
        return ['curfile']

    def do_dbg(self, rest):
        "debug dumping. currently supports arg 'curfile'"
        if rest == 'curfile':
            print(self.current_file)


if __name__ == '__main__':
    # todo.sh usage:
    if len(sys.argv) > 1 and sys.argv[1] == 'usage':
        print("USAGE: review script. use -h for real usage")
        sys.exit()

    parser = argparse.ArgumentParser(description='todotxt review script')
    parser.add_argument('--dir', default=os.environ.get('TODO_DIR', '.'),
                        help="Directory to look for todo.txt files")
    parser.add_argument('--type', default='daily',
                        choices=['daily', 'weekly'],
                        help="Type of review - controls which files are shown")
    opts = parser.parse_args()

    ReviewShell(opts.dir, opts.type).cmdloop()
