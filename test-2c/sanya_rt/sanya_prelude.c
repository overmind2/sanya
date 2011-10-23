
#include "sanya_prelude.h"

intptr_t sanya_g_prelude_display;
intptr_t sanya_g_prelude_newline;
intptr_t sanya_g_prelude_add;
intptr_t sanya_g_prelude_lessthan;
intptr_t sanya_g_prelude_num_eq;

static sanya_t_ClosureSkeleton sanya_g_prelude_display_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_newline_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_add_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_lessthan_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_num_eq_skel;

static intptr_t
display(sanya_t_Object *ls_closure, intptr_t arg1)
{
    sanya_t_Object *item = (sanya_t_Object *)arg1;
    switch (sanya_r_W_Object_Type(item)) {
        case SANYA_T_FIXNUM:
            printf("#<fixnum %ld>", sanya_r_W_Fixnum_Unwrap(item));
            break;
        case SANYA_T_UNSPEC:
            printf("#<unspecified>");
            break;
        case SANYA_T_NIL:
            printf("()");
            break;
        case SANYA_T_BOOLEAN:
            printf("%s", sanya_r_to_boolean(item) ? "#t" : "#f");
            break;
        case SANYA_T_SYMBOL:
            printf("#<symbol %s>", item->as_symbol);
            break;
        case SANYA_T_PAIR:
            printf("#<pair at %p>", item);
            break;
        case SANYA_T_CLOSURE:
            printf("#<closure `%s` at %p>",
                    item->as_closure.skeleton->name, item);
            break;
        default:
            printf("#<unknown at %p>", item);
            break;
    }
    return (intptr_t)sanya_r_W_Unspecified();
}

static intptr_t
newline(sanya_t_Object *ls_closure)
{
    puts("");
    return (intptr_t)sanya_r_W_Unspecified();
}

static sanya_t_Object *
add(sanya_t_Object *ls_closure, sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    return sanya_r_W_Fixnum(sanya_r_W_Fixnum_Unwrap(arg1) + 
                            sanya_r_W_Fixnum_Unwrap(arg2));
}

static sanya_t_Object *
lessthan(sanya_t_Object *ls_closure, sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    return sanya_r_W_Boolean(sanya_r_W_Fixnum_Unwrap(arg1) <
                             sanya_r_W_Fixnum_Unwrap(arg2));
}

static sanya_t_Object *
num_eq(sanya_t_Object *ls_closure, sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    return sanya_r_W_Boolean(sanya_r_W_Fixnum_Unwrap(arg1) ==
                             sanya_r_W_Fixnum_Unwrap(arg2));
}

void
sanya_r_initialize_prelude()
{
    sanya_g_prelude_display_skel.name = "display";
    sanya_g_prelude_display_skel.nb_args = 1;
    sanya_g_prelude_display_skel.closure_ptr = display;
    sanya_g_prelude_display = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_display_skel, NULL);

    sanya_g_prelude_newline_skel.name = "newline";
    sanya_g_prelude_newline_skel.nb_args = 0;
    sanya_g_prelude_newline_skel.closure_ptr = newline;
    sanya_g_prelude_newline = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_newline_skel, NULL);

    sanya_g_prelude_add_skel.name = "+";
    sanya_g_prelude_add_skel.nb_args = 2;
    sanya_g_prelude_add_skel.closure_ptr = add;
    sanya_g_prelude_add = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_add_skel, NULL);

    sanya_g_prelude_lessthan_skel.name = "<";
    sanya_g_prelude_lessthan_skel.nb_args = 2;
    sanya_g_prelude_lessthan_skel.closure_ptr = lessthan;
    sanya_g_prelude_lessthan = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_lessthan_skel, NULL);

    sanya_g_prelude_num_eq_skel.name = "=";
    sanya_g_prelude_num_eq_skel.nb_args = 2;
    sanya_g_prelude_num_eq_skel.closure_ptr = num_eq;
    sanya_g_prelude_num_eq = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_num_eq_skel, NULL);
}

