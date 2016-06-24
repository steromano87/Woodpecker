import socket
import msgpack


class Messenger(object):

    def __init__(self, int_port, str_protocol,
                 int_max_pending_connections=None):
        # Inner socket object
        self._socket = None

        # Listening port
        self._port = int_port

        # Socket protocol
        self._protocol = str_protocol

        # Buffer size
        self._buffer_size = long(2 ** 30)

        # Socket connection (only for TCP connections)
        self._connection = None

        # Max pending connections (only for TCP connections)
        self._max_pending_connections = int_max_pending_connections

        # Last socket message
        self.message = None

        # Last remote address
        self.last_remote_address = None

    def _initialize_socket(self):
        if self._protocol == 'TCP':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.listen(self._max_pending_connections)
        elif self._protocol == 'UDP':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            raise Exception('Unsupported socket protocol')

        self._socket.bind(('', self._port))

    def listen(self):
        if self._protocol == 'TCP':
            self._connection, self.last_remote_address = \
                self._socket.accept()
            self.message = \
                msgpack.unpackb(self._connection.recv(self._buffer_size))
        elif self._protocol == 'UDP':
            self.message, self.last_remote_address = \
                self._socket.recvfrom(self._buffer_size)
            self.message = msgpack.unpackb(self.message)
        return self.message

    def send(self, tpl_address_port, str_msgtype, dic_data):
        dic_payload = {'type': str_msgtype, 'payload': dic_data}
        bin_payload = msgpack.packb(dic_payload)

        if self._protocol == 'TCP':
            self._socket.connect(tpl_address_port)
            int_sent_bytes = self._socket.sendall(bin_payload)
        elif self._protocol == 'UDP':
            int_sent_bytes = self._socket.sendto(bin_payload, tpl_address_port)
        else:
            int_sent_bytes = None

        return int_sent_bytes

    def reply(self, str_msgtype, dic_data):
        if self.last_remote_address:
            return self.send(self.last_remote_address, str_msgtype, dic_data)
        self.last_remote_address = None

    def __del__(self):
        if self._protocol == 'TCP':
            self._connection.close()
        self._socket.close()
