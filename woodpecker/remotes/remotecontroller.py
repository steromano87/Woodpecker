import socket
import json
import base64
import tempfile
import click

import woodpecker.misc.utils as utils

from zipfile import ZipFile
from StringIO import StringIO

from woodpecker.remotes.spawner import Spawner
from woodpecker.remotes.sysmonitor import Sysmonitor

__author__ = 'romano'


class RemoteController(object):

    def __init__(self, int_listening_port):
        # Socket properties
        self.socket = None
        self.active = True
        self.connection = None
        self.client_address = None
        self.data = None
        self.buffer_size = 2 ** 20

        # Placeholder for scenario folder
        self.scenario_folder = None

        # Placeholder for scenario file
        self.scenario_file_path = None

        # Placeholder for scenario name
        self.scenario_name = None

        # Placeholder for scenario results file path
        self.results_file_path = None

        # Placeholder for controller IP address
        self.controller_ip_address = None

        # Standard port, this value will be eventually overridden
        self.controller_port = 7878

        # Spawn quota for local spawner
        self.spawn_quota = None

        # Spawner object
        self.spawner = None

        # Sysmonitor object
        self.sysmonitor = None

        # Initialize the socket
        self.__initialize(int_listening_port)

        return

    def __initialize(self, int_listening_port):
        # Initialize socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listening_port = int_listening_port

        self.socket.bind(('', self.listening_port))
        self.socket.listen(3)

        # Print message on screen
        str_message = ' '.join(('Socket opened on port', str(self.listening_port)))
        click.echo(str_message)

    def __handle(self):
        # Read the messages and parse them into dict
        obj_message = json.loads(self.data)

        # Switch action according to message type
        if obj_message['dataType'] == 'setup':
            self.__setup_scenario(obj_message['payload'])
        elif obj_message['dataType'] == 'start':
            self.__start_scenario()
        elif obj_message['dataType'] == 'stop':
            pass
        elif obj_message['dataType'] == 'emergency_stop':
            pass
        elif obj_message['dataType'] == 'shutdown':
            self.shutdown()

    def __setup_scenario(self, dic_payload):
        # Get the Base64 encoded ZIP file from payload
        str_base64_zipped_scenario = dic_payload['scenarioBase64ZippedFolder']
        obj_zipped_scenario = StringIO(base64.b64decode(str_base64_zipped_scenario))
        obj_zipfile = ZipFile(obj_zipped_scenario, 'r')

        # Extract  ZIP file into temporary folder
        self.scenario_folder = tempfile.mkdtemp(prefix='woodpecker-')
        obj_zipfile.extractall(self.scenario_folder)

        # Fill all the object properties
        self.controller_ip_address = dic_payload.get('controllerIPAddress', 'localhost')
        self.controller_port = dic_payload.get('controllerPort', '7878')
        self.spawn_quota = dic_payload.get('spawnQuota', 1)
        self.scenario_name = dic_payload.get('scenarioName', 'Scenario')
        self.scenario_file_path = utils.get_abs_path(dic_payload.get('scenarioFile', './scenario.py'),
                                                     self.scenario_folder)
        self.results_file_path = utils.get_abs_path(dic_payload.get('resultsFile', './results/results.sqlite'),
                                                    self.scenario_folder)

        # Create Sysmonitor
        self.sysmonitor = Sysmonitor(self.controller_ip_address, self.controller_port)

    def __start_scenario(self):
        self.spawner = Spawner(self.controller_ip_address,
                               self.controller_port,
                               self.scenario_folder,
                               self.scenario_name,
                               self.scenario_file_path,
                               self.results_file_path,
                               self.spawn_quota)

    def serve_forever(self):
        click.secho('Waiting for controller connection...', fg='green', bold=True)
        while self.active:
            self.connection, self.client_address = self.socket.accept()
            self.data = self.connection.recv(self.buffer_size)
            self.__handle()

        self.connection.close()

    def shutdown(self):
        str_message = ' '.join(('Remote controller gracefully closed by controller on', self.client_address))
        click.echo(str_message)
        self.active = False

if __name__ == '__main__':
    obj_server = RemoteController(7878)
    obj_server.serve_forever()
