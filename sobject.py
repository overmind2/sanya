
class W_Root(object):
    """ Base class for all application-level objects.
    """
    def __init__(self):
        pass

    def is_fixnum(self):
        return False

    def is_symbol(self):
        return False

    def is_pair(self):
        return False

    def is_null(self):
        return False

    def is_boolean(self):
        return False

    def is_procedure(self):
        return False

    def is_procedure_skeleton(self):
        return False

    def is_cellvalue(self):
        return False

    def is_pyproc(self):
        return False

    def to_string(self):
        return '#<wrap>'

    def to_bool(self):
        return True

    def accept_compiler_walker(self, walker, flag):
        raise NotImplementedError

    def __repr__(self):
        """NOT_RPYTHON"""
        return self.to_string()

class W_Symbol(W_Root):
    symtab = {}
    _immutable_fields_ = ['sval']

    def __init__(self, sval):
        self.sval = sval

    def is_symbol(self):
        return True

    def to_string(self):
        return self.sval

    def accept_compiler_walker(self, walker, flag):
        return walker.local_lookup(self)

def make_symbol(sval):
    got = W_Symbol.symtab.get(sval, None)
    if got is None:
        got = W_Symbol(sval)
        W_Symbol.symtab[sval] = got
    return got

class W_Fixnum(W_Root):
    #_immutable_fields_ = ['ival']

    def __init__(self, ival):
        self.ival = ival

    def is_fixnum(self):
        return True

    def to_string(self):
        return str(self.ival)

    def accept_compiler_walker(self, walker, flag):
        return walker.visit_fixnum_const(self)

class W_Pair(W_Root):
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
        """ This is huge....
        """
        w_proc = self.car
        w_args = self.cdr

        if w_proc.is_symbol():
            # defer compilation of lambda by putting a placeholder in the
            # local_consts and append this lambda expr to the deferred_lambda
            # list. will visit this again just before the end of the
            # walker.
            if walker.symbol_is_special_form(w_proc):
                return walker.visit_special_form(w_proc, w_args, flag)

        # if not special form, them apply the proc against the args
        return walker.visit_application(w_proc, w_args, flag)


class W_Nil(W_Root):
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
    # RPy dont have reversed...
    for i in xrange(len(lis) - 1, -1, -1):
        w_item = lis[i]
        w_tail = W_Pair(w_item, w_tail)
    return w_tail

def scmlist2py(w_list, output):
    while w_list.is_pair():
        output.append(w_list.car)
        w_list = w_list.cdr
    return w_list

class W_Boolean(W_Root):
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
    if bval:
        return w_true
    else:
        return w_false

class W_Unspecified(W_Root):
    def to_string(self):
        return '#<unspecified>'

w_unspecified = W_Unspecified()


class W_PyProc(W_Root):
    def is_pyproc(self):
        return True

    def py_call(self, py_args):
        raise NotImplementedError

    def to_string(self):
        return '#<py-procedure>'

