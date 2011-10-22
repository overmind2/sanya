#ifndef SANYA_RUNTIME_H
#define SANYA_RUNTIME_H
#include <inttypes.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

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

typedef void (*sanya_t_ClosurePtr) (intptr_t *ls_retval,
                                    sanya_t_Object *ls_closure,
                                    intptr_t ls_nb_args, ...);

struct sanya_t_ClosureSkeleton_ {
    intptr_t *consts;
    intptr_t *cell_recipt;
    intptr_t nb_cells;
    sanya_t_ClosurePtr closure_ptr;
    intptr_t nb_args;
    intptr_t vararg_p;
    char *name;
};

struct sanya_t_CellValue_ {
    intptr_t *ref;
    union {
        intptr_t *frame_mark;
        intptr_t escaped_value;
    };
    sanya_t_CellValue *next;
    sanya_t_CellValue *prev;
};

void sanya_r_check_nb_args(sanya_t_Object *clos, intptr_t nb_args);
sanya_t_CellValue *sanya_r_build_cell_value(intptr_t *ref,
                                            intptr_t *frame_mark);
void sanya_r_escape_cell_values(intptr_t *frame_mark);
sanya_t_Object *sanya_r_build_closure(sanya_t_ClosureSkeleton *skel,
                                      sanya_t_CellValue **cell_values,
                                      sanya_t_CellValue **fresh_cells);

void sanya_r_halt();
void sanya_r_bootstrap();  // defined in main.c instead.

#endif /* SANYA_RUNTIME_H */

