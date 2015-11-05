from __future__ import division
import base64
import os

from zipfile import ZipFile
from StringIO import StringIO

from woodpecker.remotes.sysmonitor import Sysmonitor
from woodpecker.logging.sender import Sender
from woodpecker.logging.logcollector import LogCollector
import woodpecker.misc.utils as utils

__author__ = 'Stefano.Romano'


class Controller(object):

    def __init__(self, str_scenario_name, **kwargs):
        self.__initialize(str_scenario_name, **kwargs)

    def __enter__(self, str_scenario_name, **kwargs):
        self.__initialize(str_scenario_name, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        pass

    def __initialize(self, str_scenario_name, **kwargs):
        # IP addresses and ports
        self.controller_ip_addr = utils.get_ip_address()
        self.port = kwargs.get('port', 7878)

        # Allocate an empty dict to collect spawners data
        self.spawners = {}
        list_spawners = kwargs.get('spawners', ['localhost'])
        for str_spawner in list_spawners:
            self.spawners[str_spawner] = {}

            # Create a sender for each spawner
            self.spawners[str_spawner]['sender'] = Sender(str_spawner, self.port, 'TCP')

        # Spawning mode (threads or subprocesses), defaults to threads
        self.spawn_mode = kwargs.get('spawn_mode', 'thread')

        # Local flag to run everything on localhost (to nbe used in the future...), defaults to False
        self.local = kwargs.get('local', False)

        # Placeholder for scenario
        self.scenario = None

        # Scenario class name
        self.scenario_name = str_scenario_name

        # Scenario folder
        self.scenario_folder = utils.get_abs_path(kwargs.get('scenario_folder',  os.getcwd()))

        # Scenario file, defaults to 'scenario.py'
        self.scenario_file = kwargs.get('scenario_file_path', './scenario.py')

        # Scenario file path, defaults to standard scenario file
        self.scenario_file_path = utils.get_abs_path(self.scenario_file, self.scenario_folder)

        # Result file, defaults to 'results/results.sqlite' file
        self.results_file = kwargs.get('results_file', './results/results.sqlite')

        # Result file path
        self.results_file_path = utils.get_abs_path(self.results_file, self.scenario_folder)

    def __load_scenario(self):
        # Get scenario from path and name
        self.scenario = utils.import_from_path(self.scenario_file_path, self.scenario_name,
                                               {'scenario_folder': self.scenario_folder})

        # Load tests
        self.scenario.tests_definition()

    def __scale_ramps(self):
        # Get spawners number
        int_spawners_num = len(self.spawners)
        int_max_spawns = self.scenario.get_max_scenario_spawns()

        # Cycle through spawners scenarios and rescale max spawn number to match total spawn number
        for str_spawner_ip in self.spawners.iterkeys():
            int_spawn_quota = int(round(int_max_spawns / int_spawners_num, 0))
            dbl_spawn_quota = int_spawn_quota / int_max_spawns
            int_max_spawns -= int_spawn_quota
            int_spawners_num -= 1
            self.spawners[str_spawner_ip]['spawn_quota'] = dbl_spawn_quota

    def __zip__scenario_folder(self):
        # Create a in-memory string file and write Zip file in it
        obj_in_memory_zip = StringIO()
        obj_zipfile = ZipFile(obj_in_memory_zip, 'w')

        # Walk through files and folders
        for root, dirs, files in os.walk(self.scenario_folder):
            for file in files:
                str_relpath = os.path.relpath(root, self.scenario_folder)
                obj_zipfile.write(os.path.join(root, file), os.path.join(str_relpath, file))
        obj_zipfile.close()
        self.scenario_folder_encoded_zip = base64.b64encode(obj_in_memory_zip.getvalue())

    def __send_scenario(self):
        # Cycle through spawners and send serialized scenario class
        for str_spawner_ip in self.spawners.iterkeys():
            dic_payload = {'scenarioBase64ZippedFolder': self.scenario_folder_encoded_zip,
                           'spawnQuota': self.spawners[str_spawner_ip]['spawn_quota'],
                           'controllerIPAddress': self.controller_ip_addr,
                           'controllerPort': self.port,
                           'scenarioName': self.scenario_name,
                           'scenarioFile': self.scenario_file,
                           'resultsFile': self.results_file}
            self.spawners[str_spawner_ip]['sender'].send('setup', dic_payload)

    def setup_scenario(self):
        self.__load_scenario()
        self.__scale_ramps()
        self.__zip__scenario_folder()
        self.__send_scenario()

    def start_scenario(self):
        # Cycle through spawners and send serialized scenario class
        dic_payload = {'spawnMode': self.spawn_mode}
        for str_spawner_ip in self.spawners.iterkeys():
            self.spawners[str_spawner_ip]['sender'].send('start', dic_payload)

    def shutdown_remotes(self):
        for str_spawner_ip in self.spawners.iterkeys():
            self.spawners[str_spawner_ip]['sender'].send('shutdown', {})
