from pypy.rlib.jit import purefunction

class W_Root(object):
    """ Base class for all application-level objects.
    """
    def __init__(self):
        pass

    def is_fixnum(self):
        """ @see W_Fixnum
        """
        return False

    def is_symbol(self):
        """ @see W_Symbol
        """
        return False

    def is_pair(self):
        """ @see W_Pair
        """
        return False

    def is_null(self):
        """ @see W_Nil
        """
        return False

    def is_unspecified(self):
        """ @see W_Unspecified
        """
        return False

    def is_boolean(self):
        """ @see W_Boolean
        """
        return False

    def is_procedure(self):
        """ @see sanya.closure.W_Closure
        """
        return False

    def is_procedure_skeleton(self):
        """ @see sanya.closure.W_ClosureSkeleton
        """
        return False

    def is_cellvalue(self):
        """ @see sanya.closure.W_CellValue
        """
        return False

    def is_pyproc(self):
        """ @see W_PyProc
        """
        return False

    def to_string(self):
        return '#<root-object>'

    def to_bool(self):
        return True

    def accept_compiler_walker(self, walker, flag):
        """ @see sanya.compilation.ClosureWalker
        """
        raise NotImplementedError

    def accept_cps_transformer(self, walker, flag):
        """ @see sanya.transform.CPSWalker
        """
        raise NotImplementedError

    def __repr__(self):
        """NOT_RPYTHON"""
        return self.to_string()

class W_Symbol(W_Root):
    """ Symbol has a static symbol table which maps a string to its
        corresponding w_symbol instance. In this way, global variable
        lookups in the vm can be faster.

        Thus, you should not call W_Symbol() directly. Instead, you
        should use make_symbol(str) to get a w_symbol with the given str.
    """
    symtab = {}
    _immutable_fields_ = ['sval']

    def __init__(self, sval):
        self.sval = sval

    def is_symbol(self):
        return True

    @purefunction
    def get_symbol(self):
        return self.sval

    @purefunction
    def to_string(self):
        return self.sval

    def accept_compiler_walker(self, walker, flag):
        return walker.local_lookup(self)

    def accept_cps_transformer(self, walker, flag):
        return walker.make_identical_cont(self)


def make_symbol(sval):
    """ Use this to get a w_symbol instance.
    """
    got = W_Symbol.symtab.get(sval, None)
    if got is None:
        got = W_Symbol(sval)
        W_Symbol.symtab[sval] = got
    return got

class W_Fixnum(W_Root):
    """ Generally a machine word.
    """
    _immutable_fields_ = ['ival']

    def __init__(self, ival):
        self.ival = ival

    def is_fixnum(self):
        return True

    @purefunction
    def get_fixnum(self):
        return self.ival

    @purefunction
    def to_string(self):
        return str(self.ival)

    def accept_compiler_walker(self, walker, flag):
        return walker.visit_fixnum_const(self)

    def accept_cps_transformer(self, walker, flag):
        return walker.make_identical_cont(self)

class W_Pair(W_Root):
    """ Mutable data structure. It's particular important in scheme
        implementations that directly interprets the syntax tree.
        However since we are compiling to bytecode, pairs become
        not so important in the runtime.
    """
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def is_pair(self):
        return True

    def to_string(self):
        buf = ['(', self.car.to_string()]
        w_pair = self.cdr

        while isinstance(w_pair, W_Pair):
            buf.append(' ')
            buf.append(w_pair.car.to_string())
            w_pair = w_pair.cdr

        if not w_pair.is_null():
            buf.append(' . ')
            buf.append(w_pair.to_string())

        buf.append(')')
        return ''.join(buf)

    def accept_compiler_walker(self, walker, flag):
        """ Most of the works are done in the compiler so
            here is just a stub.
        """
        w_proc = self.car
        w_args = self.cdr

        if w_proc.is_symbol():
            # This may be a special form (like define, set!, if etc...)
            if walker.symbol_is_special_form(w_proc):
                return walker.visit_special_form(w_proc, w_args, flag)

        # if its' not a special form, then simply
        # apply the procedure against the arguments
        return walker.visit_application(w_proc, w_args, flag)

    def accept_cps_transformer(self, walker, flag):
        lis = []
        w_rest = scmlist2py(self, lis)
        assert w_rest.is_null()

        transformed_lis = [None] * len(lis)
        for i in xrange(len(lis)): # RPython plz give me enumerate...
            w_item = lis[i]
            transformed_lis[i] = walker.visit(w_item)

        w_proc = transformed_lis[0]
        args_list = transformed_lis[1:]
        return walker.transform_application(w_proc, args_list)

class W_Nil(W_Root):
    """ Use w_nil to access this singleton instance.
    """
    def to_string(self):
        return '()'

    def to_bool(self):
        return False

    def is_null(self):
        return True

    def accept_compiler_walker(self, walker, flag):
        raise TypeError, 'w_nil visited'

w_nil = W_Nil()

def pylist2scm(lis, w_tail=w_nil):
    """ Convert a (R)Python list to a scheme cons list.
        You could specify w_tail to be things other than w_nil.
    """
    # Since RPy dont have reversed(list)...
    for i in xrange(len(lis) - 1, -1, -1):
        w_item = lis[i]
        w_tail = W_Pair(w_item, w_tail)
    return w_tail

def scmlist2py(w_list, output):
    """ Convert a scheme cons list to a (R)Python list.
        The return value is the rest of the list that could
        not be converted. If w_list is a proper list, the return value
        will be w_nil.
    """
    while w_list.is_pair():
        output.append(w_list.car)
        w_list = w_list.cdr
    return w_list

class W_Boolean(W_Root):
    """ Singleton class with two instances: w_true and w_false.
    """
    def to_bool(self):
        return self is w_true

    def is_boolean(self):
        return True
    
    def to_string(self):
        if self.to_bool():
            return '#t'
        else:
            return '#f'

    def accept_compiler_walker(self, walker, flag):
        return walker.visit_boolean_const(self)

w_true = W_Boolean()
w_false = W_Boolean()

def make_bool(bval):
    """ Use this to wrap a interpreter-level boolean to an
        application-level boolean object.
    """
    if bval:
        return w_true
    else:
        return w_false

class W_Unspecified(W_Root):
    """ As its name suggests. Access this through singleton instance:
        w_unspecified
    """
    def to_string(self):
        return '#<unspecified>'

    def is_unspecified(self):
        return True

w_unspecified = W_Unspecified()


class W_PyProc(W_Root):
    """ A Python foreign function. Subclass from this to create
        custom procedures.
    """
    def is_pyproc(self):
        return True

    def py_call(self, py_args):
        raise NotImplementedError

    def to_string(self):
        return '#<py-procedure>'

