#ifndef SANYA_RUNTIME_H
#define SANYA_RUNTIME_H
#include <inttypes.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include "sanya_object.h"

// naming conventions: sanya_t -- types
//                     sanya_g -- globals
//                     sanya_p -- prelude
//                     sanya_r -- runtime-related
//                     v_<number> -- local variables
//                     ls_<name> -- local special variables

// Forward from sanya_obj.h
typedef struct sanya_t_Object_ sanya_t_Object;

typedef struct sanya_t_ClosureSkeleton_ sanya_t_ClosureSkeleton;
typedef struct sanya_t_CellValue_ sanya_t_CellValue;

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

#define SANYA_R_CALLCLOSURE_0(retval, closure) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 0); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr0)funcptr)(call); \
    } while (0)

#define SANYA_R_CALLCLOSURE_1(retval, closure, arg1) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 1); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr1)funcptr)(call, (intptr_t)arg1); \
    } while (0)

#define SANYA_R_CALLCLOSURE_2(retval, closure, arg1, arg2) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 2); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr2)funcptr)(call, \
                (intptr_t)arg1, (intptr_t)arg2); \
    } while (0)

#define SANYA_R_CALLCLOSURE_3(retval, closure, arg1, arg2, arg3) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 3); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr3)funcptr)(call, \
                (intptr_t)arg1, (intptr_t)arg2, (intptr_t)arg3); \
    } while (0)

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

inline void sanya_r_check_nb_args(sanya_t_Object *clos, intptr_t nb_args);
sanya_t_CellValue *sanya_r_build_cell_value(intptr_t *ref);
void sanya_r_escape_cell_values(sanya_t_CellValue **cell_list,
                                intptr_t length);
sanya_t_Object *sanya_r_build_closure(sanya_t_ClosureSkeleton *skel,
                                      sanya_t_CellValue **cell_values,
                                      sanya_t_CellValue **fresh_cells);
intptr_t sanya_r_to_boolean(sanya_t_Object *self);

void sanya_r_halt();
void sanya_r_bootstrap();  // defined in main.c instead.

inline void
sanya_r_check_nb_args(sanya_t_Object *clos, intptr_t nb_args)
{
    sanya_t_ClosureSkeleton *skel = clos->as_closure.skeleton;
    if (skel->nb_args != nb_args) {
        fprintf(stderr, "ERROR: closure %s called with wrong number"
                " of argument.\n", skel->name);
        fprintf(stderr, " -- requires %ld arguments, got %ld.\n",
                skel->nb_args, nb_args);
        exit(1);
    }
}


#endif /* SANYA_RUNTIME_H */

