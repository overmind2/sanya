#include "sanya_runtime.h"
#include "sanya_object.h"
#include "sanya_prelude.h"

// Preludes
sanya_t_ClosureSkeleton sanya_g_display;

// Globals
intptr_t sanya_g_global_variables[123];
sanya_t_ClosureSkeleton sanya_g_skeleton_table[5];

// General closure pointer.
// sanya_r_load_cell
// sanya_r_check_nb_args
// sanya_r_build_closure
intptr_t sanya_g_closure_ptr_0(sanya_t_Object *ls_closure, intptr_t v_0)
{
    intptr_t v_1, v_2, v_3, v_4, v_5;
    sanya_t_CellValue *ls_fresh_cells[1];

    // build fresh cell values.
    ls_fresh_cells[0] = sanya_r_build_cell_value(&v_0);

    // Unpack va-args, don't consider for now.
    //v_5 = sanya_r_unpack_vararg(ls_arg_list, 

    // done unpacking args.

    // Load from consts
    v_4 = ls_closure->as_closure.skeleton->consts[0];

    // Load from cell
    v_5 = *(ls_closure->as_closure.cell_values[0]->ref);
    // Store to cell
    *(ls_closure->as_closure.cell_values[0]->ref) = v_3;

    // BuildClosure, consider inline this?
    v_0 = (intptr_t)sanya_r_build_closure(sanya_g_skeleton_table + 0,
                                          ls_closure->as_closure.cell_values,
                                          ls_fresh_cells);
    sanya_g_global_variables[0] = v_0;

    // Call closure, seems it's prone to segfault...
    v_1 = sanya_g_global_variables[0];

    // argument length check is done by caller -- speeds up calling.
    SANYA_R_CALLCLOSURE_0(v_2, v_1);  // call v_1, return to v_2

    // prepare for return -- escape the cell values at first.
    sanya_r_escape_cell_values(ls_fresh_cells, 1);
    return v_1;
}

// Special case.
void sanya_r_toplevel()
{
    intptr_t v_0, v_1, v_2, v_3, v_4, v_5;

    // Load from consts -- different from non-toplevel
    intptr_t *ls_toplevel_consts = sanya_g_skeleton_table[4].consts;
    v_4 = ls_toplevel_consts[0];

    // BuildClosure, consider inline this?
    v_0 = (intptr_t)sanya_r_build_closure(sanya_g_skeleton_table + 1,
                                          NULL, NULL);
    sanya_g_global_variables[0] = v_0;

    // argument length check is done by caller -- speeds up calling.
    // call v_1, return to v_2, two args: v_3 and v_4
    SANYA_R_CALLCLOSURE_2(v_2, v_1, v_3, v_4);

    // halt
    sanya_r_halt();

    // noreturn -- different from non-toplevels
}

// Initializer
void
sanya_r_bootstrap()
{
    sanya_g_skeleton_table[0].consts = malloc(sizeof(intptr_t) * 3);
    sanya_g_skeleton_table[0].consts[0] = 0;
    sanya_g_skeleton_table[0].cell_recipt = malloc(sizeof(intptr_t) * 4);
    sanya_g_skeleton_table[0].closure_ptr = sanya_g_closure_ptr_0;
    sanya_g_skeleton_table[0].nb_args = 0;
    sanya_g_skeleton_table[0].vararg_p = 0;
}

void
sanya_r_initialize_prelude()
{
    {
        sanya_g_display.nb_args = 1;
        sanya_g_display.name = "display";
        sanya_g_display.closure_ptr = sanya_p_display;
        sanya_t_Object *display = sanya_r_W_Closure(&sanya_g_display, NULL);
        sanya_g_global_variables[10] = (intptr_t)display;
    }
}

// Entrypoint

int
main()
{
    sanya_r_bootstrap();
    sanya_r_initialize_prelude();
    {
        intptr_t res;
        SANYA_R_CALLCLOSURE_1(res, sanya_g_global_variables[10],
                              sanya_r_W_Fixnum(10));
        SANYA_R_CALLCLOSURE_1(res, sanya_g_global_variables[10], res);
    }
    //sanya_r_toplevel();
    return 0;
}

