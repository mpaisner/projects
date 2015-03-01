

CC=g++
CFLAGS=-I/usr/include/python2.7 -lpython2.7

all: cCode

cCode: cCode.o
	$(CC) $(CFLAGS) cCode.o -o cCode
	
cCode.o: cCode.cpp
	$(CC) $(CFLAGS) -c cCode.cpp

clean:
	rm -rf *o cCode