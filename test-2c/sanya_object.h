
#include "sanya_runtime.h"

#define SANYA_T_NIL     0
#define SANYA_T_FIXNUM  1
#define SANYA_T_SYMBOL  2
#define SANYA_T_PAIR    3
#define SANYA_T_CLOSURE 4

struct sanya_t_Object_ {
    intptr_t type;
    union {
        intptr_t as_fixnum;
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

sanya_t_Object *sanya_r_create_fixnum(intptr_t ival);
sanya_t_Object *sanya_r_create_symbol(char *sval);
sanya_t_Object *sanya_r_create_pair(intptr_t car, intptr_t cdr);
sanya_t_Object *sanya_r_create_closure(intptr_t skeleton, intptr_t cell_values);

