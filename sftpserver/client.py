#!/usr/bin/env python3

import selectors
import socket
from typing import Any, Dict

try:
    from .args import get_client_parser
    from .common import HOST, PORT
    from .libclient import ClientMessage
except ModuleNotFoundError:
    from args import get_client_parser
    from common import HOST, PORT
    from libclient import ClientMessage


def start_connection(sel, request: Dict[str, Any]):
    addr = (HOST, PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = ClientMessage(selector=sel, sock=sock, request=request)
    sel.register(sock, events, data=message)


def process(sel):
    events = sel.select(timeout=1)
    for key, mask in events:
        message = key.data
        message.process_events(mask)


def main():
    args = get_client_parser().parse_args()

    sel = selectors.DefaultSelector()

    start_connection(sel, request=dict(args._get_kwargs()))

    try:
        while True:
            process(sel)
            if not sel.get_map():  # Check for a socket being monitored
                break
    except KeyboardInterrupt:
        print("\r" + "Caught keyboard interrupt, exiting".center(80, "-"))
    finally:
        sel.close()


if __name__ == "__main__":
    main()
