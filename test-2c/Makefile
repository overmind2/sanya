# automatically generated from .pymakegen_v2.conf
# timestamp: 1319343884.784842
# handler_namespaces: ['root', handler.gcc]

gcc_CC=gcc
gcc_CFLAGS=-flto -ggdb3 -O0 -Wall -Winline -Wwrite-strings  \
	    -Wno-unused -c
gcc_INCLUDES=-I./sanya_rt
gcc_LDFLAGS=-O0 -flto -fwhole-program -ggdb3 -lgc
gcc_TARGET=c-scheme2c-test

all : $(gcc_TARGET)

main.c : closure.scm
	../targetc.py --compile closure.scm > $@
	
$(gcc_TARGET) : main.o sanya_rt/func_defs.o
	$(gcc_CC) $(gcc_LDFLAGS) main.o sanya_rt/func_defs.o -o  \
	    $(gcc_TARGET)

main.o : main.c sanya_rt/func_decl.h sanya_rt/type_decl.h  \
	    sanya_rt/forward_decl.h
	$(gcc_CC) $(gcc_CFLAGS) main.c $(gcc_INCLUDES) -o main.o

sanya_rt/func_defs.o : sanya_rt/func_defs.c  \
	    sanya_rt/func_decl.h sanya_rt/type_decl.h  \
	    sanya_rt/forward_decl.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_rt/func_defs.c $(gcc_INCLUDES)  \
	    -o sanya_rt/func_defs.o

clean : 
	rm -rf main.o sanya_rt/func_defs.o
.PHONY : clean
