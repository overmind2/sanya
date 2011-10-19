from pypy.rlib.jit import JitDriver, hint
from sanya.closure import W_CellValue, CellValueNode
from sanya.config import DEBUG

# make jit
jitdriver = JitDriver(greens=['pc', 'instr'], reds=['vm', 'frame'])

class HaltException(Exception):
    """ Raise this and VM will stop running.
    """
    pass

class Frame(object):
    """ Could make the stack frame a continuous space so that function calls
        can be cheaper -- no need to copy args between frames.
        However since in most of the situations we are doing tail-calls
        which will not benefit from this...
    """
    def __init__(self, size):
        # Wondering why this hint is not giving any speed improvement...
        self = hint(self, access_directly=True, fresh_virtualizable=True)
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
    def __init__(self):
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

        # contains all closure skeletons. @see compilation.SkeletonWalker
        self.skeleton_registry = []

    def new_frame(self, size):
        return Frame(size)

    def bootstrap(self, w_skel):
        assert w_skel.is_procedure_skeleton()
        if self.frame is None:
            self.frame = self.new_frame(w_skel.frame_size)
        else:
            self.frame.resize(w_skel.frame_size)
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
                instr = self.codes[self.pc]

                jitdriver.jit_merge_point(pc=self.pc,
                        instr=instr,
                        vm=self,
                        frame=self.frame)

                if DEBUG:
                    print self

                self.pc += 1
                instr.dispatch(self)
        except HaltException:
            return

    def __repr__(self):
        """NOT_RPYTHON"""
        return '<vm pc=%02d instr=%s>' % (self.pc, self.codes[self.pc])

