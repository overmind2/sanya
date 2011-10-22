
#include "sanya_prelude.h"

void
sanya_p_display(intptr_t *ls_retval, sanya_t_Object *ls_closure,
                intptr_t ls_nb_args, ...)
{
    sanya_t_Object *item;
    sanya_r_check_nb_args(ls_closure, ls_nb_args);
    va_list ls_arg_list;
    va_start(ls_arg_list, ls_nb_args);
    item = va_arg(ls_arg_list, sanya_t_Object *);

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
}

