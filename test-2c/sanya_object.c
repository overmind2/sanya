
#include "sanya_obj.h"

sanya_t_Object *
sanya_r_create_fixnum(intptr_t ival)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_FIXNUM;
    self->as_fixnum = ival;
    return self;
}

sanya_t_Object *
sanya_r_create_symbol(char *sval)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_SYMBOL;
    self->as_symbol = sval;
    return self;
}

sanya_t_Object *
sanya_r_create_pair(intptr_t car, intptr_t cdr)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_PAIR;
    self->as_pair.car = (sanya_t_Object *)car;
    self->as_pair.cdr = (sanya_t_Object *)cdr;
    return self;
}

sanya_t_Object *
sanya_r_create_closure(intptr_t skeleton, intptr_t cell_values)
{
    sanya_t_Object *self = malloc(sizeof(sanya_t_Object));
    self->type = SANYA_T_CLOSURE;
    self->as_closure.skeleton = (sanya_t_ClosureSkeleton *)skeleton;
    self->as_closure.cell_values = (sanya_t_CellValue **)cell_values;
    return self;
}

