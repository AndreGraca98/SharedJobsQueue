#!/usr/bin/env python3

import datetime
import selectors
import socket
import traceback

from .common import HOST, PORT
from .lib_smtp_server import ServerMessage


def accept_wrapper(sel, conn):
    sock, addr = conn.accept()  # Should be ready to read
    print(
        f"= Accepted connection from: host={addr[0]}, port={addr[1]} =".center(80, "=")
    )
    print(str(datetime.datetime.now()).center(80))
    sock.setblocking(False)
    message = ServerMessage(selector=sel, sock=sock, verbose=True)
    sel.register(sock, selectors.EVENT_READ, data=message)


def process(sel):
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            accept_wrapper(sel, key.fileobj)
            continue

        message = key.data
        try:
            message.process_events(mask)
        except Exception:
            print(f"\n{'- ERROR -':-^80}")
            print(traceback.format_exc())
            print(f"{'':-^80}\n")

            message.close()


def start_connection(sel):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        lsock.bind((HOST, PORT))
    except OSError as e:
        print("ERROR:", e.strerror, f"( host={HOST}, port={PORT} )")
        exit(1)

    lsock.listen(0)
    print(f"# Listening on: host={HOST}, port={PORT} #".center(80, "#"))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)


def main():
    sel = selectors.DefaultSelector()

    start_connection(sel)

    try:
        while True:
            process(sel)
    except KeyboardInterrupt:
        print("\r" + "# Shutting down #".center(80, "#"))
    finally:
        sel.close()


if __name__ == "__main__":
    main()
