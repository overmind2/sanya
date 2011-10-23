#include "func_decl.h"

// Globals
sanya_t_TrampolineBuf sanya_g_trampoline_buf;
intptr_t sanya_g_global_variable_0;
intptr_t sanya_g_global_variable_1;
intptr_t sanya_g_global_variable_2;
intptr_t sanya_g_global_variable_3;
intptr_t sanya_g_global_variable_4;
intptr_t sanya_g_global_variable_5;
intptr_t sanya_g_global_variable_6;
intptr_t sanya_g_global_variable_7;
intptr_t sanya_g_global_variable_8;
intptr_t sanya_g_global_variable_9;
sanya_t_ClosureSkeleton sanya_g_skeleton_0;
sanya_t_ClosureSkeleton sanya_g_skeleton_1;
sanya_t_ClosureSkeleton sanya_g_skeleton_2;
sanya_t_ClosureSkeleton sanya_g_skeleton_3;
sanya_t_ClosureSkeleton sanya_g_skeleton_4;
intptr_t sanya_g_skeleton_cell_recipt_0[] = {  };
intptr_t sanya_g_skeleton_cell_recipt_1[] = {  };
intptr_t sanya_g_skeleton_cell_recipt_2[] = { 1 };
intptr_t sanya_g_skeleton_cell_recipt_3[] = {  };
intptr_t sanya_g_skeleton_cell_recipt_4[] = {  };
intptr_t *sanya_g_toplevel_consts;

// Closure `print`
intptr_t
sanya_g_closure_ptr_0(sanya_t_Object *ls_closure, intptr_t v_0)
{
    intptr_t v_1, v_2, v_3, v_4, v_5, v_6;
    v_1 = sanya_g_prelude_display;
    v_2 = v_0;
    SANYA_R_CALLCLOSURE_1(v_3, v_1, v_2);
    v_4 = sanya_g_prelude_newline;
    SANYA_R_TAILCALLCLOSURE_0(v_4);
    SANYA_R_RETURN_VALUE(v_5);
}  // End of closure `print`

// Closure `fibo`
intptr_t
sanya_g_closure_ptr_1(sanya_t_Object *ls_closure, intptr_t v_0)
{
    intptr_t v_1, v_2, v_3, v_4, v_5, v_6, v_7, v_8, v_9, v_10, v_11, v_12, v_13, v_14, v_15, v_16, v_17, v_18, v_19, v_20, v_21, v_22, v_23, v_24;
    v_2 = sanya_g_prelude_lessthan;
    v_3 = v_0;
    v_4 = ls_closure->as_closure.skeleton->consts[0];
    SANYA_R_CALLCLOSURE_2(v_5, v_2, v_3, v_4);
    if (!sanya_r_to_boolean((sanya_t_Object *)v_5)) goto LABEL_0;
    v_1 = v_0;
    goto LABEL_1;
    LABEL_0: { /* label statement */ }
    v_6 = sanya_g_prelude_add;
    v_9 = sanya_g_global_variable_1;
    v_11 = sanya_g_prelude_minus;
    v_12 = v_0;
    v_13 = ls_closure->as_closure.skeleton->consts[1];
    SANYA_R_CALLCLOSURE_2(v_14, v_11, v_12, v_13);
    v_10 = v_14;
    SANYA_R_CALLCLOSURE_1(v_15, v_9, v_10);
    v_7 = v_15;
    v_16 = sanya_g_global_variable_1;
    v_18 = sanya_g_prelude_minus;
    v_19 = v_0;
    v_20 = ls_closure->as_closure.skeleton->consts[2];
    SANYA_R_CALLCLOSURE_2(v_21, v_18, v_19, v_20);
    v_17 = v_21;
    SANYA_R_CALLCLOSURE_1(v_22, v_16, v_17);
    v_8 = v_22;
    SANYA_R_TAILCALLCLOSURE_2(v_6, v_7, v_8);
    v_1 = v_23;
    LABEL_1: { /* label statement */ }
    SANYA_R_RETURN_VALUE(v_1);
}  // End of closure `fibo`

