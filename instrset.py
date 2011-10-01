""" Instruction set for the virtual machine. Is register based, largely
    inspired by Lua-5.1's instruction set.

    rA/rB/rC: frame slot, by frame[r_]
    kA/kB/kC: immediate value, by consts[k_]
    kBx: extended immediate value, usually used in branching.

    A closure, in order to be executed, should have `instrs`, `consts`,
    `nframeslots` and `cellvalues`.
    To figure out the number of arguments, `nargs` and `hasvarargs` are also
    included.
    In the future it may also capture its current globalvars (to make
    python-like modules).
"""
from sobject import *

class Instr(object):
    def dispatch(self, vm):
        raise NotImplementedError

    def __repr__(self):
        """NOT_RPYTHON"""
        return '[instr]'

class Halt(Instr):
    def dispatch(self, vm):
        vm.halt() # instantly, no other things will happen.

    def __repr__(self):
        return '[halt]'

class MoveLocal(Instr):
    """ rA = rB
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.frame.get(self.B))

    def __repr__(self):
        return '[r(%d) = r(%d)]' % (self.A, self.B)

class LoadGlobal(Instr):
    """ rA = globalvars[kB]
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.globalvars[vm.consts[self.B]])

    def __repr__(self):
        return '[r(%d) = g(k(%d))]' % (self.A, self.B)

class LoadCell(Instr):
    """ rA = cellvalues[B].getvalue()
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.cellvalues[self.B].getvalue())

    def __repr__(self):
        return '[r(%d) = c(%d).get]' % (self.A, self.B)

class LoadConst(Instr):
    """ rA = kB
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.consts[self.B])

    def __repr__(self):
        return '[r(%d) = k(%d)]' % (self.A, self.B)

class StoreGlobal(Instr):
    """ globalvars[kA] = rB
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B
    
    def dispatch(self, vm):
        vm.globalvars[vm.consts[self.A]] = vm.frame.get(self.B)

    def __repr__(self):
        return '[g(k(%d)) = r(%d)]' % (self.A, self.B)

class StoreCell(Instr):
    """ cellvalues[A].setvalue(rB)
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B
    
    def dispatch(self, vm):
        vm.cellvalues[self.A].setvalue(vm.frame.get(self.B))

    def __repr__(self):
        return '[c(%d).set(r(%d))]' % (self.A, self.B)

class BuildClosure(Instr):
    """ The most involved things is to open cellvalues.
        Usually the current frame need to be passed to replace the closure's
        cellvalues' baseframe. After then, those cellvalues will be added
        into the vm's cellval_list.

        @see sdo.W_ClosureSkeleton.build_closure()

        rA = build_closure_and_open_cellvalues(kB)
    """
    _immutable_fields_ = ['A', 'B']

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def dispatch(self, vm):
        w_skel = vm.consts[self.B]
        assert w_skel.is_procedure_skeleton()
        w_proc = w_skel.build_closure(vm)
        vm.frame.set(self.A, w_proc)

    def __repr__(self):
        return '[r(%d) = buildclosure(k(%d))]' % (self.A, self.B)

class Call(Instr):
    """ rA = rB(rB + 1, ..., rB + C)

        Eg, func(1, 2, 3, 4, 5) when func is (lambda (x y . z) ...),
                            rB+0 +1 +2 +3 +4 +5
        stack will be [..., func, 1, 2, 3, 4, 5, ...].
        (3, 4, 5) will be packed to a cons list reversely.
        then, z, y and x will be placed on vm's new frame reversely.

        The current state of vm will be stored in a dump.
    """
    _immutable_fields_ = ['A', 'B', 'C']

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def dispatch(self, vm):
        dest_reg = self.A
        proc_reg = self.B
        index_of_first_arg = proc_reg + 1
        actual_argcount = self.C

        # make sure its a procedure and we have enough args
        w_proc = vm.frame.get(proc_reg)

        if w_proc.is_pyproc():
            py_args = [vm.frame.get(index_of_first_arg + i)
                for i in xrange(actual_argcount)]
            w_result = w_proc.py_call(py_args) # Call it!
            vm.frame.set(dest_reg, w_result)
            return

        assert w_proc.is_procedure()
        assert w_proc.skeleton.nargs <= actual_argcount

        # handle varargs.
        if w_proc.skeleton.nargs < actual_argcount:
            assert(w_proc.skeleton.hasvarargs)
            # vararg is slowish.
            # XXX: scmlist_to_pylist here
            vararg = pylist2scm([
                vm.frame.get(index_of_first_arg + i)
                for i in xrange(actual_argcount)])
        else:
            vararg = None # make pypy happy

        # save vm's current state
        vm.save_dump()

        # switch vm to the new closure
        old_frame = vm.frame
        vm.frame = vm.new_frame(w_proc.skeleton.nframeslots)
        vm.consts = w_proc.skeleton.consts
        vm.cellvalues = w_proc.cellvalues
        vm.instrs = w_proc.skeleton.instrs
        vm.pc = 0
        vm.return_addr = dest_reg

        # push the arguments on the new frame
        # Note that if we have continuous stack frame then the argument
        # copying overhead could be avoided. But does it worth?
        # Anyway we can take a profile first.
        for i in xrange(w_proc.skeleton.nargs):
            vm.frame.set(i, old_frame.get(i + index_of_first_arg))
        if w_proc.skeleton.hasvarargs:
            vm.frame.set(w_proc.skeleton.nargs, vararg)

    def __repr__(self):
        if self.C == 0:
            return '[r(%d) = r(%d).call()]' % (
                    self.A, self.B)
        elif self.C == 1:
            return '[r(%d) = r(%d).call(r(%d))]' % (
                    self.A, self.B, self.B + 1)
        elif self.C == 2:
            return '[r(%d) = r(%d).call(r(%d), r(%d))]' % (
                    self.A, self.B, self.B + 1, self.B + self.C)
        else:
            return '[r(%d) = r(%d).call(r(%d), ..., r(%d))]' % (
                    self.A, self.B, self.B + 1, self.B + self.C)


