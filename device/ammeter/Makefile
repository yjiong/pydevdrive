.PHONY: clean
CC=gcc
CROSS_COMPLET=arm-linux-
CROSS_COMPLET_ARRCH64=aarch64-linux-
ARCH=
CFLAGS := -shared -g -O3 -fPIC -Wall
LDLIBS := 

TARGETS := des.so armdes.so arm64des.so

all: $(TARGETS)

clean:
		rm ${TARGETS}

des.so : des.c des.h
		$(CC) $(CFLAGS) -o $@ $^

armdes.so : des.c des.h
		$(CROSS_COMPLET)cc $(CFLAGS) -o $@ $^
		
arm64des.so : des.c des.h
		$(CROSS_COMPLET_ARRCH64)gnu-gcc $(CFLAGS) -o $@ $^
		
