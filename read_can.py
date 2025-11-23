#!/usr/bin/env python3
"""
Read CAN frames from interface 'can0' and print them to stdout.
Requires python-can.
"""

import sys
import can
import time

INTERFACE = "socketcan"
CHANNEL = "can0"
BITRATE = None  # not used when interface already configured

def format_msg(msg: can.Message) -> str:
    timestamp = f"{msg.timestamp:.6f}" if msg.timestamp is not None else ""
    id_str = f"{msg.arbitration_id:#x}"
    dlc = msg.dlc if msg.dlc is not None else len(msg.data or [])
    data = " ".join(f"{b:02x}" for b in msg.data) if msg.data else ""
    flags = []
    if msg.is_remote_frame:
        flags.append("RTR")
    if msg.is_error_frame:
        flags.append("ERR")
    if msg.is_extended_id:
        flags.append("EXT")
    flag_str = f"[{','.join(flags)}]" if flags else ""
    return f"{timestamp} ID={id_str} DLC={dlc} {flag_str} DATA={data}"

def main():
    try:
        bus = can.interface.Bus(channel=CHANNEL, bustype=INTERFACE)
    except Exception as e:
        print(f"Failed to open CAN interface {CHANNEL}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Listening on {CHANNEL} (press Ctrl-C to exit)...")
    try:
        while True:
            msg = bus.recv(timeout=1.0)  # seconds
            if msg is None:
                continue
            print(format_msg(msg))
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        try:
            bus.shutdown()
        except Exception:
            pass

if __name__ == "__main__":
    main()
