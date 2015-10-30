import threading
import cPickle
import json

from woodpecker.remotes.sysmonitor import Sysmonitor
from woodpecker.logging.sender import Sender
from woodpecker.logging.logcollector import LogCollector
from woodpecker.misc.utils import get_ip_address, get_timestamp

__author__ = 'Stefano.Romano'


class Controller(object):

    def __init__(self, str_scenario_class_path, **kwargs):
        self.__initialize(str_scenario_class_path, **kwargs)

    def __enter__(self, str_scenario_class_path, **kwargs):
        self.__initialize(str_scenario_class_path, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __del__(self):
        pass

    def __initialize(self, str_scenario_class_path, **kwargs):
        # IP addresses and ports
        self.controller_ip_addr = get_ip_address()
        self.port = kwargs.get('port', 7878)
        self.spawners_ip_addr = kwargs.get('spawners', ('localhost',))

        # Allocate an empty dict to collect spawners hostnames (for better logging readability)
        self.spawners = {}

        # Running mode (controller or spawner), defaults to controller
        self.run_mode = kwargs.get('run_mode', 'controller')

        # Spawning mode (threads or subprocesses), defaults to threads
        self.spawn_mode = kwargs.get('spawn_mode', 'thread')

        # Local flag to run everything on localhost (to nbe used in the future...), defaults to False
        self.local = kwargs.get('local', False)