// Closure `sum1`
intptr_t
sanya_g_closure_ptr_2(sanya_t_Object *ls_closure, intptr_t v_0, intptr_t v_1)
{
    intptr_t v_2, v_3, v_4, v_5, v_6, v_7, v_8, v_9, v_10, v_11, v_12, v_13, v_14, v_15, v_16, v_17, v_18, v_19;
    v_3 = sanya_g_prelude_lessthan;
    v_4 = v_0;
    v_5 = ls_closure->as_closure.skeleton->consts[0];
    SANYA_R_CALLCLOSURE_2(v_6, v_3, v_4, v_5);
    if (!sanya_r_to_boolean((sanya_t_Object *)v_6)) goto LABEL_2;
    v_2 = v_1;
    goto LABEL_3;
    LABEL_2: { /* label statement */ }
    v_7 = *(ls_closure->as_closure.cell_values[0]->ref);
    v_10 = sanya_g_prelude_minus;
    v_11 = v_0;
    v_12 = ls_closure->as_closure.skeleton->consts[1];
    SANYA_R_CALLCLOSURE_2(v_13, v_10, v_11, v_12);
    v_8 = v_13;
    v_14 = sanya_g_prelude_add;
    v_15 = v_0;
    v_16 = v_1;
    SANYA_R_CALLCLOSURE_2(v_17, v_14, v_15, v_16);
    v_9 = v_17;
    SANYA_R_TAILCALLCLOSURE_2(v_7, v_8, v_9);
    v_2 = v_18;
    LABEL_3: { /* label statement */ }
    SANYA_R_RETURN_VALUE(v_2);
}  // End of closure `sum1`

// Closure `sum`
intptr_t
sanya_g_closure_ptr_3(sanya_t_Object *ls_closure, intptr_t v_0)
{
    intptr_t v_1, v_2, v_3, v_4, v_5, v_6, v_7;
    sanya_t_CellValue *ls_fresh_cells[1];
    ls_fresh_cells[0] = sanya_r_build_cell_value(&v_2);
    // Build from skeleton `sum1`
    v_1 = (intptr_t)sanya_r_build_closure(&sanya_g_skeleton_2, ls_closure->as_closure.cell_values, ls_fresh_cells);
    v_2 = v_1;
    v_3 = v_2;
    v_4 = v_0;
    v_5 = ls_closure->as_closure.skeleton->consts[1];
    sanya_r_escape_cell_values(ls_fresh_cells, 1);
    SANYA_R_TAILCALLCLOSURE_2(v_3, v_4, v_5);
    sanya_r_escape_cell_values(ls_fresh_cells, 1);
    SANYA_R_RETURN_VALUE(v_6);
}  // End of closure `sum`

// Closure `main`
intptr_t
sanya_g_closure_ptr_4(sanya_t_Object *ls_closure)
{
    intptr_t v_0, v_1, v_2, v_3, v_4, v_5, v_6, v_7, v_8, v_9, v_10, v_11, v_12, v_13, v_14, v_15, v_16, v_17, v_18, v_19, v_20, v_21;
    v_0 = sanya_g_global_variable_0;
    v_2 = sanya_g_prelude_cons;
    v_3 = ls_closure->as_closure.skeleton->consts[0];
    v_5 = sanya_g_prelude_cons;
    v_6 = ls_closure->as_closure.skeleton->consts[1];
    v_8 = sanya_g_prelude_cons;
    v_9 = ls_closure->as_closure.skeleton->consts[2];
    v_10 = ls_closure->as_closure.skeleton->consts[3];
    SANYA_R_CALLCLOSURE_2(v_11, v_8, v_9, v_10);
    v_7 = v_11;
    SANYA_R_CALLCLOSURE_2(v_12, v_5, v_6, v_7);
    v_4 = v_12;
    SANYA_R_CALLCLOSURE_2(v_13, v_2, v_3, v_4);
    v_1 = v_13;
    SANYA_R_CALLCLOSURE_1(v_14, v_0, v_1);
    v_15 = sanya_g_global_variable_0;
    v_17 = sanya_g_global_variable_1;
    v_18 = ls_closure->as_closure.skeleton->consts[4];
    SANYA_R_CALLCLOSURE_1(v_19, v_17, v_18);
    v_16 = v_19;
    SANYA_R_TAILCALLCLOSURE_1(v_15, v_16);
    SANYA_R_RETURN_VALUE(v_20);
}  // End of closure `main`

// Toplevel
void sanya_r_toplevel()
{
    intptr_t v_0, v_1, v_2, v_3, v_4, v_5, v_6;
    // Build from skeleton `print`
    v_0 = (intptr_t)sanya_r_build_closure(&sanya_g_skeleton_0, NULL, NULL);
    sanya_g_global_variable_0 = v_0;
    // Build from skeleton `fibo`
    v_1 = (intptr_t)sanya_r_build_closure(&sanya_g_skeleton_1, NULL, NULL);
    sanya_g_global_variable_1 = v_1;
    // Build from skeleton `sum`
    v_2 = (intptr_t)sanya_r_build_closure(&sanya_g_skeleton_3, NULL, NULL);
    sanya_g_global_variable_2 = v_2;
    // Build from skeleton `main`
    v_3 = (intptr_t)sanya_r_build_closure(&sanya_g_skeleton_4, NULL, NULL);
    sanya_g_global_variable_3 = v_3;
    v_4 = sanya_g_global_variable_3;
    SANYA_R_CALLCLOSURE_0(v_5, v_4);
    sanya_r_halt();
}  // End of toplevel.

