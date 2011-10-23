
from cStringIO import StringIO
import hir
import lir

def compile_from_hir_walker(hir_walker):
    llw = LowLevelWalker(hir_walker)
    cg = CodeGenerator(llw)
    return cg.generate()

class CodeGenerator(object):
    def __init__(self, lir_walker):
        self.walker = lir_walker

    def generate(self):
        self._indent = 0
        self.buf = StringIO()
        self.emit_global_decl()
        for i, skel in enumerate(self.walker.skel_table):
            self.emit_one_skeleton_func(i, skel)
        self.emit_toplevel_func(self.walker.toplevel_skel)
        self.emit_bootstrap_func()
        self.emit_main_func()
        return self.buf.getvalue()

    def indent(self):
        self._indent += 4

    def dedent(self):
        self._indent -= 4

    def emit(self, s):
        self.buf.write(' ' * self._indent)
        self.buf.write(s)
        self.buf.write('\n')

    def emit_bootstrap_func(self):
        self.emit('')
        self.emit('void')
        self.emit('sanya_r_bootstrap()')
        self.emit('{')
        self.indent()

        # set properties for skeletons
        for i, skel in enumerate(self.walker.skel_table):
            skel_name = 'sanya_g_skeleton_%d' % i
            self.emit('%s.name = "%s";' % (skel_name, skel.name))
            self.emit('%s.consts = malloc(sizeof(intptr_t) * %d);' % (
                skel_name, len(skel.consts)))
            # consts.
            for nth_const, const_val in enumerate(skel.consts):
                if const_val.is_fixnum():
                    self.emit('%s.consts[%d] = sanya_r_W_Fixnum(%d);' % (
                        skel_name, nth_const, const_val.ival))
                elif const_val.is_symbol():
                    self.emit('%s.consts[%d] = sanya_r_W_Symbol("%s");' % (
                        skel_name, nth_const, const_val.sval))
                elif const_val.is_unspecified():
                    self.emit('%s.consts[%d] = sanya_r_W_Unspecified();' % (
                        skel_name, nth_const))
                else:
                    raise ValueError('unsupported %s' % const_val)
            # cell_recipt, initialized in global section
            self.emit('%s.cell_recipt = sanya_g_skeleton_cell_recipt_%d;' % (
                skel_name, i))
            self.emit('%s.nb_cells = %d;' % (skel_name, len(skel.cell_recipt)))
            # function ptr
            self.emit('%s.closure_ptr = sanya_g_closure_ptr_%d;' % (
                skel_name, i))
            # arg count
            self.emit('%s.nb_args = %d;' % (skel_name, skel.nb_args))
            self.emit('%s.varargs_p = %d;' % (skel_name, skel.varargs_p))
            # done
            self.emit('')

        # dont forget about toplevel..
        skel = self.walker.toplevel_skel
        consts_name = 'sanya_g_toplevel_consts'
        self.emit('%s = malloc(sizeof(intptr_t) * %d);' % (
            consts_name, len(skel.consts)))
        # consts.
        for nth_const, const_val in enumerate(skel.consts):
            if const_val.is_fixnum():
                self.emit('%s[%d] = sanya_r_W_Fixnum(%d);' % (
                    consts_name, nth_const, const_val.ival))
            elif const_val.is_symbol():
                self.emit('%s[%d] = sanya_r_W_Symbol("%s");' % (
                    consts_name, nth_const, const_val.sval))
            elif const_val.is_unspecified():
                self.emit('%s[%d] = sanya_r_W_Unspecified();' % (
                    consts_name, nth_const))
            else:
                raise ValueError('unsupported %s' % const_val)

        self.dedent()
        self.emit('}')

    def emit_main_func(self):
        self.emit('')
        self.emit('int')
        self.emit('main(int argc, char **argv)')
        self.emit('{')
        self.indent()
        self.emit('sanya_r_initialize_prelude();  // @see sanya_prelude.*');
        self.emit('sanya_r_bootstrap();');
        self.emit('sanya_r_toplevel();');
        self.emit('return 0;')
        self.dedent()
        self.emit('}')

    def emit_global_decl(self):
        self.emit('#include "sanya_runtime.h"')
        self.emit('#include "sanya_object.h"')
        self.emit('#include "sanya_prelude.h"')
        self.emit('')
        self.emit('// Globals')
        for i in xrange(len(self.walker.global_variable_list)):
            self.emit('intptr_t sanya_g_global_variable_%d;' % i)
        for i in xrange(len(self.walker.skel_table)):
            self.emit('sanya_t_ClosureSkeleton sanya_g_skeleton_%d;' % i)
        # cell recipts
        for i, skel in enumerate(self.walker.skel_table):
            fmt = 'intptr_t sanya_g_skeleton_cell_recipt_%d[] = { %s };'
            fmt %= (i, ', '.join('%s' % recipt
                                 for recipt in skel.cell_recipt))
            self.emit(fmt)

        self.emit('intptr_t *sanya_g_toplevel_consts;')
        self.emit('')

    def emit_toplevel_func(self, skel):
        self.emit('// Toplevel')
        self.emit('void sanya_r_toplevel()')
        self.emit('{')
        self.indent()

        # local variable declaration
        self.emit('intptr_t %s;' % (', '.join('v_%d' % vid for vid in
            range(0, skel.frame_size + 1))))

        # for each instruction, translate to c
        for lir_insn in skel.lir_list:
            c_line = lir_insn.to_c(skel, self.walker) # may be a list or string
            if isinstance(c_line, basestring):
                self.emit(c_line)
            else:
                for line in c_line:
                    self.emit(line)
        self.dedent()
        self.emit('}  // End of toplevel.')

    def emit_one_skeleton_func(self, skel_id, skel):
        # Debug info
        self.emit('// Closure `%s`' % skel.name)
        # function head
        self.emit('intptr_t')
        # func args
        arglist = ['sanya_t_Object *ls_closure']
        for i in range(skel.nb_args):
            arglist.append('intptr_t v_%d' % i)

        # func name
        self.emit('sanya_g_closure_ptr_%d(%s)' % (skel_id,
            ', '.join(arglist)))
        self.emit('{')
        self.indent()

        # local var decl
        self.emit('intptr_t %s;' % (', '.join('v_%d' % vid for vid in
            range(skel.nb_args, skel.frame_size + 1))))
        if skel.fresh_cells:
            self.emit('sanya_t_CellValue *ls_fresh_cells[%d];' %
                    len(skel.fresh_cells))

        # fresh cell building
        for i, slot_index in enumerate(skel.fresh_cells):
            self.emit('ls_fresh_cells[%d] = sanya_r_build_cell_value(&v_%d);'
                    % (i, slot_index))

        # translate instructions
        for lir_insn in skel.lir_list:
            c_line = lir_insn.to_c(skel, self.walker) # may be a list or string
            if isinstance(c_line, basestring):
                self.emit(c_line)
            else:
                for line in c_line:
                    self.emit(line)

        # end of func.
        self.dedent()
        self.emit('}  // End of closure `%s`' % skel.name)
        self.emit('')


