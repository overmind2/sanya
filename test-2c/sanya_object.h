#ifndef SANYA_OBJECT_H
#define SANYA_OBJECT_H

#include "sanya_runtime.h"

#define SANYA_T_FIXNUM  1
#define SANYA_T_UNSPEC  2
#define SANYA_T_NIL     3
#define SANYA_T_BOOLEAN 4
#define SANYA_T_SYMBOL  16
#define SANYA_T_PAIR    17
#define SANYA_T_CLOSURE 18

#define SANYA_R_TAGWIDTH  4
#define SANYA_R_TAGMASK  15

struct sanya_t_Object_ {
    intptr_t type;
    union {
        char *as_symbol;
        struct {
            sanya_t_Object *car;
            sanya_t_Object *cdr;
        } as_pair;
        struct {
            sanya_t_ClosureSkeleton *skeleton;
            sanya_t_CellValue **cell_values;
        } as_closure;
    };
};

// Constructors
sanya_t_Object *sanya_r_W_Nil();
sanya_t_Object *sanya_r_W_Unspecified();
sanya_t_Object *sanya_r_W_Boolean(intptr_t bval);
sanya_t_Object *sanya_r_W_Fixnum(intptr_t ival);
sanya_t_Object *sanya_r_W_Symbol(char *sval);
sanya_t_Object *sanya_r_W_Pair(intptr_t car, intptr_t cdr);
sanya_t_Object *sanya_r_W_Closure(sanya_t_ClosureSkeleton *skeleton,
                                  sanya_t_CellValue **cell_values);

intptr_t sanya_r_W_Object_Type(sanya_t_Object *self);
intptr_t sanya_r_W_Object_Nullp(sanya_t_Object *self);
intptr_t sanya_r_W_Fixnum_Unwrap(sanya_t_Object *self);

#endif /* SANYA_OBJECT_H */
