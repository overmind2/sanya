""" How closures are build and called?
"""
from pypy.rlib.jit import purefunction
from sanya.objectmodel import W_Root

# XXX: consider unify this with vm.Dump and vm.Frame?
class W_Skeleton(W_Root):
    """ Closure skeleton, just like function prototype in Lua,
        contains every runtime information about a closure,
        expect the actual call value list.

        When build a closure from its skeleton, the cell_recipt
        list is iterated and its int values are unpacked. If the
        LSB is 0, then this cell value is copied from vm's current
        cell value list. Otherwise, this cell value is build from
        vm's current frame.

        __slots__:
            codes ; list of instructions
            consts ; list of constants
            frame_size ; number of frame slots required for this closure.
            cell_recipe ; list of ints, used when building closure instance.
                        ; data is packed as (index << 1) | fresh_p
                        ; if fresh_p is true, the cell comes from the current
                        ; running closure's {fresh_cells}.
                        ; Otherwise, the cell comes from the current running
                        ; closure's {cellvalues}.
            fresh_cells ; used to build fresh cell values from frame
                        ; when entering a new closure
            nb_args ; number of args required
            varargs_p ; whether the closure accepts varargs or not.
            skeleton_registry ; list of skeletons, @see Lua's KPROTO
    """
    _immutable_fields_ = ['codes', 'consts', 'frame_size', 'cell_recipt',
            'fresh_cells', 'nb_args', 'varargs_p']

    def __init__(self, codes, consts, frame_size, cell_recipt,
            fresh_cells, nb_args, varargs_p, skeleton_registry):
        # Those are all immutables except for skeleton_registry, which
        # will be set to None when bootstraping vm.
        self.codes = codes
        self.consts = consts
        self.frame_size = frame_size
        self.cell_recipt = cell_recipt
        self.fresh_cells = fresh_cells
        self.nb_args = nb_args
        self.varargs_p = varargs_p
        self.skeleton_registry = skeleton_registry

    def is_procedure_skeleton(self):
        return True

    def build_closure(self, vm):
        cellvalues = [None] * len(self.cell_recipt)
        for i, packed_data in enumerate(self.cell_recipt):
            # meaning of {index} depends on {fresh_p}.
            # @see docstring for this class.
            (index, fresh_p) = ((packed_data >> 1), (packed_data & 0x1))
            if fresh_p: # is freshly moved from the vm's temporary cell table.
                w_cell = vm.fresh_cells[index]
            else: # is a borrowed cell value. move from vm.cellvalues
                w_cell = vm.cellvalues[index]
            cellvalues[i] = w_cell
        # instanitiate a new closure.
        return W_Closure(self, cellvalues)

    def to_string(self):
        return '#<procedure-skeleton>'

    def to_dict(self):
        """NOT_RPYTHON"""
        res = self.__dict__.copy()
        res['consts'] = list(res['consts'])
        res['name'] = '<ClosureSkeleton object at 0x%x>' % id(self)
        for k, v in enumerate(res['consts']):
            if v.is_procedure_skeleton():
                res['consts'][k] = v.to_dict()
        return res

    def __repr__(self):
        from cStringIO import StringIO
        from pprint import pprint
        buf = StringIO()
        pprint(self.to_dict(), buf)
        return buf.getvalue()

class W_Closure(W_Root):
    """ Closure instance, built during runtime.
        @see W_Skeleton
        @see instruction_set.BuildClosure
    """
    _immutable_fields_ = ['skeleton', 'cellvalues'] # why not?

    def __init__(self, skeleton, cellvalues):
        self.skeleton = skeleton
        self.cellvalues = cellvalues

    @purefunction
    def get_skeleton(self):
        return self.skeleton

    @purefunction
    def get_cellvalues(self):
        return self.cellvalues

    def is_procedure(self):
        return True

    def to_string(self):
        return '#<procedure>'

class W_CellValue(W_Root):
    """ Cellvalues are used to implement nested scope / closures.

        A cellvalue can be in two status: not-escaped or escaped.
        When it's not escaped, it contains a frame and an index pointing
        to a frame slot. When it's escaped, the value on the frame slot
        will be 'grabbed' out and stored inside this cell.

        Cellvalues only exist in closure instances that is built
        during runtime, since cellvalue's constructor require an
        existing frame as the first parameter.
    """
    def __init__(self, baseframe, slotindex):
        self.baseframe = baseframe
        self.slotindex = slotindex
        self.escaped = False
        self.escaped_value = None

    def to_string(self):
        return '#<cellvalue>'

    def __repr__(self):
        buf = ['#<']
        if self.escaped:
            buf.append('escaped ')
        buf.append('cellvalue value=')
        buf.append(self.getvalue().to_string())
        if not self.escaped:
            buf.append(' frame=%s' % str(self.baseframe))
            buf.append(' slotindex=%s' % str(self.slotindex))
        buf.append('>')
        return ''.join(buf)

    def is_cellvalue(self):
        return True

    def getvalue(self):
        if self.escaped:
            return self.escaped_value
        else:
            return self.baseframe.get(self.slotindex)

    def setvalue(self, value):
        if self.escaped:
            self.escaped_value = value
        else:
            self.baseframe.set(self.slotindex, value)

    def try_escape(self, frame):
        if self.baseframe is frame:
            self.escaped = True
            self.escaped_value = self.baseframe.get(self.slotindex)
            self.baseframe = None
            self.slotindex = -1
            return True
        else:
            return False

class CellValueNode(object):
    """ Container class to store cellvalues in doubly-linked list.
    """
    _immutable_fields_ = ['val']
    def __init__(self, val, prevnode, nextnode):
        self.val = val
        self.prevnode = prevnode
        self.nextnode = nextnode

    def remove(self):
        """ Return this node and return the next node.
        """
        res = self.nextnode
        self.prevnode.nextnode = self.nextnode
        self.nextnode.prevnode = self.prevnode
        self.nextnode = None
        self.prevnode = None
        return res

    def append(self, val):
        """ Hmmm... The name of this function should actually be ``prepend``.
        """
        new_node = CellValueNode(val, self, self.nextnode)
        self.nextnode.prevnode = new_node
        self.nextnode = new_node