class LowLevelWalker(object):
    """ TODO: compare toplevel define with total LoadGlobals and figure
        out what prelude procedures should we add.
    """
    def __init__(self, hir_walker):
        self.global_variable_list = []
        self.global_variable_id_map = {}

        self.toplevel_skel = LowLevelSkeleton(self,
                hir_walker.to_closure_skeleton())
        self.skel_table = [LowLevelSkeleton(self, skel) for skel in
                           hir_walker.skeleton_registry]

        self.gid_to_name = dict((val, key) for (key, val) in
                self.global_variable_id_map.iteritems())

    def new_global_var(self, name):
        """ Return a global variable index
        """
        if name not in self.global_variable_id_map:
            nid = len(self.global_variable_list)
            self.global_variable_list.append(name)
            self.global_variable_id_map[name] = nid
            return nid
        else:
            return self.global_variable_id_map[name]

class LowLevelSkeleton(object):
    def __init__(self, lir_walker, hir_skeleton):
        # redirect load/store globals to array.
        self.names_to_gtable_id = []
        for name in hir_skeleton.names:
            self.names_to_gtable_id.append(lir_walker.new_global_var(name))

        self.lir_list = []
        for hir_code in hir_skeleton.hir_list:
            self.lir_list.append(self.translate_hir(hir_code))

        self.consts = hir_skeleton.consts
        self.frame_size = hir_skeleton.frame_size
        self.cell_recipt = hir_skeleton.cell_recipt
        self.fresh_cells = hir_skeleton.fresh_cells
        self.nb_args = hir_skeleton.nb_args
        self.varargs_p = hir_skeleton.varargs_p
        self.name = hir_skeleton.name

    def translate_hir(self, hir_code):
        isa = lambda tp: isinstance(hir_code, tp)
        if isa(hir.Halt):
            return lir.Halt()
        if isa(hir.MoveLocal):
            return lir.MoveLocal(hir_code.A, hir_code.B)
        if isa(hir.LoadGlobal):
            return lir.LoadGlobal(hir_code.A,
                    self.names_to_gtable_id[hir_code.B])
        if isa(hir.LoadCell):
            return lir.LoadCell(hir_code.A, hir_code.B)
        if isa(hir.LoadConst):
            return lir.LoadConst(hir_code.A, hir_code.B)
        if isa(hir.StoreGlobal):
            return lir.StoreGlobal(self.names_to_gtable_id[hir_code.A],
                    hir_code.B)
        if isa(hir.StoreCell):
            return lir.StoreCell(hir_code.A, hir_code.B)
        if isa(hir.BuildClosure):
            return lir.BuildClosure(hir_code.A, hir_code.B)
        if isa(hir.Call) or isa(hir.TailCall):
            return lir.Call(hir_code.A, hir_code.B, hir_code.C)
        if isa(hir.Return):
            return lir.Return(hir_code.B)
        if isa(hir.Label):
            return lir.Label(hir_code)
        if isa(hir.Branch):
            return lir.Branch(hir_code.label)
        if isa(hir.BranchIfFalse):
            return lir.BranchIfFalse(hir_code.A, hir_code.label)

        raise TypeError, 'no such instr'

