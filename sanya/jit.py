from pypy.rlib.jit import JitDriver

def get_location(pc, codes):
    return 'pc=%d' % pc

# make jit
jitdriver = JitDriver(greens=['pc', 'codes'],
                      reds=['vm'],
                      virtualizables=['vm'],
                      get_printable_location=get_location)

