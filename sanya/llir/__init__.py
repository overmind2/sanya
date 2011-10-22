""" LLIR -- Low-level intermediate representation.
    Intended to be compiled to C, has two passes:
        1. Just like the VM compilation but has first-class label rather than
           using directly calcuated offset jump.
        2. Further reduce the complexity by transforming the following
           pseudo-instructions: TailCall, LoadGlobal, StoreGlobal
"""

