#!/usr/bin/env python3

from sys import argv, stderr
import re

ConditionShape = 'hexagon'
NormalShape = 'ellipse'

line_no = 0
indent = 0
last_src_line = None
open_conditions = []
print('digraph {')
with open(argv[1]) as srcfile:
    for line in srcfile:
        line_no += 1
        stripped = line.strip()
        if stripped == '' or stripped[0] == '#':
            continue
        this_indent = re.search(r'\S', line).start()
        is_condition = stripped[-1] == ':'
        if is_condition:
            shape = ConditionShape
        else:
            shape = NormalShape
        node = 'l%s [label = "%s", shape = "%s"]' % (line_no, stripped.replace('"', '\\"'), shape)
        print(node)
        if this_indent == indent:
            if last_src_line:
                print('l%s -> l%s' % (last_src_line, line_no))
        elif this_indent > indent:
            print('l%s -> l%s [label = "да"]' % (last_src_line, line_no))
        else:
            print('l%s -> l%s [label = "нет"]' % (open_conditions.pop(), line_no))
        if stripped[-1] == ':':
            open_conditions.append(line_no)
        last_src_line = line_no
        indent = this_indent
        print('[%s] indent = %s' % (line_no, indent), file=stderr)
print('}')
