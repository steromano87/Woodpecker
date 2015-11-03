import threading
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

        # Scenario file path, defaults to standard scenario file
        self.scenario_file_path = utils.get_abs_path(kwargs.get('scenario_file_path', './scenario.py'),
                                                     self.scenario_folder)

        # Result file path
        self.result_file_path = utils.get_abs_path(kwargs.get('result_file', './results/results.sqlite'),
                                                   self.scenario_folder)

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
            int_spawner_quota = int(round(int_max_spawns / int_spawners_num, 0))
            int_max_spawns -= int_spawner_quota
            int_spawners_num -= 1
            self.spawners[str_spawner_ip]['spawn_quota'] = int_spawner_quota

    def __zip__scenario_folder(self):
        # Create a in-memory string file and write Zip file in it
        obj_in_memory_zip = StringIO()
        obj_zipfile = ZipFile(obj_in_memory_zip, 'w')

        # Walk through files and folders
        for root, dirs, files in os.walk(self.scenario_folder):
            for file in files:
                obj_zipfile.write(os.path.join(root, file))
        obj_zipfile.close()
        self.scenario_folder_encoded_zip = base64.b64encode(obj_in_memory_zip.getvalue())

    def __send_zipped_scenarios(self):
        # Cycle through spawners and send serialized scenario class
        dic_payload = {'scenarioSerializedFolder': self.scenario_folder_encoded_zip}
        for str_spawner_ip in self.spawners.iterkeys():
            # self.spawners[str_spawner_ip]['sender'].send('serializedScenario', dic_payload)
            pass

    def start_scenario(self):
        self.__load_scenario()
        self.__scale_ramps()
        self.__zip__scenario_folder()
        self.__send_zipped_scenarios()