class TailCall(Instr):
    """ TailCall -- do not save dump. However, escape the cellvalues on
        the current stack frame since the current closure's frame
        is gone.
        If it's a pyfunc then it's just like normal Call.
        Codes copied for now, refactor them later.
    """
    _immutable_fields_ = ['A', 'B', 'C']

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C

    def dispatch(self, vm):
        dest_reg = self.A
        proc_reg = self.B
        index_of_first_arg = proc_reg + 1
        actual_argcount = self.C

        # make sure its a procedure and we have enough args
        w_proc = vm.frame.get(proc_reg)

        if w_proc.is_pyproc():
            py_args = [vm.frame.get(index_of_first_arg + i)
                for i in xrange(actual_argcount)]
            w_result = w_proc.py_call(py_args) # Call it!
            vm.frame.set(dest_reg, w_result)
            return

        assert w_proc.is_procedure()
        assert w_proc.skeleton.nargs <= actual_argcount

        # handle varargs.
        if w_proc.skeleton.nargs < actual_argcount:
            assert(w_proc.skeleton.hasvarargs)
            # vararg is slowish.
            # XXX: scmlist_to_pylist here
            vararg = pylist2scm([
                vm.frame.get(index_of_first_arg + i)
                for i in xrange(actual_argcount)])
        else:
            vararg = None # make pypy happy

        # do not save vm's current state. However, escape current cell values
        #vm.save_dump()
        vm.escape_cellvalues()

        # switch vm to the new closure
        old_frame = vm.frame
        vm.frame = vm.new_frame(w_proc.skeleton.nframeslots)
        vm.consts = w_proc.skeleton.consts
        vm.cellvalues = w_proc.cellvalues
        vm.instrs = w_proc.skeleton.instrs
        vm.pc = 0
        #vm.return_addr = dest_reg # return address is not changed.

        # push the arguments on the new frame
        # Note that if we have continuous stack frame then the argument
        # copying overhead could be avoided. But does it worth?
        # Anyway we can take a profile first.
        for i in xrange(w_proc.skeleton.nargs):
            vm.frame.set(i, old_frame.get(i + index_of_first_arg))
        if w_proc.skeleton.hasvarargs:
            vm.frame.set(w_proc.skeleton.nargs, vararg)

    def __repr__(self):
        if self.C == 0:
            return '[r(%d) = r(%d).tailcall()]' % (
                    self.A, self.B)
        elif self.C == 1:
            return '[r(%d) = r(%d).tailcall(r(%d))]' % (
                    self.A, self.B, self.B + 1)
        elif self.C == 2:
            return '[r(%d) = r(%d).tailcall(r(%d), r(%d))]' % (
                    self.A, self.B, self.B + 1, self.B + self.C)
        else:
            return '[r(%d) = r(%d).tailcall(r(%d), ..., r(%d))]' % (
                    self.A, self.B, self.B + 1, self.B + self.C)


class Return(Instr):
    """ return rB
        
        Currently we only return one and exactly one value.
        The function cell values will be cleaned as well.
    """
    _immutable_fields_ = ['B']

    def __init__(self, B):
        self.B = B

    def dispatch(self, vm):
        """ return_value = vm.frame[self.B]
            escape_cellvalues(vm)
            restore_dump(vm)
            # some how the dest reg for return value is restored.
            vm.frame[dest_reg] = return_value
        """
        return_value = vm.frame.get(self.B)
        vm.restore_dump(return_value)

    def __repr__(self):
        return '[return r(%d)]' % (self.B,)


class Branch(Instr):
    """ Unconditional jump, pc += Bx
    """
    _immutable_fields_ = ['Bx']

    def __init__(self, Bx):
        self.Bx = Bx

    def dispatch(self, vm):
        vm.pc += self.Bx

    def __repr__(self):
        return '[pc += %d]' % (self.Bx,)


class BranchIfFalse(Instr):
    """ if not rA then pc += self.Bx
    """
    _immutable_fields_ = ['A', 'Bx']

    def __init__(self, A, Bx):
        self.A = A
        self.Bx = Bx

    def dispatch(self, vm):
        if not vm.frame.get(self.A).to_bool():
            vm.pc += self.Bx

    def __repr__(self):
        return '[if not r(%d): pc += %d]' % (self.A, self.Bx,)


# _________________________________________________________________________
# application instructions

