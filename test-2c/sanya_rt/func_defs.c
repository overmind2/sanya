
// Runtime

// ref is a c-stack slot currently.
sanya_t_CellValue *
sanya_r_build_cell_value(intptr_t *ref)
{
    sanya_t_CellValue *self = malloc(sizeof(sanya_t_CellValue));
    self->ref = ref;
    return self;
}

// escape cell values that matches this frame_mark to the heap.
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

intptr_t
sanya_r_to_boolean(sanya_t_Object *self)
{
    if (self == sanya_r_W_Boolean(0))
        return 0;
    else
        return 1;
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
sanya_r_W_Nil()
{
    return (sanya_t_Object *)SANYA_T_NIL;
}

sanya_t_Object *
sanya_r_W_Unspecified()
{
    return (sanya_t_Object *)SANYA_T_UNSPEC;
}

sanya_t_Object *
sanya_r_W_Boolean(intptr_t bval)
{
    if (bval)
        return (sanya_t_Object *)(1 << SANYA_R_TAGWIDTH | SANYA_T_BOOLEAN);
    else
        return (sanya_t_Object *)(0 << SANYA_R_TAGWIDTH | SANYA_T_BOOLEAN);
}

sanya_t_Object *
sanya_r_W_Fixnum(intptr_t ival)
{
    return (sanya_t_Object *)((ival << SANYA_R_TAGWIDTH) | SANYA_T_FIXNUM);
}

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

intptr_t
sanya_r_W_Fixnum_Unwrap(sanya_t_Object *self)
{
    return (intptr_t)self >> SANYA_R_TAGWIDTH;
}

// Prelude
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

