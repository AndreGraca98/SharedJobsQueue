import io
import json
import selectors
import struct
import sys
from abc import ABC, abstractmethod
from socket import socket

from easydict import EasyDict as EDict

HOST: str = "127.0.0.1"
PORT: int = 65432
UTF8: str = "utf-8"

operations = EDict(
    show="show",
    add="add",
    remove="remove",
    update="update",
    pause="pause",
    resume="resume",
    clear="clear",
    clear_state="clear_state",
    kill="kill",
    retry="retry",
    info="info",
)


try:
    from .jobs_table import JobsTable, kills, not_implemented, show_info

    callable_operations = dict(
        show=JobsTable.show,
        add=JobsTable.add,
        remove=JobsTable.remove,
        update=JobsTable.update,
        pause=JobsTable.pause,
        resume=JobsTable.resume,
        clear=JobsTable.clear,
        clear_state=JobsTable.clear_state,
        kill=kills,
        retry=JobsTable.retry,
        # retry=not_implemented,
        info=show_info,
    )
    assert callable_operations.keys() == operations.keys()

except TypeError:  # Lock mechanism
    ...


class MessageABC(ABC):
    def __init__(
        self, selector: selectors.BaseSelector, sock: socket, verbose: bool = False
    ) -> None:
        self.selector = selector
        self.sock = sock
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.message = None
        self._message_created = False
        self.verbose = verbose

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {mode!r}.")
        self.selector.modify(self.sock, events, data=self)

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding, **kwargs
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader.update(kwargs)

        jsonheader_bytes = self._json_encode(jsonheader, UTF8)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    @abstractmethod
    def create_message(self):
        ...

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.message is None:
                self.process_message()

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(int(2**15))
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        except ConnectionRefusedError:
            print(f"ERROR: Connection to peer unavailable...")
            exit(1)
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("ERROR: Peer closed...")

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[:hdrlen], UTF8)
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f"Missing required header '{reqhdr}'.")

    def process_message(self):
        "NOTE: Expected to be used as super().process_message() in subclass"
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return

        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]

        self.message = self._json_decode(data, UTF8)

    @abstractmethod
    def write(self):
        ...

    @abstractmethod
    def _write(self):
        ...

    def close(self):
        host, port = self.sock.getpeername()

        if self.verbose:
            print(
                "\r"
                + f"= Closing connection to: host={host}, port={port} =".center(80, "=")
            )
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(f"ERROR: selector.unregister() exception : {e!r}")

        try:
            self.sock.close()
        except OSError as e:
            print(f"ERROR: socket.close() exception : {e!r}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None


# ENDFILE
