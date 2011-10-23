
#include "sanya_object.h"

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
sanya_r_W_Symbol(char *sval)
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

