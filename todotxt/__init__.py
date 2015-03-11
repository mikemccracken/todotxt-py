# todo.txt parsing / management library

from collections import defaultdict
from datetime import datetime
from functools import total_ordering
import os
import re
import tempfile

DATE_FMT = "%Y-%m-%d"


@total_ordering
class TODO:
    def __init__(self, text, priority=None, created_date=None,
                 done_date=None, contexts=None, projects=None,
                 done=False):
        """Initialize a TODO object with none of the chars from the parsed
        version, like @+#.

        _date args are strings

        contexts and projects are lists
        """
        self.text = text
        self.priority = priority
        self.created_date = created_date
        self.done_date = done_date
        self.contexts = contexts if contexts else []
        self.projects = projects if projects else []

    def _get_str_components(self):
        d = {}
        d['donestr'] = "x {} ".format(self.done_date) if self.done_date else ""

        if not self.done_date:
            d['pstr'] = "({}) ".format(self.priority) if self.priority else ""
        else:
            d['pstr'] = ""
        d['cdstr'] = (self.created_date + " ") if self.created_date else ""
        d['text'] = self.text
        if len(self.contexts) + len(self.projects) > 0:
            d['text'] += " "
        d['cxstr'] = " ".join(["@{}".format(c)
                               for c in sorted(self.contexts)])
        if len(self.contexts) > 0:
            d['cxstr'] += " "
        d['prjstr'] = " ".join(["+{}".format(p)
                                for p in sorted(self.projects)])
        if len(self.projects) > 0:
            d['prjstr'] += " "
        return d

    def __str__(self):
        d = self._get_str_components()
        return "{donestr}{pstr}{cdstr}{text}{prjstr}{cxstr}".format(**d)

    def __eq__(self, other):
        # depends on sorted context/project arrays
        return str(self) == str(other)

    @property
    def done(self):
        return self.done_date is not None

    @done.setter
    def done(self, newval):
        if newval:
            self.done_date = datetime.strftime(datetime.now(), DATE_FMT)
        else:
            self.done_date = None

    def __lt__(self, other):
        def get_tuple(d):
            return (d['donestr'],
                    d['prjstr'],
                    d['cxstr'],
                    d['cdstr'],
                    d['pstr'],
                    d['text'])
        d_self = self._get_str_components()
        d_other = other._get_str_components()
        return get_tuple(d_self) < get_tuple(d_other)


def todo_from_line(line):
    """returns a TODO object parsed from 'line'"""
    prio_re = re.compile(r"\(([A-Z])\)")

    words = line.split()
    if len(words) == 0:
        return None

    # TODO: not handling done correctly
    t_done = False
    t_done_date = None
    if words[0][0] == 'x':
        t_done = True
        t_done_date = words[1]
        words = words[2:]

    # TODO: ignore priority for done tasks, use k:v?
    t_prio = None
    prio_match = prio_re.match(words[0])
    if prio_match:
        t_prio = prio_match.groups()[0]
        words = words[1:]

    t_created_date = None
    try:
        d = datetime.strptime(words[0], DATE_FMT)
        d  # flakes :(
        t_created_date = words[0]
        words = words[1:]
    except ValueError:
        pass

    t_projects = []
    t_contexts = []
    t_txt = []
    for word in words:
        if word.startswith("+"):
            t_projects.append(word[1:])
        elif word.startswith("@"):
            t_contexts.append(word[1:])
        else:
            t_txt.append(word)
    t_txt = " ".join(t_txt)

    return TODO(t_txt, priority=t_prio,
                created_date=t_created_date,
                done_date=t_done_date,
                contexts=t_contexts,
                projects=t_projects,
                done=t_done)


class TODOFile:
    def __init__(self, filename):
        self.filename = filename
        self._todos = []
        with open(self.filename, 'r') as f:
            self._todos += [todo_from_line(l) for l in f.readlines()]
        self._todos = [t for t in self._todos if t is not None]

        self._recalc()

    def __str__(self):
        return "\n".join(map(str, self._todos))

    def _recalc(self):
        self.projects = defaultdict(list)
        self.contexts = defaultdict(list)

        for t in self._todos:
            for p in t.projects:
                self.projects[p].append(t)
            for c in t.contexts:
                self.contexts[c].append(t)

    def summary(self):
        return ("{}: {} todos, {} projects and "
                "{} contexts".format(os.path.basename(self.filename),
                                     len(self._todos),
                                     len(self.projects),
                                     len(self.contexts)))

    def add_todo(self, todo):
        self._todos.append(todo)
        self._recalc()

    def delete_todo(self, todo):
        self._todos.remove(todo)
        self._recalc()

    def replace_todo(self, old, new):
        self._todos[self._todos.index(old)] = new
        self._recalc()

    def get_todos(self):
        return self._todos

    def save(self):
        with tempfile.NamedTemporaryFile(
                dir=os.path.dirname(self.filename),
                delete=False) as fout:
            fout.write(str(self).encode())
            fout.write("\n".encode())
        os.replace(fout.name, self.filename)
