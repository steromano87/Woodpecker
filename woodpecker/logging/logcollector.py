import msgpack
import socket
import os

from woodpecker.logging.dbwriter import DBWriter
from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.options import Options


class LogCollector(StoppableThread):

    def __init__(self, **kwargs):
        super(LogCollector, self).__init__()

        # Scenario folder
        self._scenario_folder = kwargs.get('scenario_folder', os.getcwd())

        # Options
        self._options = kwargs.get('options', Options())

        # Results file name
        self._results_file = '.'.join((
            kwargs.get('results_file',
                       '/'.join((self._scenario_folder, 'results', 'results'))),
            'sqlite'
        ))

        # Internal DBWriter
        self._dbwriter = DBWriter(self._results_file)

        # Listening socket
        self._socket = socket.socket()

        # Socket setup
        if self._options.get('logging', 'logger_protocol') == 'TCP':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif self._options.get('logging', 'logger_protocol') == 'UDP':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._socket_listening_port = self._options.get('logging',
                                                        'logger_port')
        self._socket_connection = None
        self._socket_remote_address = None
        self._socket_data = None
        self._socket_buffer_size = long(2 ** 30)

        # Bind socket and start listening
        self._socket.bind(('', self._socket_listening_port))
        self._socket.listen(
            self._options.get('logging',
                              'logger_socket_max_pending_connections')
        )

    def _handle_data(self):
        self.message = msgpack.unpackb(self._socket_data)
        for str_section, lst_data in self.message['payload'].iteritems():
            if len(lst_data) > 0:
                self._dbwriter.insert_in_section(str_section, lst_data)

    def run(self):
        # Run until marked for stop
        while True:
            if not self.is_marked_for_stop:
                self._socket_connection, \
                    self._socket_remote_address = self._socket.accept()
                # Correct the controller IP address
                self._socket_remote_address = \
                    self._socket_remote_address[0]
                self._socket_data = self._socket_connection.recv(
                    self._socket_buffer_size
                )
                self._handle_data()
            else:
                self._socket_connection.close()
                break
