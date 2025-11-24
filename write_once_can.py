#!/usr/bin/env python3
import os
import can
import time

INTERFACE = "socketcan"
CAN_NETWORK_INTERFACE = os.getenv("CAN_NETWORK_INTERFACE", "can0")


def send_once(arbitration_id=0x123, data=b"\xde\xad\xbe\xef", extended_id=False):
    bus = can.interface.Bus(channel=CAN_NETWORK_INTERFACE, interface=INTERFACE)
    msg = can.Message(
        arbitration_id=arbitration_id, data=data, is_extended_id=extended_id
    )
    try:
        bus.send(msg, timeout=1.0)
        print(f"Sent ID=0x{arbitration_id:X} len={len(data)} data={data.hex()}")
    except can.CanError as e:
        print("Send failed:", e)
    finally:
        bus.shutdown()


if __name__ == "__main__":
    send_once(
        0x00B,
        bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD]),
        extended_id=False,
    )
