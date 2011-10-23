""" Low-level intermediate representation and utility structures,

    Or to say, this IR could be directly translated into C without
    too much things to care.
    Later on, memory handling should be happened here as well.

    - Eliminate global hash table and replace it with an array.
    - Emit code for initializing skeleton table and global_variables.
"""

class LowLevelInsn(object):
    def to_c(self, skel, lir_walker):
        raise NotImplementedError

class Halt(LowLevelInsn):
    def to_c(self, skel, lir_walker):
        return 'sanya_r_halt();'

class MoveLocal(LowLevelInsn):
    def __init__(self, dest, src):
        self.dest = dest
        self.src = src

    def to_c(self, skel, lir_walker):
        return 'v_%d = v_%d;' % (self.dest, self.src)


class LoadGlobal(LowLevelInsn):
    def __init__(self, dest, gtable_index):
        self.dest = dest
        self.gtable_index = gtable_index

    def to_c(self, skel, lir_walker):
        return 'v_%d = sanya_g_global_variables[%d];' % (
                self.dest, self.gtable_index)

class LoadCell(LowLevelInsn):
    def __init__(self, dest, cell_index):
        self.dest = dest
        self.cell_index = cell_index

    def to_c(self, skel, lir_walker):
        return 'v_%d = *(ls_closure->as_closure.cell_values[%d]->ref);' % (
                self.dest, self.cell_index)

class LoadConst(LowLevelInsn):
    def __init__(self, dest, const_index):
        self.dest = dest
        self.const_index = const_index

    def to_c(self, skel, lir_walker):
        return 'v_%d = ls_closure->as_closure.skeleton->consts[%d];' % (
                self.dest, self.const_index)

class StoreGlobal(LowLevelInsn):
    def __init__(self, gtable_index, src):
        self.gtable_index = gtable_index
        self.src = src

    def to_c(self, skel, lir_walker):
        return 'sanya_g_global_variables[%d] = v_%d;' % (
                self.gtable_index, self.src)

class StoreCell(LowLevelInsn):
    def __init__(self, cell_index, src):
        self.cell_index = cell_index
        self.src = src

    def to_c(self, skel, lir_walker):
        return '*(ls_closure->as_closure.cell_values[%d]->ref) = v_%d;' % (
                self.cell_index, self.src)

class BuildClosure(LowLevelInsn):
    def __init__(self, dest, skel_index):
        self.dest = dest
        self.skel_index = skel_index

    def to_c(self, skel, lir_walker):
        skel_to_build = lir_walker.skel_table[self.skel_index]
        fmt = ('v_%(dest)d = (intptr_t)%(func)s(%(skel_tab)s + %(index)d, '
               'ls_closure->as_closure.cell_values, ls_fresh_cells);')
        fmt %= {
            'dest': self.dest,
            'func': 'sanya_r_build_closure',
            'skel_tab': 'sanya_g_skeleton_table',
            'index': self.skel_index
        }
        return ['// Build from skeleton `%s`' % skel_to_build.name,
                fmt]

class Call(LowLevelInsn):
    def __init__(self, dest, func, argc):
        self.dest = dest
        self.func = func
        self.argc = argc

    def to_c(self, skel, lir_walker):
        fmt = 'SANYA_R_CALLCLOSURE_%(argc)s(%(arglist)s);'
        arglist = [self.dest, self.func] + range(self.dest + 1, self.dest +
                self.argc)
        return fmt % {
            'argc': self.argc,
            'arglist': ', '.join('v_%d' % var_id for var_id in arglist)
        }

class Return(LowLevelInsn):
    def __init__(self, src):
        self.src = src

    def to_c(self, skel, lir_walker):
        if not skel.fresh_cells: # no need to escape cell values.
            return 'return v_%d;' % self.src
        else:
            return ['sanya_r_escape_cell_values(ls_fresh_cells, %d);' % (
                    len(skel.fresh_cells)),
                    'return v_%d;' % self.src]

class Label(LowLevelInsn):
    def __init__(self, hir_label):
        self.label_id = hir_label.ident

    def to_c(self, skel, lir_walker):
        return 'LABEL_%d: { /* label statement */ }' % self.label_id


class Branch(LowLevelInsn):
    def __init__(self, hir_label):
        self.label_id = hir_label.ident

    def to_c(self, skel, lir_walker):
        return 'goto LABEL_%d;' % self.label_id


class BranchIfFalse(LowLevelInsn):
    def __init__(self, pred, hir_label):
        self.pred = pred
        self.label_id = hir_label.ident

    def to_c(self, skel, lir_walker):
        return 'if (sanya_r_to_boolean(v_%d)) goto LABEL_%d;' % (
                self.pred, self.label_id)

