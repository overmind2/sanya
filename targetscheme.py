
import os
import sys
import __pypy_path__
from sparser import parse
from scompile import w_compile, ClosureWalker
from stdlib import open_lib
from svm import VM
from sobject import w_unspecified
from pypy.rlib.streamio import fdopen_as_stream, open_file_as_stream
from pypy.rlib.objectmodel import we_are_translated

if not we_are_translated():
    import readline

DEBUG = False

def jitpolicy(driver):
    from pypy.jit.codewriter.policy import JitPolicy
    return JitPolicy()

def run_file(filename):
    stream = open_file_as_stream(filename, 'r')
    code_string = stream.readall()
    codes = parse(code_string)
    walker = ClosureWalker()
    w_skel = w_compile(walker, codes)

    vm = VM()
    open_lib(vm)
    vm.bootstrap(w_skel)
    vm.run()

def disassemble_file(filename):
    """NOT_RPYTHON"""
    content = open(filename).read()
    codes = parse(content)
    walker = ClosureWalker()
    w_skel = w_compile(walker, codes)
    print w_skel

def repl():
    stdin = fdopen_as_stream(0, 'r')
    stdout = fdopen_as_stream(1, 'a')
    vm = VM()
    open_lib(vm)
    walker = ClosureWalker()

    while True:
        if we_are_translated():
            stdout.write('> ')
            stdout.flush()
            code_string = stdin.readline()
        else:
            try:
                code_string = raw_input('> ')
            except (EOFError, KeyboardInterrupt):
                code_string = ''

        if not code_string:
            break # handle EOF

        code_string = code_string.strip('\n') # RPy
        if not code_string:
            continue # handle plain ENTER

        codes = parse(code_string)
        if not codes:
            continue # handle whitespace in RPy

        w_skel = w_compile(walker, codes)
        # some hack so as to not return the vm?

        # to view code
        if DEBUG:
            print w_skel

        walker.instructions = [] # clean up
        #walker.local_consts = []
        walker.deferred_lambdas = []
        walker.just_entered_visit = True

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
    elif len(argv) == 3:
        if not we_are_translated():
            disassemble_file(argv[2])
            return 0

    print 'usage: %s [filename]' % argv[0]
    return 0

def target(driver, args):
    driver.exe_name = '%(backend)s-scheme'
    return entry_point, None

if __name__ == '__main__':
    entry_point(sys.argv)

