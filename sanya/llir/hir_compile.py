""" Compile scheme expression to HIR.
"""

import hir
from sanya.objectmodel import (scmlist2py, w_unspecified, make_symbol,
        W_Pair, pylist2scm)
from sanya.compilation import SchemeSyntaxError

def compile_list_of_expr(expr_list):
    walker = SexprWalker()
    walker.visit_list_of_expr(expr_list)
    toplevel_skeleton = walker.to_closure_skeleton()
    return toplevel_skeleton, walker

class SexprWalker(object):
    def __init__(self, parent_walker=None):
        self.global_variables = {}
        self.insn_list = []
        self.frame_size = 0
        self.names = [] # used in LocalGlobal/StoreGlobal
        self.name_id_map = {}
        self.consts = []
        self.cell_recipe = [] # list of packed ints, @see closure.ClosSkel 

        # temporarily maps frame index to shadow_cv's index
        self.fresh_cell_map = {}
        self.fresh_cells = [] # list of ints

        self.parent_walker = parent_walker
        if parent_walker:
            self.skeleton_registry = parent_walker.skeleton_registry
        else:
            self.skeleton_registry = []
        if self.is_toplevel():
            self.local_variables = None # no local var in toplevel
            self.name = 'toplevel'
        else:
            self.local_variables = {} # frame variable and opened cellvalues
            self.name = '#f'
        self.nb_args = 0
        self.varargs_p = False

        self.deferred_lambdas = []

    def is_toplevel(self):
        return not self.parent_walker

    def to_closure_skeleton(self):
        self.resolve_deferred_lambdas()

        if not self.is_toplevel():
            return hir.ClosureSkeleton(self.insn_list,
                    self.consts, self.names, self.frame_size,
                    self.cell_recipe, self.fresh_cells,
                    self.nb_args, self.varargs_p, None, name=self.name)
        else: # toplevel -- should pass its closure skeleton table
            return hir.ClosureSkeleton(self.insn_list,
                    self.consts, self.names, self.frame_size,
                    self.cell_recipe, self.fresh_cells,
                    self.nb_args, self.varargs_p, self.skeleton_registry,
                    name=self.name)

    def resolve_deferred_lambdas(self):
        for dfd_lambda in self.deferred_lambdas:
            dfd_lambda.resume_compilation()
        self.deferred_lambdas = []

    def alloc_frame_slot(self):
        res = self.frame_size
        self.frame_size += 1
        return res

    def new_const_slot(self, w_obj):
        consts_id = len(self.consts)
        self.consts.append(w_obj)
        return consts_id

    def new_name_slot(self, w_name):
        assert w_name.is_symbol()
        if w_name in self.name_id_map:
            return self.name_id_map[w_name]
        else:
            name_id = len(self.names)
            self.names.append(w_name)
            self.name_id_map[w_name] = name_id
            return name_id

    def new_skel_slot(self, w_skel):
        self.skeleton_registry.append(w_skel)
        return len(self.skeleton_registry) - 1

    def new_fresh_cell(self, frameslot):
        slot_id = len(self.fresh_cells)
        self.fresh_cells.append(frameslot)
        return slot_id

    def emit(self, insn):
        assert isinstance(insn, hir.HighLevelInsn)
        self.insn_list.append(insn)

    def visit_list_of_expr(self, w_exprlist):
        """ Visit a list of expression, compile them to a closure skeleton with
            no cellvalues, and append a return statement to the insn_list
            generated. After then, to_closure_skeleton() will do the rest work.
        """
        last_value_repr = None
        for i, w_expr in enumerate(w_exprlist):
            if i == len(w_exprlist) - 1: # is last -- tail
                last_value_repr = self.visit(w_expr, tail=True)
            else:
                last_value_repr = self.visit(w_expr)
        if self.is_toplevel():
            self.emit(hir.Halt())
        else:
            self.emit(hir.Return(
                self.cast_to_local(last_value_repr).to_index()))

    def visit(self, w_object, tail=False):
        if w_object.is_fixnum():
            return ConstValueRepr(self.new_const_slot(w_object))
        if w_object.is_symbol():
            return self.local_lookup(w_object)
        if w_object.is_pair():
            return self.visit_pair(w_object, tail)
        if w_object.is_nil():
            raise TypeError, 'nil visited'
        if w_object.is_boolean():
            return ConstValueRepr(self.new_const_slot(w_object))
        if w_object.is_unspecified():
            return ConstValueRepr(self.new_const_slot(w_object))
        else:
            raise TypeError, 'unknown expression appeares in compilation'

    def visit_pair(self, w_pair, tail=False):
        if w_pair.car.is_symbol() and self.symbol_is_special_form(w_pair.car):
            return self.visit_special_form(w_pair.car, w_pair.cdr, tail)
        else:
            return self.visit_application(w_pair.car, w_pair.cdr, tail)

    def local_lookup(self, w_symbol):
        """ Recursively lookup for a symbol until toplevel is reached.
        """
        assert w_symbol.is_symbol()

        if not self.is_toplevel() and w_symbol in self.local_variables:
            return self.local_variables[w_symbol]
        else:
            if not self.is_toplevel():
                # Firstly look at outer's locals to look for cellvalues.
                # Since we need exactly to open the cellvalue exactly one
                # level inside the closure with that frame.
                found = self.parent_walker.local_lookup(w_symbol)
                if found.on_frame():
                    # Here we share the cellvalue between sibling closures
                    if (found.slotindex in
                            self.parent_walker.fresh_cell_map):
                        shadow_id = self.parent_walker.fresh_cell_map[
                            found.slotindex]
                    else:
                        shadow_id = self.parent_walker.new_fresh_cell(
                                found.slotindex)
                        self.parent_walker.fresh_cell_map[
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

                # come here from if and elif
                self.local_variables[w_symbol] = value_repr
                return value_repr
            else:
                # If we cannot find the symbol, then it must be a global.
                return GlobalValueRepr(w_symbol)

    special_form_set = set('define set! if quote lambda begin'.split(' '))
    def symbol_is_special_form(self, w_symbol):
        assert w_symbol.is_symbol()
        sval = w_symbol.to_string()
        return sval in self.special_form_set

    def visit_special_form(self, w_proc, w_args, tail=False):
        sval = w_proc.to_string()
        if sval == 'define':
            # @see visit_binding
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if len(lst) < 2 or not w_rest.is_null():
                # (define name expr)
                # (define (name . args) body ...)
                raise SchemeSyntaxError, 'define require at least 2 args'

            w_first = lst[0]
            if w_first.is_pair():
                # sugar for lambda
                w_name = w_first.car
                w_formals = w_first.cdr
                body = lst[1:]

                value_repr = self.visit_lambda([w_formals] + body,
                        w_name.to_string())
                self.visit_binding(w_name, value_repr)
                # create binding for define
                return ConstValueRepr(self.new_const_slot(w_unspecified))

            elif w_first.is_symbol():
                w_name = w_first
                w_expr = lst[1]
                value_repr = self.visit(w_expr)
                self.visit_binding(w_name, value_repr)
                # create binding for define
                return ConstValueRepr(self.new_const_slot(w_unspecified))
            else:
                raise SchemeSyntaxError, ('define require the first arg '
                        'to be symbol or pair -- got %s' % w_first.to_string())

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
            # change binding for set!
            self.visit_rebinding(w_name, value_repr)
            return ConstValueRepr(self.new_const_slot(w_unspecified))

        elif sval == 'if':
            # (if pred iftrue [else])
            # this local slot stores the result of the (if) expr
            result_value_repr = FrameValueRepr(self.alloc_frame_slot())
            # two labels, placed just before iftrue and after else.
            label_goto_else = hir.Label()
            label_goto_end = hir.Label()

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
            self.emit(hir.BranchIfFalse(pred_local_val.to_index(),
                                        label_goto_else))

            # if_true insn_list
            iftrue_result_repr = self.visit(w_iftrue, tail)
            self.set_frame_slot(result_value_repr, iftrue_result_repr)
            self.emit(hir.Branch(label_goto_end))  # goto the end of if

            self.emit(label_goto_else) # here comes the else.
            if len(lst) == 2:
                self.set_frame_slot(result_value_repr,
                        ConstValueRepr(self.new_const_slot(w_unspecified)))
            else: # has else
                w_iffalse = lst[2]
                iffalse_result_repr = self.visit(w_iffalse, tail)
                self.set_frame_slot(result_value_repr, iffalse_result_repr)

            self.emit(label_goto_end)  # here we are done.
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
            return self.visit_lambda(lst)

        elif sval == 'begin':
            lst = []
            w_rest = scmlist2py(w_args, lst)
            if not w_rest.is_null():
                raise SchemeSyntaxError, 'begin -- not a well-formed list'
            for i, w_expr in enumerate(lst):
                if i != len(lst) - 1:
                    self.visit(w_expr)
                else:
                    return self.visit(w_expr, tail)
            # when there is no args: return unspecified
            return ConstValueRepr(self.new_const_slot(w_unspecified))

        else:
            raise ValueError, '%s is not a special form' % sval

    def visit_lambda(self, lst, name=None):
        if len(lst) < 2:
            raise SchemeSyntaxError, 'lambda -- missing expression'
        frame_val_repr = FrameValueRepr(self.alloc_frame_slot())
        current_insn_pos = len(self.insn_list)
        self.insn_list.append(None)
        # compile the lambdas in the end
        self.deferred_lambdas.append(DeferredLambdaCompilation(
            self, lst, current_insn_pos, frame_val_repr, name))
        return frame_val_repr

    def visit_binding(self, w_name, value_repr):
        """ If w_name is a local variable, this is the same as set!.
            Else if w_name is a cell variable, then this is an error!
            Otherwise, create a new binding.

            If we are in toplevel, then generate/change a global binding.

            (define w_name value_repr)
        """
        assert w_name.is_symbol()

        if self.is_toplevel():
            if w_name in self.global_variables:
                # change global binding
                val = self.global_variables[w_name]
                self.set_global_value(val, value_repr)
            else:
                # add global binding
                new_val = GlobalValueRepr(w_name)
                self.global_variables[w_name] = new_val
                self.set_global_value(new_val, value_repr)
        else:
            if w_name in self.local_variables:
                # modify local bindings
                old_val = self.local_variables[w_name]
                if old_val.on_frame(): # set frame
                    self.set_frame_slot(old_val, value_repr)
                elif old_val.is_cell(): # set cell
                    raise ValueError, 'shadowing used cell value'
                    #self.set_cell_value(old_val, value_repr)
                else:
                    raise ValueError, 'unreachable'
            else:
                # create new local binding
                new_val = FrameValueRepr(self.alloc_frame_slot())
                self.local_variables[w_name] = new_val
                self.set_frame_slot(new_val, value_repr)

    def visit_rebinding(self, w_name, value_repr):
        """ (set! w_name value_repr)
        """
        assert w_name.is_symbol()

        if w_name in self.local_variables:
            # modify binding
            old_val = self.local_variables[w_name]
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

    def visit_application(self, w_proc, w_args, tail=False):
        lst = []
        w_rest = scmlist2py(w_args, lst)
        if not w_rest.is_null():
            raise SchemeSyntaxError('application -- not a well-formed list')
        # allocate len(lst) + 1 frame slots
        proc_slot = FrameValueRepr(self.alloc_frame_slot())
        arg_slots = [FrameValueRepr(self.alloc_frame_slot())
                for i in xrange(len(lst))]

        # evaluate the proc and the args
        proc_val_repr = self.visit(w_proc)
        self.set_frame_slot(proc_slot, proc_val_repr) # could be no-op

        for i, w_expr in enumerate(lst):
            dest_slot = arg_slots[i]
            arg_val_repr = self.visit(w_expr)
            self.set_frame_slot(dest_slot, arg_val_repr)

        result_value_repr = FrameValueRepr(self.alloc_frame_slot())
        # call and return
        if tail:
            self.emit(hir.TailCall(result_value_repr.to_index(),
                    proc_slot.to_index(), len(lst)))
        else:
            self.emit(hir.Call(result_value_repr.to_index(),
                    proc_slot.to_index(), len(lst)))
        return result_value_repr

    def cast_to_local(self, value_repr):
        if value_repr.on_frame():
            return value_repr
        elif value_repr.is_const():
            res = FrameValueRepr(self.alloc_frame_slot())
            insn = hir.LoadConst(res.to_index(), value_repr.to_index())
            self.emit(insn)
            return res
        elif value_repr.is_cell():
            res = FrameValueRepr(self.alloc_frame_slot())
            insn = hir.LoadCell(res.to_index(), value_repr.to_index())
            self.emit(insn)
            return res
        elif value_repr.is_global():
            res = FrameValueRepr(self.alloc_frame_slot())
            insn = hir.LoadGlobal(res.to_index(),
                    self.new_name_slot(value_repr.w_symbol))
            self.emit(insn)
            return res
        else:
            raise ValueError, 'unreached'

    def set_frame_slot(self, old_repr, new_repr):
        assert old_repr.on_frame()
        if old_repr is new_repr:
            return # moving self to self: ignored
        if new_repr.on_frame():
            self.emit(hir.MoveLocal(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_cell():
            self.emit(hir.LoadCell(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_const():
            self.emit(hir.LoadConst(old_repr.to_index(), new_repr.to_index()))
        elif new_repr.is_global():
            self.emit(hir.LoadGlobal(old_repr.to_index(),
                self.new_name_slot(new_repr.w_symbol)))
        else:
            raise ValueError, 'unreached'

    def set_cell_value(self, cell_repr, new_repr):
        assert cell_repr.is_cell()
        if cell_repr is new_repr:
            return # well...
        self.emit(hir.StoreCell(cell_repr.to_index(),
            self.cast_to_local(new_repr).to_index()))

    def set_global_value(self, global_repr, new_repr):
        assert global_repr.is_global()
        if global_repr is new_repr:
            return # well...
        self.emit(hir.StoreGlobal(self.new_name_slot(global_repr.w_symbol),
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
    def __init__(self, walker, expr_list, insnindex, dest_val_repr, name=None):
        self.walker = walker # the walker
        self.expr_list = expr_list # the lambda formals and body, a pylist
        self.insnindex = insnindex # the insnuction index
        self.dest_val_repr = dest_val_repr # a frame slot
        self.name = name # may be None.

    def resume_compilation(self):
        lambda_walker = SexprWalker(self.walker)
        if self.name:
            lambda_walker.name = self.name # for compile-time reflection.
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
            lambda_walker.local_variables[w_argname] = frame_slot_repr

        # if vararg
        if lambda_walker.varargs_p:
            frame_slot_repr = FrameValueRepr(lambda_walker.alloc_frame_slot())
            lambda_walker.local_variables[w_rest] = frame_slot_repr

        # compile the body and add to the global skeleton table.
        lambda_walker.visit_list_of_expr(lambda_body)
        w_lambda_skeleton = lambda_walker.to_closure_skeleton()
        self.walker.insn_list[self.insnindex] = hir.BuildClosure(
            self.dest_val_repr.to_index(),
            self.walker.new_skel_slot(w_lambda_skeleton))


class WalkerPrinter(object):
    def __init__(self, walker):
        self.walker = walker
        self.indent = 0

    def pprint(self):
        title = 'Globals'
        print title
        print len(title) * '*'
        for key, value in self.walker.global_variables.items():
            print '  %s: %s' % (key, value)
        print

        self.pprint_once('-', self.walker.to_closure_skeleton())
        for i, skel in enumerate(self.walker.skeleton_registry):
            self.pprint_once(i, skel)


    def pprint_once(self, i, skel):
        title = 'Closure[%s] `%s` at 0x%x' % (i, skel.name, id(skel))
        print title
        print '=' * len(title)
        print skel

