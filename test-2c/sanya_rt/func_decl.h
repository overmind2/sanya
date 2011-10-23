#include "type_decl.h"

// Globals
extern sanya_t_TrampolineBuf sanya_g_trampoline_buf;

// Macros

#define SANYA_R_RETURN_VALUE(retval) \
    sanya_g_trampoline_buf.is_done = 1; \
    return retval


#define SANYA_R_CHECK_TRAMPOLINE(retval) \
    while (!sanya_g_trampoline_buf.is_done) { \
        sanya_g_trampoline_buf.is_done = 1; \
        sanya_t_Object *call = (sanya_t_Object *)sanya_g_trampoline_buf.closure; \
        sanya_r_check_nb_args(call, sanya_g_trampoline_buf.argc); \
        switch (sanya_g_trampoline_buf.argc) { \
            case 0: { \
                void *funcptr = call->as_closure.skeleton->closure_ptr; \
                retval = ((sanya_t_ClosurePtr0)funcptr)(call); \
                break; \
            } \
            case 1: { \
                void *funcptr = call->as_closure.skeleton->closure_ptr; \
                retval = ((sanya_t_ClosurePtr1)funcptr)(call, \
                        sanya_g_trampoline_buf.argv[0]); \
                break; \
            } \
            case 2: { \
                void *funcptr = call->as_closure.skeleton->closure_ptr; \
                retval = ((sanya_t_ClosurePtr2)funcptr)(call, \
                        sanya_g_trampoline_buf.argv[0], \
                        sanya_g_trampoline_buf.argv[1]); \
                break; \
            } \
            case 3: { \
                void *funcptr = call->as_closure.skeleton->closure_ptr; \
                retval = ((sanya_t_ClosurePtr3)funcptr)(call, \
                        sanya_g_trampoline_buf.argv[0], \
                        sanya_g_trampoline_buf.argv[1], \
                        sanya_g_trampoline_buf.argv[2]); \
                break; \
            } \
            case 4: { \
                void *funcptr = call->as_closure.skeleton->closure_ptr; \
                retval = ((sanya_t_ClosurePtr4)funcptr)(call, \
                        sanya_g_trampoline_buf.argv[0], \
                        sanya_g_trampoline_buf.argv[1], \
                        sanya_g_trampoline_buf.argv[2], \
                        sanya_g_trampoline_buf.argv[3]); \
                break; \
            } \
            default: { \
                fprintf(stderr, \
                        "tail call with argv = %ld is not supported.\n", \
                        sanya_g_trampoline_buf.argc); \
                fprintf(stderr, "faulting closure: %s.\n", \
                        (call->as_closure.skeleton->name)); \
                exit(1); \
            } \
        } \
    }

#define SANYA_R_CALLCLOSURE_0(retval, closure) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 0); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr0)funcptr)(call); \
        SANYA_R_CHECK_TRAMPOLINE(retval); \
    } while (0)

#define SANYA_R_CALLCLOSURE_1(retval, closure, arg1) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 1); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr1)funcptr)(call, (intptr_t)arg1); \
        SANYA_R_CHECK_TRAMPOLINE(retval); \
    } while (0)

#define SANYA_R_CALLCLOSURE_2(retval, closure, arg1, arg2) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 2); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr2)funcptr)(call, \
                (intptr_t)arg1, (intptr_t)arg2); \
        SANYA_R_CHECK_TRAMPOLINE(retval); \
    } while (0)

#define SANYA_R_CALLCLOSURE_3(retval, closure, arg1, arg2, arg3) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 3); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr3)funcptr)(call, \
                (intptr_t)arg1, (intptr_t)arg2, (intptr_t)arg3); \
        SANYA_R_CHECK_TRAMPOLINE(retval); \
    } while (0)

#define SANYA_R_CALLCLOSURE_4(retval, closure, arg1, arg2, arg3, arg4) \
    do { \
        sanya_t_Object *call = (sanya_t_Object *)closure; \
        sanya_r_check_nb_args(call, 4); \
        void *funcptr = call->as_closure.skeleton->closure_ptr; \
        retval = ((sanya_t_ClosurePtr4)funcptr)(call, \
                (intptr_t)arg1, (intptr_t)arg2, (intptr_t)arg3, \
                (intptr_t)arg4); \
        SANYA_R_CHECK_TRAMPOLINE(retval); \
    } while (0)

#define SANYA_R_TAILCALLCLOSURE_0(closure_) \
    do { \
        sanya_g_trampoline_buf.is_done = 0; \
        sanya_g_trampoline_buf.closure = closure_; \
        sanya_g_trampoline_buf.argc = 0; \
        return 0; \
    } while (0)

#define SANYA_R_TAILCALLCLOSURE_1(closure_, arg1) \
    do { \
        sanya_g_trampoline_buf.is_done = 0; \
        sanya_g_trampoline_buf.closure = closure_; \
        sanya_g_trampoline_buf.argc = 1; \
        sanya_g_trampoline_buf.argv[0] = arg1; \
        return 0; \
    } while (0)

