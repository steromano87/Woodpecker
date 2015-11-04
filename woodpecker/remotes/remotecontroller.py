import SocketServer
import json
import base64
import tempfile
import os

import woodpecker.misc.utils as utils

from zipfile import ZipFile
from StringIO import StringIO

from woodpecker.remotes.spawner import Spawner
from woodpecker.remotes.sysmonitor import Sysmonitor

__author__ = 'romano'


class RemoteController(SocketServer.StreamRequestHandler):

    def __init__(self, request, client_address, server):
        # Init method of the father class
        SocketServer.StreamRequestHandler.__init__(self, request, client_address, server)

        # Placeholder for scenario folder
        if not self.scenario_folder:
            self.scenario_folder = None

        # Placeholder for scenario file
        if not self.scenario_file_path:
            self.scenario_file_path= None

        # Placeholder for scenario name
        if not self.scenario_name:
            self.scenario_name= None

        # Placeholder for scenario results file path
        if not self.results_file_path:
            self.results_file_path= None

        # Placeholder for controller IP address
        if not self.controller_ip_address:
            self.controller_ip_address= None

        # Standard port, this value will be eventually overridden
        if not self.controller_port:
            self.controller_port= 7878

        # Spawn quota for local spawner
        if not self.spawn_quota:
            self.spawn_quota= None

        # Spawner object
        if not self.spawner:
            self.spawner = None

        # Sysmonitor object
        if not self.sysmonitor:
            self.sysmonitor= None

        return

    def handle(self):
        # Read the messages and parse them into dict
        str_message = self.rfile.readline().strip()
        obj_message = json.loads(str_message)

        # Switch action according to message type
        if obj_message['dataType'] == 'start':
            self.__initialize(obj_message['payload'])
            self.__start_scenario()
        elif obj_message['dataType'] == 'stop':
            pass
        elif obj_message['dataType'] == 'emergency_stop':
            pass
        elif obj_message['dataType'] == 'shutdown':
            self.server.shutdown()
            self.server.server_close()

    def __initialize(self, dic_payload):
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

    def __start_scenario(self):
        self.spawner = Spawner(self.controller_ip_address,
                               self.controller_port,
                               self.scenario_folder,
                               self.scenario_name,
                               self.scenario_file_path,
                               self.results_file_path,
                               self.spawn_quota)

if __name__ == '__main__':
    obj_server = SocketServer.TCPServer(('localhost', 7878), RemoteController)
    obj_server.serve_forever()
