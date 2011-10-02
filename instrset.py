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

OP_TYPE_DUMMY = 0
OP_TYPE_ABC = 1
OP_TYPE_ABx = 2

class Instr(object):
    _immutable_fields_ = ['A', 'B', 'C', 'Bx']
    op_num = 0
    op_type = OP_TYPE_DUMMY

    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        raise NotImplementedError

    def __repr__(self):
        """NOT_RPYTHON"""
        return '[instr]'

    def dump_u32(self):
        if not self.op_num:
            raise ValueError('no opnum')

        if self.op_type == OP_TYPE_ABC:
            return (self.op_num << (32 - 5) | self.A << (32 - 5 - 9) |
                    self.B << (32 - 5 - 9 - 9) | self.C)
        elif self.op_type == OP_TYPE_ABx:
            return (self.op_num << (32 - 5) | self.A << (32 - 5 - 9) |
                    self.Bx << (32 - 5 - 9 - 9))
        else:
            raise ValueError('unknown op type')

class Halt(Instr):
    op_type = OP_TYPE_ABC

    def __init__(self):
        self.A = 0
        self.B = 0
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        vm.halt() # instantly, no other things will happen.

    def __repr__(self):
        return '[halt]'

class MoveLocal(Instr):
    """ rA = rB
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.frame.get(self.B))

    def __repr__(self):
        return '[r(%d) = r(%d)]' % (self.A, self.B)

class LoadGlobal(Instr):
    """ rA = globalvars[kB]
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.globalvars[vm.consts[self.B]])

    def __repr__(self):
        return '[r(%d) = g(k(%d))]' % (self.A, self.B)

class LoadCell(Instr):
    """ rA = cellvalues[B].getvalue()
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.cellvalues[self.B].getvalue())

    def __repr__(self):
        return '[r(%d) = c(%d).get]' % (self.A, self.B)

class LoadConst(Instr):
    """ rA = kB
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        vm.frame.set(self.A, vm.consts[self.B])

    def __repr__(self):
        return '[r(%d) = k(%d)]' % (self.A, self.B)

class StoreGlobal(Instr):
    """ globalvars[kA] = rB
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0
    
    def dispatch(self, vm):
        vm.globalvars[vm.consts[self.A]] = vm.frame.get(self.B)

    def __repr__(self):
        return '[g(k(%d)) = r(%d)]' % (self.A, self.B)

class StoreCell(Instr):
    """ cellvalues[A].setvalue(rB)
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0
    
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

        rA = build_closure_and_open_cellvalues(closkel_table[B])
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B):
        self.A = A
        self.B = B
        self.C = 0
        self.Bx = 0

    def dispatch(self, vm):
        w_skel = vm.closkel_table[self.B]
        assert w_skel.is_procedure_skeleton()
        w_proc = w_skel.build_closure(vm)
        vm.frame.set(self.A, w_proc)

    def __repr__(self):
        return '[r(%d) = buildclosure(CloskelT[%d])]' % (self.A, self.B)

class Call(Instr):
    """ rA = rB(rB + 1, ..., rB + C)

        Eg, func(1, 2, 3, 4, 5) when func is (lambda (x y . z) ...),
                            rB+0 +1 +2 +3 +4 +5
        stack will be [..., func, 1, 2, 3, 4, 5, ...].
        (3, 4, 5) will be packed to a cons list reversely.
        then, z, y and x will be placed on vm's new frame reversely.

        The current state of vm will be stored in a dump.
    """
    op_type = OP_TYPE_ABC

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.Bx = 0

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
            vararg = pylist2scm([
                vm.frame.get(index_of_first_arg + i)
                for i in xrange(actual_argcount)])
        else:
            vararg = w_nil

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
    op_type = OP_TYPE_ABC

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C
        self.Bx = 0

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
    op_type = OP_TYPE_ABC

    def __init__(self, B):
        self.A = 0
        self.B = B
        self.C = 0
        self.Bx = 0

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
    op_type = OP_TYPE_ABx

    def __init__(self, Bx):
        self.Bx = Bx
        self.A = 0
        self.B = 0
        self.C = 0

    def dispatch(self, vm):
        vm.pc += self.Bx

    def __repr__(self):
        return '[pc += %d]' % (self.Bx,)


class BranchIfFalse(Instr):
    """ if not rA then pc += self.Bx
    """
    op_type = OP_TYPE_ABx

    def __init__(self, A, Bx):
        self.A = A
        self.Bx = Bx
        self.B = 0
        self.C = 0

    def dispatch(self, vm):
        if not vm.frame.get(self.A).to_bool():
            vm.pc += self.Bx

    def __repr__(self):
        return '[if not r(%d): pc += %d]' % (self.A, self.Bx,)


# _________________________________________________________________________
# application instructions


# _________________________________________________________________________
# opcode numbers map
op_map = {
    'Halt':         1,
    'MoveLocal':    2,
    'LoadGlobal':   3,
    'LoadCell':     4,
    'LoadConst':    5,
    'StoreGlobal':  6,
    'StoreCell':    7,
    'BuildClosure': 8,
    'Call':         9,
    'TailCall':     10,
    'Return':       11,
    'Branch':       12,
    'BranchIfFalse': 13
}

for op_name, op_num in op_map.items():
    globals()[op_name].op_num = op_num

# _________________________________________________________________________
# make instruction from uint32?
def make_instr(u32):
    op = u32 >> (32 - 5)
    A = (u32 >> (32 - 5 - 9)) & ((1 << 9) - 1)
    B = (u32 >> (32 - 5 - 9 - 9)) & ((1 << 9) - 1)
    C = u32 & ((1 << 9) - 1)
    Bx = (u32 >> (32 - 5 - 9 - 9)) & ((1 << 18) - 1)

    if op == 1:
        return Halt()
    elif op == 2:
        return MoveLocal(A, B)
    elif op == 3:
        return LoadGlobal(A, B)
    elif op == 4:
        return LoadCell(A, B)
    elif op == 5:
        return LoadConst(A, B)
    elif op == 6:
        return StoreGlobal(A, B)
    elif op == 7:
        return StoreCell(A, B)
    elif op == 8:
        return BuildClosure(A, B)
    elif op == 9:
        return Call(A, B, C)
    elif op == 10:
        return TailCall(A, B, C)
    elif op == 11:
        return Return(B)
    elif op == 12:
        return Branch(Bx)
    elif op == 13:
        return BranchIfFalse(A, Bx)
    else:
        raise ValueError('unknown opcode -- %d' % op)

