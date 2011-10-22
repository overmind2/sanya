#ifndef SANYA_PRELUDE_H
#define SANYA_PRELUDE_H

#include "sanya_runtime.h"
#include "sanya_object.h"

// in main.c as well.
void sanya_r_initialize_prelude();

// Display.
void sanya_p_display(intptr_t *ls_retval, sanya_t_Object *ls_closure,
                     intptr_t ls_nb_args, ...);


#endif /* SANYA_PRELUDE_H */
