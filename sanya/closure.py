""" Calling and execution related things.
"""
from sanya.objectmodel import W_Root

class W_ClosureSkeleton(W_Root):
    """ The skeleton may request the outer closure to share its cellvalues.
        Hmm... How to do it? Or shall I create a global cellvalue table when
        compiling?
    """
    _immutable_fields_ = ['instrs', 'consts', 'nframeslots', 'raw_cellvalues',
            'shadow_cellvalues', 'nargs', 'hasvarargs']

    def __init__(self, instrs, consts, nframeslots, raw_cellvalues,
            shadow_cellvalues, nargs, hasvarargs, closkel_table):
        self.instrs = instrs
        self.consts = consts
        self.nframeslots = nframeslots

        # rlist of ints, if &0x1 then it's a cell from vm.frame
        # else it's a cell from vm.cellvalue
        # @see build_closure
        self.raw_cellvalues = raw_cellvalues

        # contains frame slot indexes that need to be made into cellvalues.
        # @see build_closure
        self.shadow_cellvalues = shadow_cellvalues

        self.nargs = nargs # Actually it's number of positional args...
        self.hasvarargs = hasvarargs
        self.closkel_table = closkel_table

    def is_procedure_skeleton(self):
        return True

    def build_closure(self, vm):
        cellvalues = [None] * len(self.raw_cellvalues)

        for i, pindex in enumerate(self.raw_cellvalues):
            real_index = pindex >> 1
            is_from_frame = pindex & 0x1
            if is_from_frame: # is from the current shadow cellvalue frame.
                w_cellval = vm.shadow_cellvalues[real_index]
            else: # is borrowed cell value
                w_cellval = vm.cellvalues[real_index]
            cellvalues[i] = w_cellval
        # instanitiate a newly bound closure.
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
    #_immutable_fields_ = ['skeleton', 'cellvalues'] # why not?

    def __init__(self, skeleton, cellvalues):
        self.skeleton = skeleton
        self.cellvalues = cellvalues

    def is_procedure(self):
        return True

    def to_string(self):
        return '#<procedure>'

class W_CellValue(W_Root):
    """ Multiple closures must share the same cellvalue. That is,
        some how they have the same reference/pointer.
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
    _immutable_fields_ = ['val']
    def __init__(self, val, prevnode, nextnode):
        self.val = val
        self.prevnode = prevnode
        self.nextnode = nextnode

    def remove(self):
        res = self.nextnode
        self.prevnode.nextnode = self.nextnode
        self.nextnode.prevnode = self.prevnode
        self.nextnode = None
        self.prevnode = None
        return res

    def append(self, val):
        new_node = CellValueNode(val, self, self.nextnode)
        self.nextnode.prevnode = new_node
        self.nextnode = new_node

