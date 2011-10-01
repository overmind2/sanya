# make jit
from pypy.rlib.jit import JitDriver
jitdriver = JitDriver(greens=['pc', 'instr'], reds=['vm', 'frame'])

from sdo import W_CellValue, CellValueNode

class HaltException(Exception):
    pass

class Frame(object):
    """ TODO: make the stack a continuous space so that function calls
        can be cheaper -- no need to copy args between frames.
    """
    def __init__(self, size):
        self.items = [None] * size

    def __repr__(self):
        return '<frame %r>' % self.items

    def resize(self, new_size):
        if len(self.items) < new_size:
            self.items += [None] * (new_size - self.size())

    def size(self):
        return len(self.items)

    def get(self, index):
        assert index >= 0
        return self.items[index]

    def set(self, index, value):
        assert index >= 0
        self.items[index] = value


class Dump(object):
    def __init__(self, vm):
        self.frame = vm.frame
        self.consts = vm.consts
        self.cellvalues = vm.cellvalues
        self.instrs = vm.instrs
        self.pc = vm.pc
        self.return_addr = vm.return_addr
        self.dump = vm.dump

    def restore(self, vm):
        vm.frame = self.frame
        vm.consts = self.consts
        vm.cellvalues = self.cellvalues
        vm.instrs = self.instrs
        vm.pc = self.pc
        vm.return_addr = self.return_addr
        vm.dump = self.dump


class VM(object):

    def __init__(self):
        self.reboot()

    def reboot(self):
        # current local status
        self.frame = None
        self.consts = []
        self.cellvalues = []
        self.globalvars = {}
        self.instrs = []
        self.pc = 0
        self.return_addr = 0
        self.dump = None
        self.exit_value = None # the toplevel return value

        # cellvalues are shared since they die quickly
        self.cellval_head = CellValueNode(None, None, None)
        self.cellval_head.nextnode = self.cellval_head
        self.cellval_head.prevnode = self.cellval_head

    def new_frame(self, size):
        return Frame(size)

    def bootstrap(self, w_skel):
        assert w_skel.is_procedure_skeleton()
        if self.frame is None:
            self.frame = self.new_frame(w_skel.nframeslots)
        else:
            self.frame.resize(w_skel.nframeslots)
        self.pc = 0
        self.consts = w_skel.consts
        self.instrs = w_skel.instrs

    def halt(self):
        raise HaltException

    def save_dump(self):
        self.dump = Dump(self)

    def restore_dump(self, return_value):
        self.escape_cellvalues()
        if self.dump is not None:
            return_addr = self.return_addr
            self.dump.restore(self)
            self.frame.set(return_addr, return_value)
        else: # top-level return
            self.exit_value = return_value
            self.halt()

    def escape_cellvalues(self):
        frame = self.frame
        dummy_node = self.cellval_head
        iter_node = dummy_node.nextnode
        while iter_node is not dummy_node:
            cellval = iter_node.val
            assert isinstance(cellval, W_CellValue)
            if cellval.try_escape(frame):
                iter_node = iter_node.remove() # returns next node
            else:
                iter_node = iter_node.nextnode

    def run(self):
        try:
            while True:
                instr = self.instrs[self.pc]

                jitdriver.jit_merge_point(pc=self.pc,
                        instr=instr, 
                        vm=self,
                        frame=self.frame)

                print 'instr %s, pc=%d, gl=%s, frame=%s' % (instr, self.pc,
                        self.globalvars, self.frame)
                self.pc += 1
                instr.dispatch(self)
        except HaltException:
            return


