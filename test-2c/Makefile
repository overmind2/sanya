# automatically generated from .pymakegen_v2.conf
# timestamp: 1319286505.444124
# handler_namespaces: ['root', handler.gcc]

gcc_CC=gcc
gcc_CFLAGS=-ggdb3 -O0 -Wall -Winline -Wwrite-strings  \
	    -Wno-unused -c
gcc_INCLUDES=-I./
gcc_LDFLAGS=-O1 -ggdb3
gcc_TARGET=test-2c

all : $(gcc_TARGET)
	
$(gcc_TARGET) : main.o sanya_obj.o
	$(gcc_CC) $(gcc_LDFLAGS) main.o sanya_obj.o -o $(gcc_TARGET)

main.o : main.c sanya_c.h sanya_obj.h sanya_c.h
	$(gcc_CC) $(gcc_CFLAGS) main.c $(gcc_INCLUDES) -o main.o

sanya_obj.o : sanya_obj.c sanya_obj.h sanya_c.h
	$(gcc_CC) $(gcc_CFLAGS) sanya_obj.c $(gcc_INCLUDES) -o  \
	    sanya_obj.o

clean : 
	rm -rf main.o sanya_obj.o
.PHONY : clean
