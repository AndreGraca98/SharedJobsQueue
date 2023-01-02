import selectors
from socket import socket
from typing import Any, Dict

try:
    from .common import UTF8, MessageABC
except ModuleNotFoundError:
    from common import UTF8, MessageABC


class ClientMessage(MessageABC):
    def __init__(
        self,
        selector: selectors.BaseSelector,
        sock: socket,
        request: Dict[str, Any],
        verbose: bool = False,
    ):
        super().__init__(selector=selector, sock=sock, verbose=verbose)
        self.message_request = request

    def _write(self):
        if self._send_buffer:
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def write(self):
        if not self._message_created:
            self.create_message()

        self._write()

        if self._message_created and not self._send_buffer:
            # Set selector to listen for read events, we're done writing.
            self._set_selector_events_mask("r")

    def create_message(self):
        "Send client request"

        req = {
            "content_bytes": self._json_encode(self.message_request, UTF8),
            "content_type": "text/json",
            "content_encoding": UTF8,
        }

        message = self._create_message(**req)
        self._send_buffer += message
        self._message_created = True

    def process_message(self):
        "Process server response"
        super().process_message()

        content = self.message

        result = content.get("server_response")
        print(result)

        # print(f"Got result: {result}")

        # Close when response has been processed
        self.close()


# ENDFILE
