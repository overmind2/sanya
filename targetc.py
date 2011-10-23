#!/usr/bin/env python

from sys import argv
import __pypy_path__
from sanya.parser import parse_string
from sanya.llir import hir_compile
from sanya.llir import lir_compile

def main():
    with open(argv[2]) as f:
        content = f.read()
    list_of_expr = parse_string(content)
    toplevel, walker = hir_compile.compile_list_of_expr(list_of_expr)
    if argv[1] == '--dis':
        hir_compile.WalkerPrinter(walker).pprint()
    elif argv[1] == '--compile':
        c_code = lir_compile.compile_from_hir_walker(walker)
        print c_code
    else:
        print 'usage: %s [ --dis | --compile ] [FILENAME]' % argv[0]

if __name__ == '__main__':
    main()
