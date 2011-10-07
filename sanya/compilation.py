""" Things to concern:
    - How to make sure cellvalues are shared? <== The main point of this impl.
    - How to efficiently allocate frame slots?
    - Deferred allocation of frame slot: Yes I can learn from my libjit impl.
"""

from pypy.rlib.jit import dont_look_inside
from sanya.instruction_set import (Instr, MoveLocal, LoadConst,
        LoadCell, LoadGlobal, StoreCell, StoreGlobal, BuildClosure,
        Return, BranchIfFalse, Branch, TailCall, Call)
from sanya.objectmodel import w_unspecified, scmlist2py
from sanya.closure import W_Skeleton

class SchemeSyntaxError(Exception):
    pass

@dont_look_inside
def compile_list_of_expr(expr_list):
    # using default sematics.
    walker = SkeletonWalker()
    walker.visit_list_of_expr(expr_list)
    return walker.to_closure_skeleton()

# XXX: how to better represent multiple flags?
class CompilationFlag(object):
    TCO = 0x1
    DEST = 0x2
    BAR = 0x4
    WTF = 0x8

    def __init__(self, flags=0x0, desired_destination=None):
        self.flags = flags
        self.dest = desired_destination
        if desired_destination:
            assert desired_destination.is_assignable()
            self.flags |= self.DEST

    def copy(self):
        return CompilationFlag(self.flags, self.dest)

    def has_tco(self):
        return self.flags & self.TCO

    def has_dest(self):
        return self.flags & self.DEST

    def get_dest(self):
        return self.dest


class Walker(object):
    def visit(self, thing, flag=None):
        raise NotImplementedError

