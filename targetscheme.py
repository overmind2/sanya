#!/usr/bin/env python
import sys

import __pypy_path__
from pypy.rlib.streamio import fdopen_as_stream, open_file_as_stream
from pypy.rlib.objectmodel import we_are_translated

from sanya.configuration import DEBUG
from sanya.parser import parse
from sanya.compilation import compile_list_of_expr
from sanya.stdlib import open_lib
from sanya.vm import VM
from sanya.objectmodel import w_unspecified
from sanya import chunkio

if not we_are_translated():
    import readline

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def stream_to_skeleton(stream):
    content = stream.readall()
    expr_list = parse(content)
    return compile_list_of_expr(expr_list)

def run_file(filename):
    file_stream = open_file_as_stream(filename, 'r')
    vm = VM()
    open_lib(vm)
    vm.bootstrap(stream_to_skeleton(file_stream))
    file_stream.close()
    vm.run()

def disassemble_file(filename):
    """NOT_RPYTHON"""
    stream = open_file_as_stream(filename, 'r')
    print stream_to_skeleton(stream)
    stream.close()

def generate_header(filename):
    """NOT_RPYTHON"""
    from instrset import op_map
    with open(filename, 'w') as f:
        hpro = '_' + filename.upper().replace('.', '_') + '_'
        f.write('#ifndef %s\n' % hpro)
        f.write('#define %s\n' % hpro)
        f.write('\n')
        f.write('// Automatically generated from sanya/instrset.py.\n')
        f.write('\n')
        for name, val in op_map.iteritems():
            f.write('#define OP_%s (%s)\n' % (name, val))
        f.write('\n')
        f.write('#endif // %s\n' % hpro)

def compile_file(filename, outfname):
    """maybe rpython..."""
    stream = open_file_as_stream(filename, 'r')
    w_skel = stream_to_skeleton(stream)
    stream.close()

    outf = open_file_as_stream(outfname, 'w')
    chunkio.dump(w_skel, outf)
    outf.close()

def load_compiled_chunk(filename):
    vm = VM()
    open_lib(vm)
    stream = open_file_as_stream(filename, 'r')
    w_skel = chunkio.load(stream)
    stream.close()
    vm.bootstrap(w_skel)
    vm.run()

def repl():
    stdin = fdopen_as_stream(0, 'r')
    stdout = fdopen_as_stream(1, 'a')
    vm = VM()
    open_lib(vm)

    while True:
        if we_are_translated():
            # RPython -- cannot use readline
            stdout.write('> ')
            stdout.flush()
            raw_line_of_code = stdin.readline()
        else:
            # CPython -- use readline
            try:
                raw_line_of_code = raw_input('> ')
            except (EOFError, KeyboardInterrupt):
                raw_line_of_code = ''

        if not raw_line_of_code:
            break # handle EOF

        raw_line_of_code = raw_line_of_code.strip('\n') # RPy
        if not raw_line_of_code:
            continue # handle plain ENTER

        expr_list = parse(raw_line_of_code)
        if not expr_list:
            continue # handle whitespace in RPy

        w_skel = compile_list_of_expr(expr_list)
        # some hack so as to not return the vm?

        # to view code
        if DEBUG:
            print w_skel

        # to view code
        if DEBUG:
            continue

        vm.bootstrap(w_skel)
        vm.run()
        w_result = vm.exit_value
        if w_result is not w_unspecified:
            print w_result.to_string()

def entry_point(argv):
    if len(argv) == 1:
        repl()
        return 0
    elif len(argv) == 2:
        run_file(argv[1])
        return 0
    else:
        op = argv[1]
        fname = argv[2]
        if op == '-c': # compile the code and dump to another file
            outfname = argv[3]
            compile_file(fname, outfname)
            return 0
        elif op == '-r': # run compiled chunk
            load_compiled_chunk(fname)
            return 0

    # end of RPython-compatible functionalities
    if not we_are_translated():
        op = argv[1]
        fname = argv[2]
        if op == '-d': # disassemble
            disassemble_file(fname)
        elif op == '-g': # generate .hpp instruction definations
            generate_header(fname)
        elif op == '-v': # view compiled chunk
            stream = open_file_as_stream(fname, 'r')
            w_skel = chunkio.load(stream)
            stream.close()
            print w_skel
        else:
            print 'what do you want to do?'
        return

    print 'usage:'
    print '  %s to start repl' % argv[0]
    print '  %s [filename] to run file' % argv[0]
    print '  %s -c [filename] [output] to compile file' % argv[0]
    print '  %s -r [filename] to run compiled file' % argv[0]
    return 0

def target(driver, args):
    driver.exe_name = 'c-scheme'
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)

