SHELL := /bin/bash

VENV := venv
SLCAN_DEV ?= /dev/serial/by-path/pci-0000:00:14.0-usb-0:2.1.1:1.0
CAN_NETWORK_INTERFACE ?= can0
SLCAN_BIN := /bin/slcand

export

.PHONY: default
default: read

$(SLCAN_BIN):
	sudo apt install can-utils

$(VENV):
	python3 -m venv $(VENV); \
	$(VENV)/bin/pip install -r requirements.txt

.PHONY: $(CAN_NETWORK_INTERFACE)
$(CAN_NETWORK_INTERFACE): $(SLCAN_BIN)
	sudo $(SLCAN_BIN) -f -o -c -s5 $(SLCAN_DEV) $@; \
	sudo ip link set up $@;

.PHONY: read
read $(VENV) $(CAN_NETWORK_INTERFACE):
	$(VENV)/bin/python read_can.py

.PHONY: read-async
read-async $(VENV) $(CAN_NETWORK_INTERFACE):
	$(VENV)/bin/python read_can_async.py

.PHONY: write-sample
write-sample: $(VENV) $(CAN_NETWORK_INTERFACE)
	$(VENV)/bin/python write_once_can.py


.PHONY: canopen-scan
canopen-scan: $(VENV) $(CAN_NETWORK_INTERFACE)
	$(VENV)/bin/python canopen_scan.py
