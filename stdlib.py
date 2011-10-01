""" Provides some builtin functions written in sanya-asm.
"""
import os
from sobject import *

def open_lib(vm):
    for name, value in lib.items():
        vm.globalvars[make_symbol(name)] = value

class W_AddProc(W_PyProc):
    _symbol_name_ = '+'

    def py_call(self, py_args):
        res = W_Fixnum(0)
        for w_obj in py_args:
            assert w_obj.is_fixnum()
            res = W_Fixnum(res.ival + w_obj.ival)
        return res

    def to_string(self):
        return '#<primitive-procedure +>'

class W_SubtractProc(W_PyProc):
    _symbol_name_ = '-'

    def py_call(self, py_args):
        assert len(py_args) >= 1

        res = py_args[0]

        for w_obj in py_args[1:]:
            assert w_obj.is_fixnum()
            res = W_Fixnum(res.ival - w_obj.ival)
        return res

    def to_string(self):
        return '#<primitive-procedure ->'

class W_DisplayProc(W_PyProc):
    _symbol_name_ = 'display'

    def py_call(self, py_args):
        assert len(py_args) == 1
        os.write(1, py_args[0].to_string())
        return w_unspecified

    def to_string(self):
        return '#<primitive-procedure display>'

class W_NewlineProc(W_PyProc):
    _symbol_name_ = 'newline'

    def py_call(self, py_args):
        assert len(py_args) == 0
        os.write(1, '\n')
        return w_unspecified

    def to_string(self):
        return '#<primitive-procedure display>'

class W_LessThanProc(W_PyProc):
    _symbol_name_ = '<'

    def py_call(self, py_args):
        assert len(py_args) == 2
        lhs = py_args[0]
        rhs = py_args[1]
        assert lhs.is_fixnum() and rhs.is_fixnum()
        return make_bool(lhs.ival < rhs.ival)

    def to_string(self):
        return '#<primitive-procedure lt>'

class W_Cons(W_PyProc):
    _symbol_name_ = 'cons'

    def py_call(self, py_args):
        assert len(py_args) == 2
        lhs = py_args[0]
        rhs = py_args[1]
        return W_Pair(lhs, rhs)

    def to_string(self):
        return '#<primitive-procedure cons>'

class W_Car(W_PyProc):
    _symbol_name_ = 'car'

    def py_call(self, py_args):
        assert len(py_args) == 1
        w_pair = py_args[0]
        assert w_pair.is_pair()
        return w_pair.car

    def to_string(self):
        return '#<primitive-procedure car>'

class W_Cdr(W_PyProc):
    _symbol_name_ = 'cdr'

    def py_call(self, py_args):
        assert len(py_args) == 1
        w_pair = py_args[0]
        assert w_pair.is_pair()
        return w_pair.cdr

    def to_string(self):
        return '#<primitive-procedure cdr>'

lib = {}
for name in dir():
    obj = globals()[name]
    try:
        if issubclass(obj, W_PyProc) and hasattr(obj, '_symbol_name_'):
            lib[obj._symbol_name_] = obj()
    except TypeError, AttributeError:
        pass

