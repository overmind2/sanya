#include "forward_decl.h"

typedef intptr_t (*sanya_t_ClosurePtr0) (sanya_t_Object *ls_closure);
typedef intptr_t (*sanya_t_ClosurePtr1) (sanya_t_Object *ls_closure,
                                         intptr_t ls_arg1);
typedef intptr_t (*sanya_t_ClosurePtr2) (sanya_t_Object *ls_closure,
                                         intptr_t ls_arg1,
                                         intptr_t ls_arg2);
typedef intptr_t (*sanya_t_ClosurePtr3) (sanya_t_Object *ls_closure,
                                         intptr_t ls_arg1,
                                         intptr_t ls_arg2,
                                         intptr_t ls_arg3);
typedef intptr_t (*sanya_t_ClosurePtr4) (sanya_t_Object *ls_closure,
                                         intptr_t ls_arg1,
                                         intptr_t ls_arg2,
                                         intptr_t ls_arg3,
                                         intptr_t ls_arg4);
typedef intptr_t (*sanya_t_ClosurePtrVar) (sanya_t_Object *ls_closure,
                                           intptr_t ls_argc,
                                           intptr_t *ls_argv);

struct sanya_t_Object_ {
    intptr_t type;
    union {
        const char *as_symbol;
        struct {
            sanya_t_Object *car;
            sanya_t_Object *cdr;
        } as_pair;
        struct {
            sanya_t_ClosureSkeleton *skeleton;
            union {
                sanya_t_CellValue **cell_values;
                void *aux;
            };
        } as_closure;
    };
};

struct sanya_t_ClosureSkeleton_ {
    intptr_t *consts;
    intptr_t *cell_recipt;
    intptr_t nb_cells;
    void *closure_ptr;  // cast to some func before calling.
    intptr_t nb_args;
    intptr_t varargs_p;
    const char *name;
};

struct sanya_t_CellValue_ {
    intptr_t *ref;
    union {
        intptr_t *frame_mark;
        intptr_t escaped_value;
    };
};

struct sanya_t_TrampolineBuf_ {
    intptr_t is_done;
    intptr_t closure;
    intptr_t argc;
    intptr_t argv[16];
};

