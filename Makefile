SHELL := /bin/bash

VENV := venv
SLCAN_DEV ?= /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.1.1:1.0
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
read $(VENV):
	$(VENV)/bin/python read_can.py

.PHONY: write-sample
write-sample: $(VENV)
	$(VENV)/bin/python write_once_can.py
