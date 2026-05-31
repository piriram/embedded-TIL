CC      ?= cc
CFLAGS  ?= -O2 -Wall -Wextra -std=c11
BIN      = algo_test

SRC = sim_main.c algorithm.c
HDR = algorithm.h

all: $(BIN)

$(BIN): $(SRC) $(HDR)
	$(CC) $(CFLAGS) -o $@ $(SRC)

gen:
	python3 sim.py

test: $(BIN) gen
	python3 test_runner.py

clean:
	rm -f $(BIN) cases/*.csv

.PHONY: all gen test clean
