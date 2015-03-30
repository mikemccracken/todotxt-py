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
        self.description = description
        self.todos = defaultdict(list)
        if todos:
            self.todos.update(todos)
        self.sortorder = ['todo.txt', 'next-week.txt', 'waiting.txt',
                          'someday-maybe.txt', 'done.txt']

    def add_todos(self, todo_filename, todos):
        "adds a list of todos from todo_filename "
        self.todos[todo_filename] += todos

    def metadata_str(self):
        sa = []
        for fn in self.sortorder:
            tl = self.todos[fn]
            if len(tl) > 0:
                sa.append("{}: {}".format(fn[:-4], # remove .txt
                                          len(tl)))
        return ", ".join(sa)

    def _get_sort_tuple(self, p):
        t = []
        for fn in p.sortorder:
            t.append(len(self.todos[fn]))
        t.append(p.name)
        t.append(p.description)
        return tuple(t)

    def __lt__(self, other):
        return self._get_sort_tuple(self) < self._get_sort_tuple(other)
    
    def __str__(self):
        s = self.name
        if self.description:
            s += " " + self.description
        ms = self.metadata_str()
        if ms != "":
            s += " # " + ms
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
    if len(pl) > 1:
        desc = pl[1]
    else:
        desc = None
    p = Project(name, desc)
    return p

        
class ProjectFile:
    """A file with a line per project. Class reads todotxt files in same
    directory to look for matching todos.

    Creates filename on save if it doesn't exist. Always overwrites filename on save.
    """
    def __init__(self, filename):
        self.filename = filename
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

    def __str__(self):
        return "\n".join([str(p) for p in sorted(self._projects.values())])
                
    def save(self):
        with tempfile.NamedTemporaryFile(
                dir=os.path.dirname(self.filename),
                delete=False) as fout:
            fout.write(str(self).encode())
            fout.write("\n".encode())
        os.replace(fout.name, self.filename)
