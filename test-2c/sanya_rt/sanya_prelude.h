#ifndef SANYA_PRELUDE_H
#define SANYA_PRELUDE_H

#include "sanya_runtime.h"
#include "sanya_object.h"

extern intptr_t sanya_g_prelude_display;
extern intptr_t sanya_g_prelude_newline;
extern intptr_t sanya_g_prelude_add;
extern intptr_t sanya_g_prelude_lessthan;
extern intptr_t sanya_g_prelude_num_eq;

// exposed
void sanya_r_initialize_prelude();

#endif /* SANYA_PRELUDE_H */
