import os
import importlib

from woodpecker.options import Options
from woodpecker.logging.log import Log
from woodpecker.logging.sysmonitor import Sysmonitor
from woodpecker.logging.sender import Sender


class MainController(object):

    def __init__(self, str_scenario_name, **kwargs):
        # Options
        self._options = Options(kwargs.get('peckerfile', None))

        # Log
        self._log = Log()

        # Sysmonitor
        self._sysmonitor = Sysmonitor('controller')

        # Spawner hosts
        self.spawners = {}
        lst_spawners = kwargs.get('spawners', self._options.get('execution', 'spawners'))
        for str_spawner in lst_spawners:
            self.spawners[str_spawner] = {
                'sender': Sender(str_spawner,
                                 self._options.get('execution', 'controller_port'),
                                 self._options.get('execution', 'controller_protocol')),
                'rescale_ratio': 1.0
            }

        # Log collector
        self._log_collector = None

        # Scenario
        self._scenario = getattr(importlib.import_module('scenario'), str_scenario_name)()
