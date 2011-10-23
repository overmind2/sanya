""" High-level intermediate representation and utility structures,
    has first-class label.
"""

OP_TYPE_NONE =  0
OP_TYPE_B =     1
OP_TYPE_Bx =    2
OP_TYPE_AB =    3
OP_TYPE_ABC =   4
OP_TYPE_ABx =   5

def op_type_none_init(self):
    pass

def op_type_b_init(self, B):
    self.B = B

def op_type_bx_init(self, Bx):
    self.Bx = Bx

def op_type_ab_init(self, A, B):
    self.A = A
    self.B = B

def op_type_abc_init(self, A, B, C):
    self.A = A
    self.B = B
    self.C = C

def op_type_abx_init(self, A, Bx):
    self.A = A
    self.Bx = Bx

def op_type_none_repr(self):
    return '%s' % self.__class__.__name__

def op_type_b_repr(self):
    return '%-20s%s' % (self.__class__.__name__, self.B)

def op_type_bx_repr(self):
    return '%-20s%s' % (self.__class__.__name__, self.Bx)

def op_type_ab_repr(self):
    return '%-20s%s, %s' % (self.__class__.__name__, self.A, self.B)

def op_type_abc_repr(self):
    return '%-20s%s, %s, %s' % (self.__class__.__name__,
            self.A, self.B, self.C)

def op_type_abx_repr(self):
    return '%-20s%s, %s' % (self.__class__.__name__, self.A, self.Bx)

op_type_init_list = [
    op_type_none_init,
    op_type_b_init,
    op_type_bx_init,
    op_type_ab_init,
    op_type_abc_init,
    op_type_abx_init
]

op_type_repr_list = [
    op_type_none_repr,
    op_type_b_repr,
    op_type_bx_repr,
    op_type_ab_repr,
    op_type_abc_repr,
    op_type_abx_repr
]

class HighLevelInsnMetaclass(type):
    def __new__(cls, name, bases, attr):
        try:
            op_type = attr['op_type']
        except KeyError:
            for base in bases:
                try:
                    op_type = base.op_type
                    break
                except AttributeError:
                    continue
        if '__init__' not in attr:
            attr['__init__'] = op_type_init_list[op_type]
        if '__repr__' not in attr:
            def code_repr(self):
                res = op_type_repr_list[op_type](self)
                if hasattr(self, 'comment_repr'):
                    res = res.ljust(30)
                    res += self.comment_repr()
                return res
            attr['__repr__'] = code_repr

        return super(HighLevelInsnMetaclass, cls).__new__(
                cls, name, bases, attr)

class HighLevelInsn(object):
    __metaclass__ = HighLevelInsnMetaclass
    op_type = OP_TYPE_NONE

class Halt(HighLevelInsn):
    def comment_repr(self):
        return ' ; Halt the program'

class InsnTypeAB(HighLevelInsn):
    op_type = OP_TYPE_AB

class InsnTypeABC(HighLevelInsn):
    op_type = OP_TYPE_ABC

class MoveLocal(InsnTypeAB):
    """ rA = rB
    """
    def comment_repr(self):
        return ' ; rA = rB'

class LoadGlobal(InsnTypeAB):
    """ rA = globalvars[names[kB]]
        In this phase, globalvars is still represented as a
        dict. But in the next phase, it will become an array as well.
    """
    def comment_repr(self):
        return ' ; rA = globalvars[names[kB]]'

class LoadCell(InsnTypeAB):
    """ rA = cells[kB]
    """
    def comment_repr(self):
        return ' ; rA = cells[kB]'

class LoadConst(InsnTypeAB):
    """ rA = consts[kB]
    """
    def comment_repr(self):
        return ' ; rA = consts[kB]'

class StoreGlobal(InsnTypeAB):
    """ globalvars[names[kA]] = rB
    """
    def comment_repr(self):
        return ' ; globalvars[names[kA]] = rB'

class StoreCell(InsnTypeAB):
    """ cells[kA] = rB
    """
    def comment_repr(self):
        return ' ; cells[kA] = rB'

class BuildClosure(InsnTypeAB):
    """ rA = build_closure_and_open_cellvalues(skeleton_registry[B])
    """
    def comment_repr(self):
        return ' ; rA = build_closure(skel_reg[kB])'

class Call(InsnTypeABC):
    """ rA = rB(rB + 1, ..., rB + C)

        Eg, func(1, 2, 3, 4, 5) when func is (lambda (x y . z) ...),
                            rB+0 +1 +2 +3 +4 +5
        stack will be [..., func, 1, 2, 3, 4, 5, ...].
        (3, 4, 5) will be packed to a cons list reversely.
        then, z, y and x will be placed on vm's new frame reversely.

        The current state of vm will be stored in a dump.
    """
    def comment_repr(self):
        return ' ; rA = rB.call(rB + 1, ..., rB + C)'

class TailCall(InsnTypeABC):
    """ TCO-version of call insn.
    """
    def comment_repr(self):
        return ' ; rA = rB.tailcall(rB + 1, ..., rB + C)'

class Return(HighLevelInsn):
    """ Return rB
    """
    op_type = OP_TYPE_B
    def comment_repr(self):
        return ' ; return rB'

class Label(HighLevelInsn):
    """ Place a label here.
    """
    counter = 0
    def __init__(self):
        self.ident = Label.counter
        Label.counter += 1

    def comment_repr(self):
        return ' ; label-id = %d' % self.ident

class Branch(HighLevelInsn):
    """ Unconditional branch, jump to label.
    """
    def __init__(self, label):
        self.label = label

    def comment_repr(self):
        return ' ; goto label %d' % self.label.ident

class BranchIfFalse(HighLevelInsn):
    """ Conditional branch, jump to label if rA is false.
    """
    def __init__(self, A, label):
        self.A = A
        self.label = label

    def comment_repr(self):
        return ' ; if !rA: goto label %d' % self.label.ident

# ______________________________________________________________________ 
# High-level skeleton representation.

class ClosureSkeleton(object):
    def __init__(self, hir_list, consts, names, frame_size, cell_recipt,
            fresh_cells, nb_args, varargs_p, skeleton_registry, name=None):
        self.hir_list = hir_list
        self.consts = consts
        self.names = names
        self.frame_size = frame_size
        self.cell_recipt = cell_recipt
        self.fresh_cells = fresh_cells
        self.nb_args = nb_args
        self.varargs_p = varargs_p
        self.skeleton_registry = skeleton_registry
        self.name = name

    def __repr__(self):
        from cStringIO import StringIO
        buf = StringIO()
        w = lambda s: buf.write(str(s))
        wln = lambda s: (w(s), w('\n'))
        windent = lambda s, n=2: (w(' ' * n), w(s), w('\n'))

        windent('%d Consts:' % len(self.consts))
        for i, const in enumerate(self.consts):
            windent('  - const[%d] = %s' % (i, const))

        windent('%d Names:' % len(self.names))
        for i, name in enumerate(self.names):
            windent('  - name[%d] = %s' % (i, name))

        windent('%d Frame slots.' % self.frame_size)
        windent('%d Cell values from recipt.' % len(self.cell_recipt))
        windent('%d Fresh cells.' % len(self.fresh_cells))

        windent('%s Arguments.' % self.nb_args)
        windent('Is %svariadic.' % ('' if self.varargs_p else 'not '))

        windent('')
        windent('Disassembly')
        windent('-----------')
        for insn in self.hir_list:
            windent(insn, 4)

        return buf.getvalue()

