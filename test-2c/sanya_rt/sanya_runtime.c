#include "sanya_runtime.h"
#include "sanya_object.h"

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