#define SANYA_R_TAILCALLCLOSURE_2(closure_, arg1, arg2) \
    do { \
        sanya_g_trampoline_buf.is_done = 0; \
        sanya_g_trampoline_buf.closure = closure_; \
        sanya_g_trampoline_buf.argc = 2; \
        sanya_g_trampoline_buf.argv[0] = arg1; \
        sanya_g_trampoline_buf.argv[1] = arg2; \
        return 0; \
    } while (0)

#define SANYA_R_TAILCALLCLOSURE_3(closure_, arg1, arg2, arg3) \
    do { \
        sanya_g_trampoline_buf.is_done = 0; \
        sanya_g_trampoline_buf.closure = closure_; \
        sanya_g_trampoline_buf.argc = 2; \
        sanya_g_trampoline_buf.argv[0] = arg1; \
        sanya_g_trampoline_buf.argv[1] = arg2; \
        sanya_g_trampoline_buf.argv[2] = arg3; \
        return 0; \
    } while (0)

#define SANYA_R_TAILCALLCLOSURE_4(closure_, arg1, arg2, arg3, arg4) \
    do { \
        sanya_g_trampoline_buf.is_done = 0; \
        sanya_g_trampoline_buf.closure = closure_; \
        sanya_g_trampoline_buf.argc = 2; \
        sanya_g_trampoline_buf.argv[0] = arg1; \
        sanya_g_trampoline_buf.argv[1] = arg2; \
        sanya_g_trampoline_buf.argv[2] = arg3; \
        sanya_g_trampoline_buf.argv[3] = arg4; \
        return 0; \
    } while (0)


// Runtime
//static inline void sanya_r_check_nb_args(sanya_t_Object *clos, intptr_t nb_args);
sanya_t_CellValue *sanya_r_build_cell_value(intptr_t *ref);
void sanya_r_escape_cell_values(sanya_t_CellValue **cell_list,
                                intptr_t length);
sanya_t_Object *sanya_r_build_closure(sanya_t_ClosureSkeleton *skel,
                                      sanya_t_CellValue **cell_values,
                                      sanya_t_CellValue **fresh_cells);
//static inline intptr_t sanya_r_to_boolean(sanya_t_Object *self);

void sanya_r_halt();
void sanya_r_bootstrap();  // defined in main.c instead.

// Object
#define sanya_r_W_Nil() ((sanya_t_Object *)SANYA_T_NIL)
#define sanya_r_W_Unspecified() ((sanya_t_Object *)SANYA_T_UNSPEC)
#define sanya_r_W_Boolean(bval) \
    ((bval) ? \
        (sanya_t_Object *)(1 << SANYA_R_TAGWIDTH | SANYA_T_BOOLEAN) \
           : \
        (sanya_t_Object *)(0 << SANYA_R_TAGWIDTH | SANYA_T_BOOLEAN))
#define sanya_r_W_Fixnum(ival) \
    (sanya_t_Object *)(((ival) << SANYA_R_TAGWIDTH) | SANYA_T_FIXNUM)

sanya_t_Object *sanya_r_W_Symbol(const char *sval);
sanya_t_Object *sanya_r_W_Pair(intptr_t car, intptr_t cdr);
sanya_t_Object *sanya_r_W_Closure(sanya_t_ClosureSkeleton *skeleton,
                                  sanya_t_CellValue **cell_values);

intptr_t sanya_r_W_Object_Type(sanya_t_Object *self);
intptr_t sanya_r_W_Object_Nullp(sanya_t_Object *self);
#define sanya_r_W_Fixnum_Unwrap(self) \
    ((intptr_t)(self) >> SANYA_R_TAGWIDTH)

// Prelude
void sanya_r_initialize_prelude();
extern intptr_t sanya_g_prelude_display;
extern intptr_t sanya_g_prelude_newline;
extern intptr_t sanya_g_prelude_add;
extern intptr_t sanya_g_prelude_minus;
extern intptr_t sanya_g_prelude_lessthan;
extern intptr_t sanya_g_prelude_num_eq;
extern intptr_t sanya_g_prelude_cons;
extern intptr_t sanya_g_prelude_car;
extern intptr_t sanya_g_prelude_cdr;

// Inlines

#define sanya_r_check_nb_args(clos, nb_args_ck) \
    do { \
        sanya_t_ClosureSkeleton *skel = (clos)->as_closure.skeleton; \
        if (skel->nb_args != nb_args_ck) { \
            fprintf(stderr, "ERROR: closure %s called with wrong number" \
                    " of argument.\n", skel->name); \
            fprintf(stderr, " -- requires %ld arguments, got %ld.\n", \
                    skel->nb_args, (intptr_t)nb_args_ck); \
            exit(1); \
        } \
    } while (0)

static inline intptr_t 
xsanya_r_to_boolean(sanya_t_Object *self)
{
    if (self == sanya_r_W_Boolean(0))
        return 0;
    else
        return 1;
}

#define sanya_r_to_boolean(self) ((self) != sanya_r_W_Boolean(0))

