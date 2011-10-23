
#include "sanya_prelude.h"

intptr_t
sanya_p_display(sanya_t_Object *ls_closure, intptr_t arg1)
{
    sanya_t_Object *item = (sanya_t_Object *)arg1;
    switch (sanya_r_W_Object_Type(item)) {
        case SANYA_T_FIXNUM:
            printf("#<fixnum %ld>\n", sanya_r_W_Fixnum_Unwrap(item));
            break;
        case SANYA_T_UNSPEC:
            printf("#<unspecified>\n");
            break;
        case SANYA_T_NIL:
            printf("()");
            break;
        case SANYA_T_SYMBOL:
            printf("#<symbol %s>\n", item->as_symbol);
            break;
        case SANYA_T_PAIR:
            printf("#<pair at %p>\n", item);
            break;
        case SANYA_T_CLOSURE:
            printf("#<closure at %p>\n", item);
            break;
        default:
            printf("#<unknown at %p>\n", item);
            break;
    }
    return (intptr_t)sanya_r_W_Unspecified();
}

