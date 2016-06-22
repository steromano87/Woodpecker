import os
import socket
import msgpack
import importlib
import tempfile
import shutil

import woodpecker.misc.utils as utils

from zipfile import ZipFile
from StringIO import StringIO

from woodpecker.options import Options
from woodpecker.logging.log import Log
from woodpecker.logging.sysmonitor import Sysmonitor
from woodpecker.controllers.spawner import Spawner


class SpawnerController(object):

    def __init__(self, **kwargs):
        # Options file
        self._options = kwargs.get('options', Options())

        # Logger
        self._log = kwargs.get('log', Log())

        # Sysmonitor
        self._sysmonitor = Sysmonitor('spawner')

        # Spawner
        self._spawner = Spawner()

        # Flag for starting/stoppping
        self.is_marked_for_stop = False

        # Socket data
        self._socket = None
        self._socket_listening_port = self._options.get('execution', 'controller_port')
        self._socket_connection = None
        self._socket_controller_address = None
        self._socket_data = None
        self._socket_buffer_size = long(2 ** 30)

        # Message from socket
        self.message = None

        # Scenario data (AKA working dir)
        self.scenario_folder = None

        # Socket setup
        if self._options.get('execution', 'controller_protocol') == 'TCP':
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif self._options.get('execution', 'controller_protocol') == 'UDP':
            pass

        # Bind socket and start listening
        self._socket.bind(('', self._socket_listening_port))
        self._socket.listen(self._options.get('execution', 'controller_socket_max_pending_connections'))

    def run(self):
        # Run until marked for stop
        while True:
            if not self.is_marked_for_stop:
                self._socket_connection, self._socket_controller_address = self._socket.accept()
                # Correct the controller IP address
                self._socket_controller_address = self._socket_controller_address[0]
                self._socket_data = self._socket_connection.recv(self._socket_buffer_size)
                self.handle_data()
            else:
                self._socket_connection.close()
                break

    def handle_data(self):
        self.message = msgpack.unpackb(self._socket_data)

        # Execute different actions based upon message type
        if self.message['type'] == 'command':
            self._handle_command()
        elif self.message['type'] == 'notice':
            pass

    def _handle_command(self):
        dic_payload = self.message['payload']

        # Allowed actions
        if dic_payload['command'] == 'scenario_unpack':
            self._scenario_unpack(dic_payload['data'])
        elif dic_payload['command'] == 'scenario_setup':
            self._scenario_setup(dic_payload['data'])
        elif dic_payload['command'] == 'start':
            self._start()
        elif dic_payload['command'] == 'stop':
            self._stop()
        elif dic_payload['command'] == 'emergency_stop':
            pass
        elif dic_payload['command'] == 'shutdown':
            self._shutdown()

    def _scenario_unpack(self, dic_data):
        # Get zipped scenario folder
        obj_scenario_zipped_folder = StringIO(dic_data['compressed_scenario_folder'])
        obj_zipfile = ZipFile(obj_scenario_zipped_folder, 'r')

        # Extract the zipped folder into temp folder
        self.scenario_folder = tempfile.mkdtemp(prefix='woodpecker-')
        obj_zipfile.extractall(self.scenario_folder)

    def _scenario_setup(self, dic_data):
        # Change current dir to scenario folder
        os.chdir(self.scenario_folder)
        obj_scenario = getattr(importlib.import_module('scenario'), dic_data['scenario_name'])()

        # Get rescale ratio and resize the whole pecker pool accordingly
        dbl_rescale_ratio = dic_data['rescale_ratio']
        obj_scenario.rescale_by_ratio(dbl_rescale_ratio)

        # Assign scenario to spawner
        self._spawner.attach_scenario(obj_scenario)

    def _start(self):
        self._sysmonitor.start()
        self._spawner.start()

    def _stop(self):
        self._sysmonitor.mark_for_stop()
        self._spawner.mark_for_stop()

    def _shutdown(self):
        self._stop()
        self._log.flush()
        self.is_marked_for_stop = True

    def __del__(self):
        if self.scenario_folder and os.path.isdir(self.scenario_folder):
            shutil.rmtree(self.scenario_folder)
