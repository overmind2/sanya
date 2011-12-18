
from sanya.instruction_set import make_instr
from sanya.closure import W_Skeleton
from sanya.objectmodel import (make_symbol, W_Fixnum,
                               W_Pair, make_bool, w_unspecified, w_nil)

CHUNK_HEADER = '-' + 'sanya' + '--'

def dump(root_skel, stream):
    stream.write(CHUNK_HEADER)
    dump_skel(root_skel, stream)
    dump_number(len(root_skel.skeleton_registry), stream)
    for skel in root_skel.skeleton_registry:
        dump_skel(skel, stream)

def load(stream):
    assert stream.read(len(CHUNK_HEADER)) == CHUNK_HEADER, 'Wrong chunk header'
    root_skel = load_skel(stream)
    nskeletons = load_number(stream)
    skeleton_registry = [None] * nskeletons
    for i in xrange(nskeletons):
        skeleton_registry[i] = load_skel(stream)
    root_skel.skeleton_registry = skeleton_registry
    return root_skel

# ___________________________________________________________________________
# implementation details

def dump_skel(skel, stream):
    dump_instr_list(skel.codes, stream)
    dump_const_list(skel.consts, stream)
    dump_number(skel.frame_size, stream)

    dump_number(len(skel.cell_recipt), stream)
    for cellvalue_repr in skel.cell_recipt:
        dump_number(cellvalue_repr, stream)

    dump_number(len(skel.fresh_cells), stream)
    for shadow_id in skel.fresh_cells:
        dump_number(shadow_id, stream)

    dump_number(skel.nb_args, stream)
    if skel.varargs_p:
        stream.write('\x01')
    else:
        stream.write('\x00')
    stream.write('\n')

def dump_instr_list(instr_list, stream):
    dump_number(len(instr_list), stream)
    for instr in instr_list:
        dump_instr(instr, stream)

def dump_instr(instr, stream):
    dump_number(instr.dump_u32(), stream)

def dump_const_list(const_list, stream):
    dump_number(len(const_list), stream)
    for const in const_list:
        dump_const(const, stream)

K_SYMBOL = 'S'
K_FIXNUM = 'I'
K_PAIR = 'P'
K_NULL = 'u'
K_TRUE = 't'
K_FALSE = 'f'
K_UNSPEC = '?'
def dump_const(const, stream):
    if const.is_symbol():
        stream.write(K_SYMBOL)
        dump_string(const.get_symbol(), stream)

    elif const.is_fixnum():
        stream.write(K_FIXNUM)
        dump_number(const.get_fixnum(), stream)

    elif const.is_pair():
        # XXX: recursive call -- stack overflow?
        assert isinstance(const, W_Pair)
        stream.write(K_PAIR)
        dump_const(const.car, stream)
        dump_const(const.cdr, stream)

    elif const.is_null():
        stream.write(K_NULL)

    elif const.is_boolean():
        if const.to_bool():
            stream.write(K_TRUE)
        else:
            stream.write(K_FALSE)

    elif const.is_unspecified():
        stream.write(K_UNSPEC)

    else:
        raise TypeError('unknown constant -- %s' % const.to_string())

def dump_number(ival, stream):
    assert abs(ival) < ((1 << 31) - 1), 'Number too large to dump'
    c4 = (ival >> 24) & 0xff
    c3 = (ival >> 16) & 0xff
    c2 = (ival >> 8) & 0xff
    c1 = ival & 0xff
    # using little endian here
    stream.write(chr(c1))
    stream.write(chr(c2))
    stream.write(chr(c3))
    stream.write(chr(c4))

def dump_string(sval, stream):
    dump_number(len(sval), stream)
    stream.write(sval)

def load_skel(stream):
    codes = load_instr_list(stream)
    consts = load_const_list(stream)
    frame_size = load_number(stream)

    ncellvalues = load_number(stream)
    cellvalues = [-1] * ncellvalues
    for i in xrange(ncellvalues):
        cellvalues[i] = load_number(stream)
    
    nfresh_cells = load_number(stream)
    fresh_cells = [-1] * nfresh_cells
    for i in xrange(nfresh_cells):
        fresh_cells[i] = load_number(stream)

    nb_args = load_number(stream)
    nxt_chr = stream.read(1)
    if nxt_chr == '\x01':
        varargs_p = True
    elif nxt_chr == '\x00':
        varargs_p = False
    else:
        raise ValueError('hasvararg -- not 0/1')

    stream.read(1) # the newline
    return W_Skeleton(codes, consts, frame_size,
            cellvalues, fresh_cells, nb_args, varargs_p, None)

def load_instr_list(stream):
    ncodes = load_number(stream)
    codes = [None] * ncodes
    for i in xrange(ncodes):
        codes[i] = load_instr(stream)
    return codes

def load_instr(stream):
    u32 = load_number(stream)
    instr = make_instr(u32)
    return instr

def load_const_list(stream):
    nconsts = load_number(stream)
    consts = [None] * nconsts
    for i in xrange(nconsts):
        consts[i] = load_const(stream)
    return consts

def load_const(stream):
    tag = stream.read(1)
    if tag == K_SYMBOL:
        return make_symbol(load_string(stream))

    elif tag == K_FIXNUM:
        return W_Fixnum(load_number(stream))

    elif tag == K_PAIR:
        # XXX: recursive call -- stack overflow?
        car = load_const(stream)
        cdr = load_const(stream)
        return W_Pair(car, cdr)

    elif tag == K_NULL:
        return w_nil

    elif tag == K_TRUE:
        return make_bool(True)

    elif tag == K_FALSE:
        return make_bool(False)

    elif tag == K_UNSPEC:
        return w_unspecified

    else:
        raise ValueError('unknown tag -- %s' % tag)

def load_number(stream):
    """ Ugly since RPython want the string to be of length 1...
    """
    c1 = stream.read(1)[0]
    v1 = ord(c1)

    c2 = stream.read(1)[0]
    v2 = ord(c2)

    c3 = stream.read(1)[0]
    v3 = ord(c3)

    c4 = stream.read(1)[0]
    v4 = ord(c4)
    return (v4 << 24) | (v3 << 16) | (v2 << 8) | v1

def load_string(stream):
    slen = load_number(stream)
    buf = []
    while slen > 0:
        s = stream.read(slen)
        slen -= len(s)
        buf.append(s)
    return ''.join(buf)

