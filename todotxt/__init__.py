# todo.txt parsing / management library

from collections import defaultdict
from datetime import datetime
import re

DATE_FMT = "%Y-%M-%d"

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
        self.done = done

    def __str__(self):
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
        d['cxstr'] = " ".join(["@{}".format(c) for c in self.contexts])
        if len(self.contexts) > 0: d['cxstr'] += " "
        d['prjstr'] = " ".join(["+{}".format(p) for p in self.projects])
        if len(self.projects) > 0: d['prjstr'] += " "
        return "'{donestr}'{pstr}{cdstr}{text}{prjstr}{cxstr}".format(**d)

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
        t_created_date = words[0]
        words = words[1:]
    except ValueError as ve:
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
                created_date = t_created_date,
                done_date = t_done_date,
                contexts=t_contexts,
                projects=t_projects,
                done=t_done)
    
        
class TODOFile:
    def __init__(self, filename):
        self.filename = filename
        self.todos = []
        with open(self.filename, 'r') as f:
            self.todos += [todo_from_line(l) for l in f.readlines()]

        self.projects = defaultdict(list)
        self.contexts = defaultdict(list)

        for t in self.todos:
            for p in t.projects:
                self.projects[p].append(t)
            for c in t.contexts:
                self.contexts[c].append(t)
        
    def __str__(self):
        return "\n".join(map(str, self.todos))
