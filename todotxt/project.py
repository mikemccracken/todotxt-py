# project file maintenance script

from collections import defaultdict
from functools import total_ordering
from glob import glob
import os
import tempfile

from todotxt import TODOFile

@total_ordering
class Project:
    def __init__(self, name, description=None, todos=None):
        "todos is a dictionary {filename: list of Todos}"
        self.name = name
        self.description = description if description else ""
        self.todos = defaultdict(list)
        if todos:
            self.todos.update(todos)
        self.sortorder = ['todo.txt', 'next-week.txt', 'waiting.txt',
                          'someday-maybe.txt', 'done.txt']

    def add_todos(self, todo_filename, todos):
        "adds a list of todos from todo_filename "
        self.todos[todo_filename] += todos

    def metadata_str(self, pad_char=" "):
        sa = []
        for fn in self.sortorder:
            tl = self.todos[fn]
            if len(tl) > 0:
                sa.append("{}:{:2}".format(fn[:-4], # remove .txt
                                            len(tl)))
            else:
                sa.append(pad_char * (len(fn[:-4]) + 3))
        return " ".join(sa)

    def _get_sort_tuple(self, p):
        t = []
        for fn in p.sortorder:
            t.append(len(p.todos[fn]))
        t.append(p.name)
        t.append(p.description)
        return tuple(t)

    def __eq__(self, other):
        return self._get_sort_tuple(self) == self._get_sort_tuple(other)

    def __lt__(self, other):
        return self._get_sort_tuple(self) < self._get_sort_tuple(other)
    
    def __str__(self):
        return self.padded_string(80)

    def padded_string(self, width, pad_char=" "):
        s = "+" + self.name
        if self.description != "":
            s += ": " + self.description
        ms = self.metadata_str(pad_char)
        if ms != "":
            ms = " # {}".format(ms)
            pad_width = max(0, width - len(s) - len(ms))
            s += pad_char * pad_width + ms
        return s
    

# projects are '+project-name Some optional description text # discarded comments
def project_from_line(line):
    """parses a Project from a line of text. discards comments, as they
    are recomputed by the scripts.
    """
    pcl = line.split('#', maxsplit=1)
    projtxt = pcl[0]
    if len(projtxt) == 0:
        return None

    pl = projtxt.split(' ', maxsplit=1)
    name = pl[0]
    if name.startswith("+"):
        name = name[1:]
    if name.endswith(":"):
        name = name[:-1]
    if len(pl) > 1:
        desc = pl[1].strip()
    else:
        desc = None
    p = Project(name, desc)
    return p

        
class ProjectFile:
    """A file with a line per project. Class reads todotxt files in same
    directory to look for matching todos.

    Creates filename on save if it doesn't exist. Overwrites filename
    on save, so externally added comments will not be preserved.

    """
    def __init__(self, filename):
        self.filename = filename
        self.orphan_projectname = "no-project"
        self._projects = {}
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                for l in f.readlines():
                    p = project_from_line(l.rstrip())
                    if p is not None:
                        self._projects[p.name] = p

        self._todo_files = {}
        self._recalc()
        
    def _recalc(self):
        self._todos = defaultdict(list)
        todo_dir = os.path.dirname(self.filename)
        todo_filenames = glob(todo_dir + "/*.txt")
        for fn in todo_filenames:
            bfn = os.path.basename(fn)
            tf = TODOFile(fn)
            for project_name, project_todos in tf.projects.items():
                p = self._projects.setdefault(project_name,
                                              Project(project_name))
                p.add_todos(bfn, project_todos)

            op = self._projects.setdefault(self.orphan_projectname,
                                          Project(self.orphan_projectname,
                                                  "Todos with no project"))
            op.add_todos(bfn, [t for t in tf.get_todos()
                               if len(t.projects) == 0])

    def __str__(self):
        return self.padded_string(120)

    def padded_string(self, width, draw_dots=False):
        s = ""
        draw_dots_now = False
        for p in sorted(self._projects.values(), reverse=True):
            s += "\n" + p.padded_string(width,
                                        pad_char="." if draw_dots_now else " ")
            draw_dots_now = ~draw_dots_now & draw_dots
        return s

    def save(self):
        with tempfile.NamedTemporaryFile(
                dir=os.path.dirname(self.filename),
                delete=False) as fout:
            fout.write(str(self).encode())
            fout.write("\n".encode())
        os.replace(fout.name, self.filename)
