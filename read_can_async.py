#!/usr/bin/env python3
"""
Async read of CAN frames from 'can0' and print to stdout.
Requires python-can with asyncio support.
"""

import os
import sys
import can
import asyncio

INTERFACE = "socketcan"
CAN_NETWORK_INTERFACE = os.getenv("CAN_NETWORK_INTERFACE", "can0")
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


async def read_loop(bus: can.BusABC):
    reader = can.AsyncBufferedReader()
    notifier = can.Notifier(bus, [reader], loop=asyncio.get_running_loop())
    print(f"Listening on {CAN_NETWORK_INTERFACE} (press Ctrl-C to exit)...")
    try:
        while True:
            msg = await reader.get_message()  # waits until a message arrives
            if msg is None:
                continue
            print(format_msg(msg))
    except asyncio.CancelledError:
        pass
    finally:
        notifier.stop()
        try:
            bus.shutdown()
        except Exception:
            pass


async def main():
    try:
        bus = can.interface.Bus(channel=CAN_NETWORK_INTERFACE, interface=INTERFACE)
    except Exception as e:
        print(
            f"Failed to open CAN interface {CAN_NETWORK_INTERFACE}: {e}",
            file=sys.stderr,
        )
        return
    task = asyncio.create_task(read_loop(bus))
    try:
        await task
    except KeyboardInterrupt:
        task.cancel()
        await task


if __name__ == "__main__":
    asyncio.run(main())
