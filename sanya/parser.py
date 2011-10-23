import __pypy_path__
from pypy.rlib.parsing.makepackrat import (PackratParser,
        BacktrackException, Status)
from sanya.objectmodel import make_symbol, W_Pair, W_Fixnum, w_nil, make_bool

def parse_string(code_string):
    """ Parse a string and return a sexpression.
    """
    p = MyParser(code_string)
    return p.prog()

# ____________________________________________________________________________
# implementation details.

quote_symbol = make_symbol('quote')

def make_quote(sexpr):
    return W_Pair(quote_symbol, W_Pair(sexpr, w_nil))

class MyParser(PackratParser):
    r"""
    IGNORE:
        ` |\n|\t|;[^\n]*`;

    BOOLEAN:
        c = `#(t|f)`
        IGNORE*
        return {make_bool(c[1] == 't')};

    FIXNUM:
        c = `-?(0|([1-9][0-9]*))`
        IGNORE*
        return {W_Fixnum(int(c))};

    SYMBOL:
        c = `[\+\-\*\^\?a-zA-Z!<=>_~/$%&:][\+\-\*\^\?a-zA-Z0-9!<=>_~/$%&:]*`
        IGNORE*
        return {make_symbol(c)};

    EOF:
        !__any__;

    prog:
        IGNORE*
        s = sexpr*
        EOF
        return {s};

    sexpr:
        SYMBOL
      | FIXNUM
      | BOOLEAN
      | list
      | quoted_sexpr;

    quoted_sexpr:
        `'`
        IGNORE*
        s = sexpr
        return {make_quote(s)};

    list:
        '('
        IGNORE*
        p = pair
        ')'
        IGNORE*
        return {p};

    pair:
        car = sexpr
        '.'
        IGNORE*
        cdr = sexpr
        return {W_Pair(car, cdr)}
      | car = sexpr
        cdr = pair
        return {W_Pair(car, cdr)}
      | return {w_nil};
    """

