#!/usr/bin/env python3

from sys import argv, stderr
import re

def debug(x):
    print(x, file=stderr)

# === Graphviz API layer ===
def start_graph():
    print('digraph {')

def add_link(src_line_no, tgt_line_no, label = None):
    label = ' [label = "%s"]' % label.replace('"', '\\"') if label else ''
    print('  %s -> %s%s' % (src_line_no, tgt_line_no, label))

def add_node(node):
    print('  %s [label = "%s", shape = %s]' % (node.line_no, node.label.replace('"', '\\"'), node.Shape))

def terminate_graph():
    print('}')

# === Line types ===
class Line:
    Shape = 'ellipse'
    def __init__(self, line_no, indent, label):
        self.line_no = line_no
        self.indent = indent
        self.label = label

    def Continue(self, next_line, termination):
        for h in termination:
            h.Terminate(next_line)
        if type(next_line) is Line:
            self.label += '\n' + next_line.label
            return self
        else:
            self.Terminate(next_line)
            return next_line

    def Terminate(self, next_line = None):
        if next_line:
            add_link(self.line_no, next_line.line_no)
        add_node(self)

class Condition(Line):
    Shape = 'hexagon'
    LabelYes = 'да'
    LabelNo = 'нет'

    def __init__(self, keyword, line_no, indent, label):
        Line.__init__(self, line_no, indent, label)
        self.keyword = keyword

    def Continue(self, next_line, termination):
        if self.keyword == 'if':
            if hasattr(next_line, 'keyword') and next_line.keyword == 'else':
                # TODO store end_if correctly
                self.end_if = next_line.line_no - 1
                self.termination = termination
                return self

        if hasattr(self, 'termination'):
            for h in self.termination:
                h.Terminate(next_line)
        for h in termination:
            h.Terminate(next_line)

        if not hasattr(self, 'end_if'):
            add_link(self.line_no, next_line.line_no, Condition.LabelNo)
        add_node(self)
        return next_line

    def Enter(self, next_line):
        if hasattr(self, 'end_if'):
            add_link(self.line_no, next_line.line_no, Condition.LabelNo)
        else:
            add_link(self.line_no, next_line.line_no, Condition.LabelYes)
        return next_line

    def Terminate(self, next_line = None):
        if next_line:
            if hasattr(self, 'end_if'):
                add_link(self.end_if, next_line.line_no)
            else:
                self.Continue(next_line, [])
        add_node(self)

    #def Terminate(self, next_line = None):
        #if self.keyword == 'if':
            #if keyword == 'else':
                #self.end_if =

# === Main code ===
headers = [] # list of headers arranged by indent
line_no = 0
start_graph()
with open(argv[1]) as srcfile:
    for line_str in srcfile:
        line_no += 1
        stripped = line_str.strip()
        if stripped == '' or stripped[0] == '#':
            continue

        this_indent = re.search(r'\S', line_str).start()
        if stripped[-1] == ':':
            try: space_idx = stripped.index(' ')
            except: space_idx = -1
            keyword = stripped[:space_idx];
            if keyword == 'if':
                label = stripped[3:-1] + '?'
            else:
                label = stripped
            this_line = Condition(keyword, line_no, this_indent, label)
        else:
            this_line = Line(line_no, this_indent, stripped)

        termination = []
        while headers and headers[-1].indent > this_indent:
            termination.append(headers.pop())

        if len(headers) == 0:
            for h in termination:
                h.Terminate(this_line)
            headers.append(this_line)
            continue

        last_header = headers[-1]
        if last_header.indent == this_indent:
            headers[-1] = last_header.Continue(this_line, termination)
            continue

        if last_header.indent < this_indent:
            headers.append(last_header.Enter(this_line))
            continue

while headers:
    last_header = headers.pop()
    last_header.Terminate()

terminate_graph()
