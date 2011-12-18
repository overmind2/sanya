from pypy.rlib.jit import hint, unroll_safe
from sanya.closure import W_CellValue, CellValueNode
from sanya.config import DEBUG
from sanya.jit import jitdriver


class HaltException(Exception):
    """ Raise this and VM will stop running.
    """
    pass

class Dump(object):
    _immutable_ = True
    def __init__(self, vm):
        self.frame = vm.frame
        self.consts = vm.consts
        self.cellvalues = vm.cellvalues
        self.fresh_cells = vm.fresh_cells
        self.codes = vm.codes
        self.pc = vm.pc
        self.return_addr = vm.return_addr
        self.dump = vm.dump

    def restore(self, vm):
        vm.frame = self.frame
        vm.consts = self.consts
        vm.cellvalues = self.cellvalues
        vm.fresh_cells = self.fresh_cells
        vm.codes = self.codes
        vm.pc = self.pc
        vm.return_addr = self.return_addr
        vm.dump = self.dump


class VM(object):
    _immutable_fields_ = ['globalvars']
    _virtualizable2_ = ['frame', 'consts', 'cellvalues', 'fresh_cells',
                        'codes', 'pc', 'return_addr', 'dump',
                        'cellval_head', 'skeleton_registry']
    def __init__(self):
        self = hint(self, promote=True, access_directly=True,
                    fresh_virtualizable=True)
        self.reboot()

    def reboot(self):
        # current local status
        self.frame = None
        self.consts = []
        self.cellvalues = []
        self.fresh_cells = []
        self.globalvars = {}
        self.codes = []
        self.pc = 0
        self.return_addr = 0
        self.dump = None
        self.exit_value = None # the toplevel return value

        # cellvalues are stored in a doubly-linkedlist since they birth and die
        # quickly and d-list allow O(1) insertion/deletion.
        # ``hao ba zhe shi chao xi Lua-5.1 de....``
        self.cellval_head = CellValueNode(None, None, None)
        self.cellval_head.nextnode = self.cellval_head
        self.cellval_head.prevnode = self.cellval_head
        self.skeleton_registry = []

    def new_frame(self, size):
        return [None] * size

    def bootstrap(self, w_skel):
        assert w_skel.is_procedure_skeleton()
        newsize = w_skel.frame_size
        if self.frame is None:
            self.frame = self.new_frame(newsize)
        else:
            if len(self.frame) < newsize:
                self.frame.extend([None] * (newsize - len(self.frame)))
        self.pc = 0
        self.consts = w_skel.consts
        self.codes = w_skel.codes

        # since toplevel variables are all globals, we dont have to bother
        # with cellvalues-related things

        # load the skeleton table and clean up
        self.skeleton_registry = w_skel.skeleton_registry
        w_skel.skeleton_registry = None

    def halt(self):
        raise HaltException

    def save_dump(self):
        self.dump = Dump(self)

    def restore_dump(self, return_value):
        self.escape_cellvalues()
        if self.dump is not None:
            return_addr = self.return_addr
            self.dump.restore(self)
            self.frame[return_addr] = return_value
        else: # top-level return
            self.exit_value = return_value
            self.halt()

    @unroll_safe
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

    @unroll_safe
    def run(self):
        self = hint(self, promote=True, access_directly=True)
        try:
            while True:
                jitdriver.jit_merge_point(pc=self.pc, codes=self.codes,
                                          vm=self)
                instr = self.codes[self.pc]
                if DEBUG:
                    print self
                self.pc += 1
                instr.dispatch(self)
        except HaltException:
            return

    def __repr__(self):
        """NOT_RPYTHON"""
        return '<vm pc=%02d instr=%s>' % (self.pc, self.codes[self.pc])

