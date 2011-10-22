#include "sanya_runtime.h"
#include "sanya_object.h"

static sanya_t_CellValue dummy_cell_head = {
    NULL,
    { NULL },
    &dummy_cell_head,
    &dummy_cell_head
};

void
sanya_r_check_nb_args(sanya_t_Object *clos, intptr_t nb_args)
{
    sanya_t_ClosureSkeleton *skel = clos->as_closure.skeleton;
    if (skel->nb_args != nb_args) {
        fprintf(stderr, "ERROR: closure %s called with wrong number"
                " of argument.\n", skel->name);
        fprintf(stderr, " -- requires %ld arguments, got %ld.\n",
                skel->nb_args, nb_args);
        exit(1);
    }
}

// ref is a c-stack slot currently.
sanya_t_CellValue *
sanya_r_build_cell_value(intptr_t *ref, intptr_t *frame_mark)
{
    sanya_t_CellValue *self = malloc(sizeof(sanya_t_CellValue));
    self->ref = ref;
    self->frame_mark = frame_mark;

    self->next = dummy_cell_head.next;
    self->prev = &dummy_cell_head;
    dummy_cell_head.next->prev = self;
    dummy_cell_head.next = self;
    return self;
}

// escape cell values that matches this frame_mark to the heap.
void
sanya_r_escape_cell_values(intptr_t *frame_mark)
{
    sanya_t_CellValue *iter = dummy_cell_head.next;
    sanya_t_CellValue *next_cell;
    while (iter != &dummy_cell_head) {
        next_cell = iter->next;
        if (iter->frame_mark == frame_mark) {
            // Unlink from list.
            iter->prev->next = next_cell;
            next_cell->prev = iter->prev;

            // Escape.
            iter->escaped_value = *(iter->ref);
            iter->ref = &(iter->escaped_value);
        }
        iter = next_cell;
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

