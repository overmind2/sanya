# automatically generated from .pymakegen_v2.conf
# timestamp: 1319336998.325219
# handler_namespaces: ['root', handler.gcc]

gcc_CC=gcc
gcc_CFLAGS=-ggdb3 -O3 -Wall -Winline -Wwrite-strings  \
	    -Wno-unused -c -pg
gcc_INCLUDES=-I./sanya_rt
gcc_LDFLAGS=-O3 -ggdb3 -pg
gcc_TARGET=c-scheme2c-test

all : $(gcc_TARGET)

main.c : closure.scm
	../targetc.py --compile closure.scm > main.c

dis :
	../targetc.py --dis closure.scm | less
	
$(gcc_TARGET) : main.o sanya_rt/sanya_runtime.o  \
	    sanya_rt/sanya_prelude.o sanya_rt/sanya_object.o
	$(gcc_CC) $(gcc_LDFLAGS) main.o sanya_rt/sanya_runtime.o  \
	    sanya_rt/sanya_prelude.o sanya_rt/sanya_object.o -o  \
	    $(gcc_TARGET)

main.o : main.c sanya_rt/sanya_object.h  \
	    sanya_rt/sanya_runtime.h sanya_rt/sanya_prelude.h  \
	    sanya_rt/sanya_runtime.h sanya_rt/sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) main.c $(gcc_INCLUDES) -o main.o

sanya_rt/sanya_object.o : sanya_rt/sanya_object.c  \
	    sanya_rt/sanya_object.h sanya_rt/sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_rt/sanya_object.c  \
	    $(gcc_INCLUDES) -o sanya_rt/sanya_object.o

sanya_rt/sanya_prelude.o : sanya_rt/sanya_prelude.c  \
	    sanya_rt/sanya_prelude.h sanya_rt/sanya_object.h  \
	    sanya_rt/sanya_runtime.h sanya_rt/sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_rt/sanya_prelude.c  \
	    $(gcc_INCLUDES) -o sanya_rt/sanya_prelude.o

sanya_rt/sanya_runtime.o : sanya_rt/sanya_runtime.c  \
	    sanya_rt/sanya_object.h sanya_rt/sanya_runtime.h  \
	    sanya_rt/sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_rt/sanya_runtime.c  \
	    $(gcc_INCLUDES) -o sanya_rt/sanya_runtime.o

clean : 
	rm -rf main.o sanya_rt/sanya_runtime.o  \
	    sanya_rt/sanya_prelude.o sanya_rt/sanya_object.o
.PHONY : clean