void
sanya_r_bootstrap()
{
    sanya_g_skeleton_0.name = "print";
    sanya_g_skeleton_0.consts = malloc(sizeof(intptr_t) * 0);
    sanya_g_skeleton_0.cell_recipt = sanya_g_skeleton_cell_recipt_0;
    sanya_g_skeleton_0.nb_cells = 0;
    sanya_g_skeleton_0.closure_ptr = sanya_g_closure_ptr_0;
    sanya_g_skeleton_0.nb_args = 1;
    sanya_g_skeleton_0.varargs_p = 0;
    
    sanya_g_skeleton_1.name = "fibo";
    sanya_g_skeleton_1.consts = malloc(sizeof(intptr_t) * 3);
    sanya_g_skeleton_1.consts[0] = sanya_r_W_Fixnum(2);
    sanya_g_skeleton_1.consts[1] = sanya_r_W_Fixnum(1);
    sanya_g_skeleton_1.consts[2] = sanya_r_W_Fixnum(2);
    sanya_g_skeleton_1.cell_recipt = sanya_g_skeleton_cell_recipt_1;
    sanya_g_skeleton_1.nb_cells = 0;
    sanya_g_skeleton_1.closure_ptr = sanya_g_closure_ptr_1;
    sanya_g_skeleton_1.nb_args = 1;
    sanya_g_skeleton_1.varargs_p = 0;
    
    sanya_g_skeleton_2.name = "sum1";
    sanya_g_skeleton_2.consts = malloc(sizeof(intptr_t) * 2);
    sanya_g_skeleton_2.consts[0] = sanya_r_W_Fixnum(1);
    sanya_g_skeleton_2.consts[1] = sanya_r_W_Fixnum(1);
    sanya_g_skeleton_2.cell_recipt = sanya_g_skeleton_cell_recipt_2;
    sanya_g_skeleton_2.nb_cells = 1;
    sanya_g_skeleton_2.closure_ptr = sanya_g_closure_ptr_2;
    sanya_g_skeleton_2.nb_args = 2;
    sanya_g_skeleton_2.varargs_p = 0;
    
    sanya_g_skeleton_3.name = "sum";
    sanya_g_skeleton_3.consts = malloc(sizeof(intptr_t) * 2);
    sanya_g_skeleton_3.consts[0] = sanya_r_W_Unspecified();
    sanya_g_skeleton_3.consts[1] = sanya_r_W_Fixnum(0);
    sanya_g_skeleton_3.cell_recipt = sanya_g_skeleton_cell_recipt_3;
    sanya_g_skeleton_3.nb_cells = 0;
    sanya_g_skeleton_3.closure_ptr = sanya_g_closure_ptr_3;
    sanya_g_skeleton_3.nb_args = 1;
    sanya_g_skeleton_3.varargs_p = 0;
    
    sanya_g_skeleton_4.name = "main";
    sanya_g_skeleton_4.consts = malloc(sizeof(intptr_t) * 5);
    sanya_g_skeleton_4.consts[0] = sanya_r_W_Fixnum(3);
    sanya_g_skeleton_4.consts[1] = sanya_r_W_Fixnum(2);
    sanya_g_skeleton_4.consts[2] = sanya_r_W_Fixnum(1);
    sanya_g_skeleton_4.consts[3] = sanya_r_W_Nil();
    sanya_g_skeleton_4.consts[4] = sanya_r_W_Fixnum(30);
    sanya_g_skeleton_4.cell_recipt = sanya_g_skeleton_cell_recipt_4;
    sanya_g_skeleton_4.nb_cells = 0;
    sanya_g_skeleton_4.closure_ptr = sanya_g_closure_ptr_4;
    sanya_g_skeleton_4.nb_args = 0;
    sanya_g_skeleton_4.varargs_p = 0;
    
    sanya_g_toplevel_consts = malloc(sizeof(intptr_t) * 4);
    sanya_g_toplevel_consts[0] = sanya_r_W_Unspecified();
    sanya_g_toplevel_consts[1] = sanya_r_W_Unspecified();
    sanya_g_toplevel_consts[2] = sanya_r_W_Unspecified();
    sanya_g_toplevel_consts[3] = sanya_r_W_Unspecified();
}

int
main(int argc, char **argv)
{
    sanya_r_initialize_prelude();  // @see sanya_prelude.*
    sanya_r_bootstrap();
    sanya_r_toplevel();
    return 0;
}

