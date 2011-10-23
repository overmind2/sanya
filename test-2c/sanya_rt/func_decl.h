#include "type_decl.h"

// Macros
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

// Runtime
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

// Object
sanya_t_Object *sanya_r_W_Nil();
sanya_t_Object *sanya_r_W_Unspecified();
sanya_t_Object *sanya_r_W_Boolean(intptr_t bval);
sanya_t_Object *sanya_r_W_Fixnum(intptr_t ival);
sanya_t_Object *sanya_r_W_Symbol(const char *sval);
sanya_t_Object *sanya_r_W_Pair(intptr_t car, intptr_t cdr);
sanya_t_Object *sanya_r_W_Closure(sanya_t_ClosureSkeleton *skeleton,
                                  sanya_t_CellValue **cell_values);

intptr_t sanya_r_W_Object_Type(sanya_t_Object *self);
intptr_t sanya_r_W_Object_Nullp(sanya_t_Object *self);
intptr_t sanya_r_W_Fixnum_Unwrap(sanya_t_Object *self);

// Prelude
void sanya_r_initialize_prelude();
extern intptr_t sanya_g_prelude_display;
extern intptr_t sanya_g_prelude_newline;
extern intptr_t sanya_g_prelude_add;
extern intptr_t sanya_g_prelude_lessthan;
extern intptr_t sanya_g_prelude_num_eq;

// Inlines

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

