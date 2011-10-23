#include "func_decl.h"

// Runtime

// ref is a c-stack slot currently.
sanya_t_CellValue *
sanya_r_build_cell_value(intptr_t *ref)
{
    sanya_t_CellValue *self = malloc(sizeof(sanya_t_CellValue));
    self->ref = ref;
    return self;
}

// escape cell values that is build freshly.
void
sanya_r_escape_cell_values(sanya_t_CellValue **cell_list, intptr_t length)
{
    intptr_t i;
    for (i = 0; i < length; ++i) {
        sanya_t_CellValue *iter = cell_list[i];
        iter->escaped_value = *(iter->ref);
        iter->ref = &(iter->escaped_value);
    }
}

// @see sanya/closure.py - W_Skeleton.build_closure
sanya_t_Object *sanya_r_build_closure(sanya_t_ClosureSkeleton *skel,
                                      sanya_t_CellValue **cell_values,
                                      sanya_t_CellValue **fresh_cells)
{
    intptr_t i, recipt, fresh_p, real_index;
    sanya_t_CellValue **new_cell_values =
        malloc(sizeof(sanya_t_CellValue *) * skel->nb_cells);

    for (i = 0; i < skel->nb_cells; ++i) {
        recipt = skel->cell_recipt[i];
        fresh_p = recipt & 0x1;
        real_index = recipt >> 1;

        if (fresh_p) {
            // Is moved from parent's fresh_cells
            new_cell_values[i] = fresh_cells[real_index];
        }
        else {
            // Is shared from parent's cell_values
            new_cell_values[i] = cell_values[real_index];
        }
    }
    return sanya_r_W_Closure(skel, new_cell_values);
}

void
sanya_r_halt()
{
    exit(0);
}

// Object

sanya_t_Object *
sanya_r_W_Symbol(const char *sval)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_SYMBOL;
    self->as_symbol = sval;
    return self;
}

sanya_t_Object *
sanya_r_W_Pair(intptr_t car, intptr_t cdr)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_PAIR;
    self->as_pair.car = (sanya_t_Object *)car;
    self->as_pair.cdr = (sanya_t_Object *)cdr;
    return self;
}

sanya_t_Object *
sanya_r_W_Closure(sanya_t_ClosureSkeleton *skeleton,
                  sanya_t_CellValue **cell_values)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_CLOSURE;
    self->as_closure.skeleton = skeleton;
    self->as_closure.cell_values = cell_values;
    return self;
}

intptr_t
sanya_r_W_Object_Type(sanya_t_Object *self)
{
    intptr_t type;
    if ((type = (intptr_t)self & SANYA_R_TAGMASK))
        return type;
    else
        return self->type;
}

intptr_t
sanya_r_W_Object_Nullp(sanya_t_Object *self)
{
    return sanya_r_W_Object_Type(self) == SANYA_T_NIL;
}

// Prelude
intptr_t sanya_g_prelude_display;
intptr_t sanya_g_prelude_newline;
intptr_t sanya_g_prelude_add;
intptr_t sanya_g_prelude_minus;
intptr_t sanya_g_prelude_lessthan;
intptr_t sanya_g_prelude_num_eq;
intptr_t sanya_g_prelude_cons;
intptr_t sanya_g_prelude_car;
intptr_t sanya_g_prelude_cdr;

static sanya_t_ClosureSkeleton sanya_g_prelude_display_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_newline_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_add_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_minus_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_lessthan_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_num_eq_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_cons_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_car_skel;
static sanya_t_ClosureSkeleton sanya_g_prelude_cdr_skel;

