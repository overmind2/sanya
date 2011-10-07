
from sanya.compilation import Walker
from sanya.objectmodel import pylist2scm, scmlist2py, make_symbol

def transform_list_of_expr(expr_list):
    walker = CPSWalker()
    outer_cont = None
    prev_cont = None
    for expr in expr_list:
        if not prev_cont:
            outer_cont = prev_cont = walker.visit(expr).make_cont_hole()
        else:
            curr_cont = walker.visit(expr).make_cont_hole()
            prev_cont.set_hole(curr_cont.make_cont_closure())
            prev_cont = curr_cont
    prev_cont.set_hole(cont_s)
    return outer_cont.make_cont_closure()

# ________________________________________________________________________ 
# implementation details

class CPSTransformError(Exception):
    pass

lambda_s = make_symbol('lambda')
cont_s = make_symbol('cont')
display_s = make_symbol('display')

class Counter(object):
    def __init__(self, prefix=""):
        self.prefix = prefix
        self.count = 0

    def get(self):
        res = self.prefix + str(self.count)
        self.count += 1
        return res

arg_counter = Counter('cps-t-')

class Cont(object):
    def make_cont_closure(self):
        raise NotImplementedError

    def make_cont_hole(self):
        w_cont = self.make_cont_closure()
        w_retsym = make_symbol(arg_counter.get())
        return ContHole(w_cont, w_retsym)


class IdenticalCont(Cont):
    def __init__(self, w_expr):
        self.w_expr = w_expr

    def make_cont_closure(self):
        return pylist2scm([lambda_s, pylist2scm([cont_s]),
            pylist2scm([cont_s, self.w_expr])])


class ContHole(IdenticalCont):
    def __init__(self, w_cont, w_retsym):
        w_body = pylist2scm([lambda_s, pylist2scm([w_retsym]), None])
        assert w_body.is_pair()
        t = w_body.cdr
        assert t.is_pair()
        t = t.cdr
        assert t.is_pair()

        self.w_retsym = w_retsym
        self.w_expr = pylist2scm([w_cont, w_body])
        self.w_hole_parent = t

    def set_hole(self, w_hole_expr):
        self.w_hole_parent.car = w_hole_expr


class CPSWalker(Walker):
    """ The general idea is:
        (proc0 (proc1) arg0 arg1) ->
        (proc1 (lambda (result-of-proc1)
                 (proc0 result-of-proc1 arg0 arg1)))

        A more complex example:
        (proc0 (proc1 (proc2)) (proc3)) ->
        (proc2 (lambda (result-of-proc2)
                 (proc1 result-of-proc2 (lambda (result-of-proc1)
                                          (proc3 (lambda (result-of-proc3)
                                                   (proc2 result-of-proc1
                                                          result-of-proc3)))))))

        And then we focus on the inner application, until expressions are
        all in the primitive forms.

        For list of expr, like
        (expr0)
        (expr1)
        (expr2)
        , will be transformed to:
        (expr0 (lambda (_) (expr1 (lambda (_) (expr2 (lambda (_) _))))))
        However it should be noticed that since the recursion is too deep,
        we need to make sure that the compiler could handle this nested
        structure as well.... Anyway, writing a compiler that only accepts
        CPS should be a easy task.
    """
    def __init__(self, parent=None):
        self.parent = parent

    def visit(self, expr, flag=None):
        return expr.accept_cps_transformer(self, flag)

    def make_identical_cont(self, w_expr):
        return IdenticalCont(w_expr)

    def transform_application(self, w_proc, args_list):
        """ (proc arg1 arg2) ->
        (lambda (cont)
          ((lambda (cont) (cont proc))
           (lambda (proc)
             ((lambda (cont) (cont arg1))
              (lambda (arg1)
                ((lambda (cont) (cont arg2))
                 (lambda (arg2)
                   (proc arg1 arg2 cont))))))))
        """
        outer_cont = curr_hole = w_proc.make_cont_hole()
        arg_symbols = [None] * len(args_list)
        for i in xrange(len(args_list)):
            w_arg = args_list[i]
            new_hole = w_arg.make_cont_hole()
            curr_hole.set_hole(new_hole.make_cont_closure())
            curr_hole = new_hole
            arg_symbols[i] = new_hole.w_retsym

        # and the actual application
        actual_application = [outer_cont.w_retsym] + arg_symbols + [cont_s]
        curr_hole.set_hole(pylist2scm(actual_application))

        return outer_cont

