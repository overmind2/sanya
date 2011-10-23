#ifndef SANYA_PRELUDE_H
#define SANYA_PRELUDE_H

#include "sanya_runtime.h"
#include "sanya_object.h"

// in main.c as well.
void sanya_r_initialize_prelude();

// Display.
intptr_t sanya_p_display(sanya_t_Object *ls_closure, intptr_t ls_arg1);


#endif /* SANYA_PRELUDE_H */
