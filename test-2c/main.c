#include "sanya_runtime.h"
#include "sanya_object.h"

// Globals

sanya_t_ClosureSkeleton sanya_g_closure_skeleton_0,
                        sanya_g_closure_skeleton_1,
                        sanya_g_closure_skeleton_2,
                        sanya_g_closure_skeleton_3,
                        sanya_g_closure_skeleton_4;

intptr_t sanya_g_global_variables[123];

sanya_t_CellValue sanya_g_cell_value_dummy_head;
intptr_t *sanya_g_cell_value_head;

// sanya_r_load_cell
// sanya_r_check_nb_args
// sanya_r_build_closure
void sanya_g_toplevel(sanya_t_ClosureSkeleton *ls_skeleton,
                      sanya_t_CellValue **ls_cell_values,
                      intptr_t *ls_retval,
                      intptr_t ls_nb_args, ...)
{
    intptr_t v_0, v_1, v_2, v_3, v_4, v_5;
    va_list ls_arg_list;
    intptr_t ls_frame_marker;
    sanya_t_CellValue *ls_fresh_cells[1];

    // Inline argument count check?
    sanya_r_check_nb_args(ls_skeleton, ls_nb_args);
    va_start(ls_arg_list, ls_nb_args);

    // build fresh cell values.
    ls_fresh_cells[0] = sanya_r_build_cell_value(&v_0, &ls_frame_marker);

    // Assume we have some arguments...
    v_3 = va_arg(ls_arg_list, intptr_t);

    // Unpack va-args, don't consider for now.
    //v_5 = sanya_r_unpack_vararg(ls_arg_list, 

    // done unpacking args.
    va_end(ls_arg_list);

    // Load from consts
    v_4 = ls_skeleton->consts[0];

    // BuildClosure, consider inline this?
    v_0 = (intptr_t)sanya_r_build_closure(&sanya_g_closure_skeleton_0,
                                          ls_cell_values,
                                          ls_fresh_cells);
    sanya_g_global_variables[0] = v_0;

    // Call closure, seems it's prone to segfault...
    v_1 = sanya_g_global_variables[0];
    ((sanya_t_Object *)v_1)->as_closure.skeleton->closure_ptr(
        ((sanya_t_Object *)v_1)->as_closure.skeleton,
        ((sanya_t_Object *)v_1)->as_closure.cell_values,
        &v_2,  // retval
        2,  // argcount
        v_3, v_4);  // arguments

    // halt
    sanya_r_halt();
}

// Initializer
void
sanya_r_bootstrap()
{
    sanya_g_closure_skeleton_0.consts = malloc(sizeof(intptr_t) * 3);
    sanya_g_closure_skeleton_0.consts[0] = 0;
    sanya_g_closure_skeleton_0.cell_recipt = malloc(sizeof(intptr_t) * 4);
    sanya_g_closure_skeleton_0.closure_ptr = sanya_g_toplevel;
    sanya_g_closure_skeleton_0.nb_args = 0;
    sanya_g_closure_skeleton_0.vararg_p = 0;
}

int
main()
{
    sanya_r_bootstrap();
    sanya_g_toplevel(&sanya_g_closure_skeleton_1, NULL, NULL, 0);
    return 0;
}
