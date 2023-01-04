from copy import deepcopy

from easydict import EasyDict as EDict

from .common import UTF8, MessageABC, callable_operations, operations


class ServerMessage(MessageABC):
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
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def write(self):
        if self.message and not self._message_created:
            self.create_message()

        self._write()

    def create_message(self):
        "Create server response"
        ###

        operation = self.message.get("operation", "MISSING_OPERATION")

        if operation in operations.keys():
            op_kwargs = EDict(deepcopy(self.message))
            op_kwargs.pop("operation")

            server_response_msg = f"Calling: {operation}( "
            for k, v in op_kwargs.items():
                server_response_msg += f"{k}={v}, "
            server_response_msg += f")"

            return_msg = callable_operations[operation](op_kwargs)

            content = {"server_response": return_msg or ""}
            # content = {"server_response": server_response_msg}

        else:
            content = {
                "server_response": f"ERROR: invalid operation '{operation}' . Choose from{list(operations.keys())}."
            }

        ###

        response = {
            "content_bytes": self._json_encode(content, UTF8),
            "content_type": "text/json",
            "content_encoding": UTF8,
        }

        message = self._create_message(**response)
        self._message_created = True
        self._send_buffer += message

    def process_message(self):
        "Process client request"
        super().process_message()

        print(f"Received request: {self.message!r}")  # TODO: clean

        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")


# ENDFILE
