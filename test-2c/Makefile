# automatically generated from .pymakegen_v2.conf
# timestamp: 1319290542.78507
# handler_namespaces: ['root', handler.gcc]

gcc_CC=gcc
gcc_CFLAGS=-ggdb3 -O0 -Wall -Winline -Wwrite-strings  \
	    -Wno-unused -c
gcc_INCLUDES=-I./
gcc_LDFLAGS=-O1 -ggdb3
gcc_TARGET=c-scheme2c-test

all : $(gcc_TARGET)
	
$(gcc_TARGET) : sanya_runtime.o main.o sanya_prelude.o  \
	    sanya_object.o
	$(gcc_CC) $(gcc_LDFLAGS) sanya_runtime.o main.o  \
	    sanya_prelude.o sanya_object.o -o $(gcc_TARGET)

main.o : main.c sanya_object.h sanya_runtime.h sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) main.c $(gcc_INCLUDES) -o main.o

sanya_object.o : sanya_object.c sanya_object.h sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_object.c $(gcc_INCLUDES) -o  \
	    sanya_object.o

sanya_prelude.o : sanya_prelude.c sanya_prelude.h  \
	    sanya_object.h sanya_runtime.h sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_prelude.c $(gcc_INCLUDES) -o  \
	    sanya_prelude.o

sanya_runtime.o : sanya_runtime.c sanya_object.h  \
	    sanya_runtime.h sanya_runtime.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_runtime.c $(gcc_INCLUDES) -o  \
	    sanya_runtime.o

clean : 
	rm -rf sanya_runtime.o main.o sanya_prelude.o sanya_object.o
.PHONY : clean
