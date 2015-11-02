import threading
import cPickle
import json
import os

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

        # Running mode (controller or spawner), defaults to controller
        self.run_mode = kwargs.get('run_mode', 'controller')

        # Spawning mode (threads or subprocesses), defaults to threads
        self.spawn_mode = kwargs.get('spawn_mode', 'thread')

        # Local flag to run everything on localhost (to nbe used in the future...), defaults to False
        self.local = kwargs.get('local', False)

        # Placeholder for scenario
        self.scenario = None

        # Scenario class name
        self.scenario_name = str_scenario_name

        # Scenario folder
        self.scenario_folder = os.getcwd()

        # Scenario file path, defaults to standard scenario file
        self.scenario_file_path = utils.get_abs_path(kwargs.get('scenario_file_path', './scenario.py'),
                                                     self.scenario_folder)

        # Result file path
        self.result_file_path = utils.get_abs_path(kwargs.get('result_file', './results/results.sqlite'),
                                                   self.scenario_folder)

    def __load_scenario(self):
        # Get scenario from path and name
        self.scenario = utils.import_from_path(self.scenario_file_path, self.scenario_name)

        # Load tests
        self.scenario.tests_definition()

    def __scale_ramps(self):
        # Get spawners number
        int_spawners_num = len(self.spawners)
        int_max_spawns = self.scenario.get_max_scenario_spawns()

        # Cycle through spawners scenarios and rescale max spawn number to match total spawn number
        for str_spawner_ip, dic_spawner_data in self.spawners.iteritems():
            # First assign original scenario...
            self.spawners[str_spawner_ip]['scenario'] = self.scenario

            # Then calculate max spawn number and assign it
            int_spawner_quota = int(round(int_max_spawns / int_spawners_num, 0))
            int_max_spawns -= int_spawner_quota
            int_spawners_num -= 1
            self.spawners[str_spawner_ip]['scenario'].rescale_spawns_to(int_spawner_quota)

    def start_scenario(self):
        self.__load_scenario()
        self.__scale_ramps()
