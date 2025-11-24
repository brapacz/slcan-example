#!/usr/bin/env python3
import os
import time
import canopen
import logging

logging.basicConfig(level=logging.INFO)

CAN_NETWORK_INTERFACE = os.getenv("CAN_NETWORK_INTERFACE", "can0")
BITRATE = None  # not required when using existing kernel interface
SCAN_NODE_IDS = range(1, 128)  # 1..127


def probe_node(network, node_id, timeout=1.0):
    try:
        # Add a temporary node without EDS file
        node = canopen.RemoteNode(node_id, None)
        network.add_node_object(node)  # internal attach for probing
        # try to read some common SDO entries
        info = {"node_id": node_id}
        try:
            # Attempt simple SDO read: device type (0x1000), vendor id (0x1018 sub 1), product code (0x1018 sub 2)
            info["device_type"] = node.sdo[0x1000].raw if 0x1000 in node.sdo else None
        except Exception:
            info["device_type"] = None
        try:
            info["vendor_id"] = node.sdo[0x1018][1].raw
            info["product_code"] = node.sdo[0x1018][2].raw
            info["revision"] = node.sdo[0x1018][3].raw
            info["serial_number"] = node.sdo[0x1018][4].raw
        except Exception:
            # try alternative common indices
            info.setdefault("vendor_id", None)
            info.setdefault("product_code", None)
            info.setdefault("revision", None)
            info.setdefault("serial_number", None)
        # Clean up
        network.remove_node_object(node)
        return info
    except canopen.SdoAbortedError:
        network.remove_node_object(node)
        return None
    except Exception:
        try:
            network.remove_node_object(node)
        except Exception:
            pass
        return None


def main():
    network = canopen.Network()
    network.connect(channel=CAN_NETWORK_INTERFACE, bustype="socketcan", bitrate=BITRATE)
    found = []
    # Use NMT master heartbeat query: try sending NMT start then check for SDO responses
    # Simple probe by addressing each node ID
    for nid in SCAN_NODE_IDS:
        logging.info("Probing node %d...", nid)
        try:
            # Try to read SDO (will time out if node not present)
            info = probe_node(network, nid, timeout=1.0)
            if info:
                found.append(info)
                logging.info("Found node %d: %s", nid, info)
        except Exception as e:
            logging.debug("Probe %d error: %s", nid, e)
        # small delay to avoid flooding
        time.sleep(0.02)

    # Print summary
    if not found:
        print("No CANopen nodes discovered on", CAN_NETWORK_INTERFACE)
    else:
        print("Discovered CANopen nodes:")
        print(
            "{:<8} {:<12} {:<12} {:<12} {:<12}".format(
                "Node ID", "Vendor ID", "Product", "Revision", "Serial"
            )
        )
        for i in found:
            print(
                "{:<8} {:<12} {:<12} {:<12} {:<12}".format(
                    i.get("node_id"),
                    str(i.get("vendor_id") or ""),
                    str(i.get("product_code") or ""),
                    str(i.get("revision") or ""),
                    str(i.get("serial_number") or ""),
                )
            )
    network.disconnect()


if __name__ == "__main__":
    main()
