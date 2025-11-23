SHELL := /bin/bash

VENV := venv
SLCAN_DEV ?= /dev/ttyACM0
SLCAN_BIN := /bin/slcand

.PHONY: default
default: $(VENV)
	@echo "This is the default target."

$(SLCAN_BIN):
	sudo apt install can-utils

$(VENV):
	python3 -m venv $(VENV); \
	$(VENV)/bin/pip install -r requirements.txt

.PHONY: can0
can0: $(SLCAN_BIN)
	sudo $(SLCAN_BIN) -f -o -c -s5 $(SLCAN_DEV) $@; \
	sudo ip link set up $@;

.PHONY: read
read:
	$(VENV)/bin/python read_can.py
