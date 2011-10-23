""" Low-level intermediate representation and utility structures,

    Or to say, this IR could be directly translated into C without
    too much things to care.
    Later on, memory handling should be happened here as well.

    - Eliminate global hash table and replace it with an array.
    - Emit code for initializing skeleton table and global_variables.

    - Inline LoadConst for primitive types(fixnums, unspec, nil, ...)
    - Inline arg count checks.
    - Most of the copy propagation is done by gcc but be aware of
      jump-and-return, which has a big penalty (~10% in fibonacii!)

    - global lookup is still more expensive than locals (fei hua!)
      but lookup is usually not that expensive (5% in fibo.)
      prelude procedure calls is expensive (total 18% in fibo, for + and <)
      consider inline prelude procedures?
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
    # keep this table in sync with sanya_prelude.h
    prelude_table = {
        '+': 'add',
        '-': 'minus',
        'display': 'display',
        'newline': 'newline',
        '<': 'lessthan',
        '=': 'num_eq',
        'cons': 'cons',
        'car': 'car',
        'cdr': 'cdr',
    }
    def __init__(self, dest, gtable_index):
        self.dest = dest
        self.gtable_index = gtable_index

    def to_c(self, skel, lir_walker):
        name = lir_walker.gid_to_name[self.gtable_index].to_string()
        if name in self.prelude_table:
            return 'v_%d = sanya_g_prelude_%s;' % (self.dest,
                    self.prelude_table[name])
        else:
            return 'v_%d = sanya_g_global_variable_%d;' % (
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
        if lir_walker.toplevel_skel is skel:
            return 'v_%d = sanya_g_toplevel_consts[%d];' % (
                    self.dest, self.const_index)
        else:
            return 'v_%d = ls_closure->as_closure.skeleton->consts[%d];' % (
                    self.dest, self.const_index)

class StoreGlobal(LowLevelInsn):
    def __init__(self, gtable_index, src):
        self.gtable_index = gtable_index
        self.src = src

    def to_c(self, skel, lir_walker):
        name = lir_walker.gid_to_name[self.gtable_index].to_string()
        if name in LoadGlobal.prelude_table:
            return 'sanya_g_prelude_%s = v_%d;' % (
                    LoadGlobal.prelude_table[name], self.src)
        else:
            return 'sanya_g_global_variable_%d = v_%d;' % (
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
        fmt = ('v_%(dest)d = (intptr_t)%(func)s(%(skel_prefix)s_%(index)d, '
               '%(cellval)s, %(freshp)s);')
        fmt %= {
            'dest': self.dest,
            'func': 'sanya_r_build_closure',
            'skel_prefix': '&sanya_g_skeleton',
            'index': self.skel_index,
            'cellval': ('ls_closure->as_closure.cell_values' if skel is not
                         lir_walker.toplevel_skel else 'NULL'),
            'freshp': ('ls_fresh_cells' if skel.fresh_cells
                       else 'NULL')
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
        arglist = [self.dest, self.func] + range(self.func + 1, self.func +
                self.argc + 1)
        return fmt % {
            'argc': self.argc,
            'arglist': ', '.join('v_%d' % var_id for var_id in arglist)
        }

class TailCall(Call):
    def __init__(self, dest, func, argc):
        self.dest = dest
        self.func = func
        self.argc = argc

    def to_c(self, skel, lir_walker):
        if skel is lir_walker.toplevel_skel:
            return Call.to_c(self, skel, lir_walker) # toplevel has not tail
        else:
            fmt = 'SANYA_R_TAILCALLCLOSURE_%(argc)s(%(arglist)s);'
            arglist = [self.func] + range(self.func + 1, self.func +
                    self.argc + 1)
            fmt %= {
                'argc': self.argc,
                'arglist': ', '.join('v_%d' % var_id for var_id in arglist)
            }
            if not skel.fresh_cells: # no need to escape cell values.
                return fmt
            else:
                return ['sanya_r_escape_cell_values(ls_fresh_cells, %d);' % (
                        len(skel.fresh_cells)), fmt]

class Return(LowLevelInsn):
    def __init__(self, src):
        self.src = src

    def to_c(self, skel, lir_walker):
        ret_stmt = 'SANYA_R_RETURN_VALUE(v_%d);' % self.src
        if not skel.fresh_cells: # no need to escape cell values.
            return ret_stmt
        else:
            return ['sanya_r_escape_cell_values(ls_fresh_cells, %d);' % (
                    len(skel.fresh_cells)), ret_stmt]

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
        return ('if (!sanya_r_to_boolean((sanya_t_Object *)v_%d)) '
                'goto LABEL_%d;' % (self.pred, self.label_id))