static intptr_t
display(sanya_t_Object *ls_closure, intptr_t arg1)
{
    sanya_t_Object *item = (sanya_t_Object *)arg1;
    switch (sanya_r_W_Object_Type(item)) {
        case SANYA_T_FIXNUM:
            printf("%ld", sanya_r_W_Fixnum_Unwrap(item));
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
            printf("%s", item->as_symbol);
            break;
        case SANYA_T_PAIR:
            {
                printf("(");
                display(ls_closure, item->as_pair.car);
                item = item->as_pair.cdr;
                for (; sanya_r_W_Object_Type(item) == SANYA_T_PAIR;
                        item = item->as_pair.cdr) {
                    printf(" ");
                    display(ls_closure, item->as_pair.car);
                }
                if (!sanya_r_W_Object_Nullp(item)) {
                    printf(" . ");
                    display(ls_closure, item);
                }
                printf(")");
                break;
            }
        case SANYA_T_CLOSURE:
            printf("#<closure `%s` at %p>",
                    item->as_closure.skeleton->name, item);
            break;
        default:
            printf("#<unknown at %p>", item);
            break;
    }
    SANYA_R_RETURN_VALUE((intptr_t)sanya_r_W_Unspecified());
}

static intptr_t
newline(sanya_t_Object *ls_closure)
{
    puts("");
    SANYA_R_RETURN_VALUE((intptr_t)sanya_r_W_Unspecified());
}

static sanya_t_Object *
add(sanya_t_Object *ls_closure,
    sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    SANYA_R_RETURN_VALUE(sanya_r_W_Fixnum(sanya_r_W_Fixnum_Unwrap(arg1) + 
                                          sanya_r_W_Fixnum_Unwrap(arg2)));
}

static sanya_t_Object *
minus(sanya_t_Object *ls_closure,
      sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    SANYA_R_RETURN_VALUE(sanya_r_W_Fixnum(sanya_r_W_Fixnum_Unwrap(arg1) -
                                          sanya_r_W_Fixnum_Unwrap(arg2)));
}

static sanya_t_Object *
lessthan(sanya_t_Object *ls_closure,
         sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    SANYA_R_RETURN_VALUE(sanya_r_W_Boolean(sanya_r_W_Fixnum_Unwrap(arg1) <
                                           sanya_r_W_Fixnum_Unwrap(arg2)));
}

static sanya_t_Object *
num_eq(sanya_t_Object *ls_closure,
       sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    SANYA_R_RETURN_VALUE(sanya_r_W_Boolean(sanya_r_W_Fixnum_Unwrap(arg1) ==
                                           sanya_r_W_Fixnum_Unwrap(arg2)));
}

static sanya_t_Object *
cons(sanya_t_Object *ls_closure, sanya_t_Object *arg1, sanya_t_Object *arg2)
{
    SANYA_R_RETURN_VALUE(sanya_r_W_Pair(arg1, arg2));
}

static sanya_t_Object *
car(sanya_t_Object *ls_closure, sanya_t_Object *arg1)
{
    SANYA_R_RETURN_VALUE(arg1->as_pair.car);
}

static sanya_t_Object *
cdr(sanya_t_Object *ls_closure, sanya_t_Object *arg1)
{
    SANYA_R_RETURN_VALUE(arg1->as_pair.cdr);
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

    sanya_g_prelude_minus_skel.name = "-";
    sanya_g_prelude_minus_skel.nb_args = 2;
    sanya_g_prelude_minus_skel.closure_ptr = minus;
    sanya_g_prelude_minus = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_minus_skel, NULL);

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

    sanya_g_prelude_cons_skel.name = "cons";
    sanya_g_prelude_cons_skel.nb_args = 2;
    sanya_g_prelude_cons_skel.closure_ptr = cons;
    sanya_g_prelude_cons = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_cons_skel, NULL);

    sanya_g_prelude_car_skel.name = "car";
    sanya_g_prelude_car_skel.nb_args = 1;
    sanya_g_prelude_car_skel.closure_ptr = car;
    sanya_g_prelude_car = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_car_skel, NULL);

    sanya_g_prelude_cdr_skel.name = "cdr";
    sanya_g_prelude_cdr_skel.nb_args = 1;
    sanya_g_prelude_cdr_skel.closure_ptr = cdr;
    sanya_g_prelude_cdr = (intptr_t)sanya_r_W_Closure(
            &sanya_g_prelude_cdr_skel, NULL);

}

