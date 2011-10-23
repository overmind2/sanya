
#include <inttypes.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#define SANYA_T_FIXNUM  1
#define SANYA_T_UNSPEC  2
#define SANYA_T_NIL     3
#define SANYA_T_BOOLEAN 4
#define SANYA_T_SYMBOL  16
#define SANYA_T_PAIR    17
#define SANYA_T_CLOSURE 18

#define SANYA_R_TAGWIDTH  4
#define SANYA_R_TAGMASK  15

struct sanya_t_ClosureSkeleton_;
struct sanya_t_CellValue_;
struct sanya_t_Object_;
struct sanya_t_TrampolineBuf_;

typedef struct sanya_t_ClosureSkeleton_ sanya_t_ClosureSkeleton;
typedef struct sanya_t_CellValue_ sanya_t_CellValue;
typedef struct sanya_t_Object_ sanya_t_Object;
typedef struct sanya_t_TrampolineBuf_ sanya_t_TrampolineBuf;