class SkeletonWalker(Walker):
    def __init__(self, parent_skeleton=None):
        self.global_variables = {} # hmmm... not used until we can modify glvar
        self.instrs = []
        self.frame_size = 0
        self.consts = []
        self.const_index_map = {} # maps consts to its id
        self.cell_recipe = [] # list of packed ints, @see closure.ClosSkel 

        # temporarily maps frame index to shadow_cv's index
        self.fresh_cell_map = {}
        self.fresh_cells = [] # list of ints

        self.local_variables = {} # frame variable and opened cellvalues
        self.nb_args = 0
        self.varargs_p = False
        if parent_skeleton:
            self.skeleton_registry = parent_skeleton.skeleton_registry
        else:
            self.skeleton_registry = []

        self.parent_skeleton = parent_skeleton
        self.deferred_lambdas = []

    @dont_look_inside
    def to_closure_skeleton(self):
        for dfd_lambda in self.deferred_lambdas:
            dfd_lambda.resume_compilation()
        self.deferred_lambdas = []

        if self.parent_skeleton: # is not toplevel
            return W_Skeleton(self.instrs,
                    self.consts, self.frame_size,
                    self.cell_recipe, self.fresh_cells,
                    self.nb_args, self.varargs_p, None)
        else: # toplevel -- should pass its closure skeleton table
            return W_Skeleton(self.instrs,
                    self.consts, self.frame_size,
                    self.cell_recipe, self.fresh_cells,
                    self.nb_args, self.varargs_p, self.skeleton_registry)

    def alloc_frame_slot(self):
        res = self.frame_size
        self.frame_size += 1
        return res

    def new_const_slot(self, w_obj):
        if w_obj in self.const_index_map:
            consts_id = self.const_index_map[w_obj]
        else:
            consts_id = self.const_index_map[w_obj] = len(self.consts)
            self.consts.append(w_obj)
        return consts_id

    def new_skel_slot(self, w_skel):
        self.skeleton_registry.append(w_skel)
        return len(self.skeleton_registry) - 1

    def new_fresh_cell(self, frameslot):
        slot_id = len(self.fresh_cells)
        self.fresh_cells.append(frameslot)
        return slot_id

    def emit(self, instr):
        assert isinstance(instr, Instr)
        self.instrs.append(instr)

    @dont_look_inside
    def visit_list_of_expr(self, w_exprlist):
        """ Visit a list of expression, compile them to a closure skeleton with
            no cellvalues, and append a return statement to the instrs
            generated. After then, to_closure_skeleton() will do the rest work.
        """
        tco_flag = CompilationFlag(CompilationFlag.TCO)
        last_value_repr = None
        for i in xrange(len(w_exprlist)): # RPython doesn't like enumerate...
            w_expr = w_exprlist[i]
            if i == len(w_exprlist) - 1:
                last_value_repr = self.visit(w_expr, tco_flag)
            else:
                last_value_repr = self.visit(w_expr)
        self.emit(Return(self.cast_to_local(last_value_repr).to_index()))

    @dont_look_inside
    def visit(self, w_object, flag=None):
        if flag is None:
            flag = CompilationFlag()
        return w_object.accept_compiler_walker(self, flag)

    @dont_look_inside
    def local_lookup(self, w_symbol, flag=None):
        """ Recursively lookup for a symbol until toplevel is reached.
        """
        assert w_symbol.is_symbol()
        sval = w_symbol.to_string()

        if sval in self.local_variables:
            return self.local_variables[sval]
        else:
            if self.parent_skeleton:
                # Firstly look at outer's locals to look for cellvalues.
                # Since we need exactly to open the cellvalue exactly one
                # level inside the closure with that frame.
                found = self.parent_skeleton.local_lookup(w_symbol, flag)
                if found.on_frame():
                    # Here we share the cellvalue between sibling closures
                    if (found.slotindex in
                            self.parent_skeleton.fresh_cell_map):
                        shadow_id = self.parent_skeleton.fresh_cell_map[
                            found.slotindex]
                    else:
                        shadow_id = self.parent_skeleton.new_fresh_cell(
                                found.slotindex)
                        self.parent_skeleton.fresh_cell_map[
                            found.slotindex] = shadow_id

                    new_cval_index = len(self.cell_recipe)
                    self.cell_recipe.append(
                            (shadow_id << 1) | 0x1)
                    value_repr = CellValueRepr(new_cval_index)

                elif found.is_cell(): # copy from it
                    new_cval_index = len(self.cell_recipe)
                    self.cell_recipe.append( # copy outer cellval
                            found.cellindex << 1)
                    value_repr = CellValueRepr(new_cval_index)

                elif found.is_global():
                    return found
                else:
                    raise ValueError('unknown value repr -- %s' % found)
                self.local_variables[sval] = value_repr
                return value_repr
            else:
                # If we cannot find the symbol, then it must be a global.
                return GlobalValueRepr(w_symbol)

    def visit_fixnum_const(self, w_fixnum, flag=None):
        assert w_fixnum.is_fixnum()
        return ConstValueRepr(self.new_const_slot(w_fixnum))

    def visit_boolean_const(self, w_boolean, flag=None):
        assert w_boolean.is_boolean()
        return ConstValueRepr(self.new_const_slot(w_boolean))

    special_form_list = 'define set! if quote lambda begin'.split(' ')
    def symbol_is_special_form(self, w_symbol):
        assert w_symbol.is_symbol()
        sval = w_symbol.to_string()
        return sval in self.special_form_list

    @dont_look_inside
    def visit_special_form(self, w_proc, w_args, flag):
        sval = w_proc.to_string()
        if sval == 'define':
            # @see visit_binding
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if len(lst) != 2 or not w_rest.is_null(): # (define name expr)
                raise SchemeSyntaxError, 'define require 2 args'

            w_name = lst[0]
            if not w_name.is_symbol():
                raise SchemeSyntaxError, ('define require the first arg '
                        'to be symbol -- got %s' % w_name.to_string())
            w_expr = lst[1]
            value_repr = self.visit(w_expr)
            self.visit_binding(w_name, value_repr) # create binding for define
            return ConstValueRepr(self.new_const_slot(w_unspecified))

        elif sval == 'set!':
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if len(lst) != 2 or not w_rest.is_null(): # (define name expr)
                raise SchemeSyntaxError, 'set! require 2 args'

            w_name = lst[0]
            if not w_name.is_symbol():
                raise SchemeSyntaxError, ('set! require the first arg '
                        'to be symbol -- got %s' % w_name.to_string())
            w_expr = lst[1]
            value_repr = self.visit(w_expr)
            self.visit_rebind(w_name, value_repr) # change binding for define
            return ConstValueRepr(self.new_const_slot(w_unspecified))

        elif sval == 'if':
            # (if pred iftrue [else])
            if flag.has_dest():
                result_value_repr = flag.get_dest()
            else:
                result_value_repr = FrameValueRepr(self.alloc_frame_slot())

            lst = []
            w_rest = scmlist2py(w_args, lst)
            if len(lst) not in (2, 3) or not w_rest.is_null():
                raise SchemeSyntaxError, 'if require 2 to 3 args'

            w_pred = lst[0]
            w_iftrue = lst[1]

            # predicate value repr
            # XXX: Note that this is a temporary variable and can be reused
            #      if we return this frame slot to the allocator.
            pred_local_val = self.cast_to_local(self.visit(w_pred))

            # saved instr index, for jump to else
            iftrue_branch_instr_index = len(self.instrs)
            self.instrs.append(None) # branch length to be calculated

            # if_true instrs
            iftrue_result_repr = self.visit(w_iftrue, flag)
            self.set_frame_slot(result_value_repr, iftrue_result_repr)
            iftrue_branch_jumpby = (len(self.instrs) -
                    iftrue_branch_instr_index)
            self.instrs[iftrue_branch_instr_index] = BranchIfFalse(
                    pred_local_val.to_index(), iftrue_branch_jumpby)

            iffalse_branch_instr_index = len(self.instrs)
            self.instrs.append(None) # branch length to be calculated
            if len(lst) == 2:
                self.set_frame_slot(result_value_repr,
                        ConstValueRepr(self.new_const_slot(w_unspecified)))
            else: # has else
                w_iffalse = lst[2]
                iffalse_result_repr = self.visit(w_iffalse, flag)
                self.set_frame_slot(result_value_repr, iffalse_result_repr)

            iffalse_branch_jumpby = (len(self.instrs) -
                    iffalse_branch_instr_index - 1)
            self.instrs[iffalse_branch_instr_index] = Branch(
                    iffalse_branch_jumpby)
            return result_value_repr

        elif sval == 'quote':
            # (quote datum)
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if len(lst) != 1 or not w_rest.is_null():
                raise SchemeSyntaxError, 'quote require 1 arg'
            return ConstValueRepr(self.new_const_slot(lst[0]))

        elif sval == 'lambda':
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if not w_rest.is_null():
                raise SchemeSyntaxError, 'lambda -- not a well-formed list'
            if len(lst) < 2:
                raise SchemeSyntaxError, 'lambda -- missing expression'
            if flag.has_dest():
                frame_val_repr = flag.get_dest()
            else:
                frame_val_repr = FrameValueRepr(self.alloc_frame_slot())
            current_instr_pos = len(self.instrs)
            self.instrs.append(None)
            # compile the lambdas in the end
            self.deferred_lambdas.append(DeferredLambdaCompilation(
                self, lst, current_instr_pos, frame_val_repr))
            return frame_val_repr

        elif sval == 'begin':
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if not w_rest.is_null():
                raise SchemeSyntaxError, 'begin -- not a well-formed list'
            for i, w_expr in enumerate(lst):
                if i != len(lst) - 1:
                    self.visit(w_expr)
                else:
                    return self.visit(w_expr, flag)
            # when there is no args: return unspecified
            return ConstValueRepr(self.new_const_slot(w_unspecified))

        else:
            raise ValueError, 'not a special form'

    @dont_look_inside
    def visit_binding(self, w_name, value_repr):
        """ This will be simpler -- if w_name is in local namespace, this is
            the same as set!. Otherwise, create a new binding.

            If we are in toplevel, then generate/change a global binding.
            Otherwise, generate/change a local binding.

            (define w_name value_repr)
        """
        assert w_name.is_symbol()
        sval = w_name.to_string()

        if sval in self.local_variables:
            # modify binding
            old_val = self.local_variables[sval]
            if old_val.on_frame(): # set frame
                self.set_frame_slot(old_val, value_repr)
            elif old_val.is_cell(): # set cell
                self.set_cell_value(old_val, value_repr)
            else:
                raise ValueError, 'unreachable'
        else:
            if not self.parent_skeleton: # We are in toplevel
                # create new global binding
                new_val = GlobalValueRepr(w_name)
                self.global_variables[sval] = new_val
                self.set_global_value(new_val, value_repr)
            else:
                # create new local binding
                new_val = FrameValueRepr(self.alloc_frame_slot())
                self.local_variables[sval] = new_val
                self.set_frame_slot(new_val, value_repr)

    @dont_look_inside
    def visit_rebind(self, w_name, value_repr):
        """ (set! w_name value_repr)
        """

        assert w_name.is_symbol()
        sval = w_name.to_string()

        if sval in self.local_variables:
            # modify binding
            old_val = self.local_variables[sval]
            if old_val.on_frame(): # set frame
                self.set_frame_slot(old_val, value_repr)
            elif old_val.is_cell(): # set cell
                self.set_cell_value(old_val, value_repr)
            else:
                raise ValueError, 'unreachable'
        else:
            # do a recursive lookup.
            val_repr_got = self.local_lookup(w_name)
            # it should be a cell or a global now.
            if val_repr_got.is_cell():
                self.set_cell_value(val_repr_got, value_repr)
            elif val_repr_got.is_global():
                self.set_global_value(val_repr_got, value_repr)
            else:
                raise ValueError, 'unreachable'

    @dont_look_inside
    def visit_application(self, w_proc, w_args, flag):
        lst = []
        w_rest = scmlist2py(w_args, lst)
        if not w_rest.is_null():
            raise SchemeSyntaxError('application -- not a well-formed list')
        # allocate len(lst) + 1 frame slots
        # XXX: ensure they sit together.
        proc_slot = FrameValueRepr(self.alloc_frame_slot())
        arg_slots = [FrameValueRepr(self.alloc_frame_slot())
                for i in xrange(len(lst))]

        # evaluate the proc and the args
        proc_visit_flag = CompilationFlag(0, desired_destination=proc_slot)
        proc_val_repr = self.visit(w_proc, proc_visit_flag)
        self.set_frame_slot(proc_slot, proc_val_repr) # could be no-op

        for i in xrange(len(lst)):
            # since enumerate is not supported in RPython...
            w_expr = lst[i]
            dest_slot = arg_slots[i]
            arg_visit_flag = CompilationFlag(0, desired_destination=dest_slot)
            arg_val_repr = self.visit(w_expr, arg_visit_flag)
            self.set_frame_slot(dest_slot, arg_val_repr)

        if flag.has_dest():
            result_value_repr = flag.get_dest()
        else:
            result_value_repr = FrameValueRepr(self.alloc_frame_slot())
        # call and return
        if flag.has_tco():
            self.emit(TailCall(result_value_repr.to_index(),
                    proc_slot.to_index(), len(lst)))
        else:
            self.emit(Call(result_value_repr.to_index(),
                    proc_slot.to_index(), len(lst)))
        return result_value_repr

    @dont_look_inside
    def cast_to_local(self, value_repr):
        if value_repr.on_frame():
            return value_repr
        elif value_repr.is_const():
            res = FrameValueRepr(self.alloc_frame_slot())
            instr = LoadConst(res.to_index(), value_repr.to_index())
            self.emit(instr)
            return res
        elif value_repr.is_cell():
            res = FrameValueRepr(self.alloc_frame_slot())
            instr = LoadCell(res.to_index(), value_repr.to_index())
            self.emit(instr)
            return res
        elif value_repr.is_global():
            res = FrameValueRepr(self.alloc_frame_slot())
            instr = LoadGlobal(res.to_index(),
                    self.new_const_slot(value_repr.w_symbol))
            self.emit(instr)
            return res
        else:
            raise ValueError, 'unreached'

    @dont_look_inside
    def set_frame_slot(self, old_repr, new_repr):
        assert old_repr.on_frame()
        if old_repr is new_repr:
            return # moving self to self: ignored
        if new_repr.on_frame():
            self.emit(MoveLocal(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_cell():
            self.emit(LoadCell(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_const():
            self.emit(LoadConst(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_global():
            self.emit(LoadGlobal(old_repr.to_index(),
                self.new_const_slot(new_repr.w_symbol)))
        else:
            raise ValueError, 'unreached'

    def set_cell_value(self, cell_repr, new_repr):
        assert cell_repr.is_cell()
        if cell_repr is new_repr:
            return # well...
        self.emit(StoreCell(cell_repr.to_index(),
            self.cast_to_local(new_repr).to_index()))

    def set_global_value(self, global_repr, new_repr):
        assert global_repr.is_global()
        if global_repr is new_repr:
            return # well...
        self.emit(StoreGlobal(self.new_const_slot(global_repr.w_symbol),
            self.cast_to_local(new_repr).to_index()))


class IntermediateRepr(object):
    """ A intermediate representation that is used during compilation.
    """
    def to_index(self):
        raise NotImplementedError

    def on_frame(self):
        return False

    def is_const(self):
        return False

    def is_cell(self):
        return False

    def is_global(self):
        return False

    def is_assignable(self):
        return False

class FrameValueRepr(IntermediateRepr):
    """ A value that is on stack.
    """
    def __init__(self, slotindex):
        self.slotindex = slotindex

    def to_index(self):
        return self.slotindex

    def on_frame(self):
        return True

    def is_assignable(self):
        return True

class ConstValueRepr(IntermediateRepr):
    def __init__(self, constindex):
        self.constindex = constindex

    def to_index(self):
        return self.constindex

    def is_const(self):
        return True

class CellValueRepr(IntermediateRepr):
    """ A value that is on local cellvalues.
    """
    def __init__(self, cellindex):
        self.cellindex = cellindex

    def to_index(self):
        return self.cellindex

    def is_cell(self):
        return True

    def is_assignable(self):
        return True

class GlobalValueRepr(IntermediateRepr):
    def __init__(self, w_symbol):
        assert w_symbol.is_symbol()
        self.w_symbol = w_symbol

    def is_global(self):
        return True

    def is_assignable(self):
        return True

class DeferredLambdaCompilation(object):
    def __init__(self, walker, expr_list, instrindex, dest_val_repr):
        self.walker = walker # the walker
        self.expr_list = expr_list # the lambda formals and body, a pylist
        self.instrindex = instrindex # the instruction index
        self.dest_val_repr = dest_val_repr # a frame slot

    @dont_look_inside
    def resume_compilation(self):
        lambda_walker = SkeletonWalker(self.walker)
        w_formals = self.expr_list[0]
        lambda_body = self.expr_list[1:]

        # decoding lambda arguments and test them
        arg_list = []
        w_rest = scmlist2py(w_formals, arg_list)
        for w_argname in arg_list:
            if not w_argname.is_symbol():
                raise SchemeSyntaxError('lambda -- formal varargs should be '
                    'nothing but a symbol, got %s' % w_argname.to_string())

        lambda_walker.nb_args = len(arg_list) # set positional argcount
        if w_rest.is_null():
            lambda_walker.varargs_p = False
        else:
            if not w_rest.is_symbol():
                raise SchemeSyntaxError('lambda -- formal varargs should be '
                        'nothing but a symbol, got %s' % w_rest.to_string())
            else:
                lambda_walker.varargs_p = True

        # fill in the frame slots using those arguments
        for w_argname in arg_list:
            frame_slot_repr = FrameValueRepr(lambda_walker.alloc_frame_slot())
            lambda_walker.local_variables[w_argname.to_string()] \
                    = frame_slot_repr

        # if vararg
        if lambda_walker.varargs_p:
            frame_slot_repr = FrameValueRepr(lambda_walker.alloc_frame_slot())
            lambda_walker.local_variables[w_rest.to_string()] \
                    = frame_slot_repr

        # compile the body. XXX: create a global skeleton table like lua?
        lambda_walker.visit_list_of_expr(lambda_body)
        w_lambda_skeleton = lambda_walker.to_closure_skeleton()
        self.walker.instrs[self.instrindex] = BuildClosure(
            self.dest_val_repr.to_index(),
            self.walker.new_skel_slot(w_lambda_skeleton))

