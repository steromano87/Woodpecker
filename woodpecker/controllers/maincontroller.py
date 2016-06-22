from __future__ import division

import os
import importlib
import msgpack
import zipfile

from StringIO import StringIO

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
        self._scenario = getattr(importlib.import_module('.scenario', 'tests.scenario_test_new'), str_scenario_name)()
        self._scenario_name = str_scenario_name
        self._scenario.configure()
        self._scenario.navigations()

        # Scenario duration
        self._scenario_duration = self._scenario.get_scenario_duration()

        # Scenario folder
        self._scenario_folder = os.path.abspath(kwargs.get('scenario_folder', os.getcwd()))

        # Compressed scenario
        self._compressed_scenario = None

    def calculate_resize_ratios(self):
        int_max_peckers = self._scenario.get_scenario_max_peckers()
        int_spawners_num = len(self.spawners.keys())
        # Iterate and calculate resize ratios for every spawner (odd numbers safe)
        for str_spawner in self.spawners.iterkeys():
            int_pecker_quota = int(round(int_max_peckers / int_spawners_num, 0))
            dbl_pecker_quota = int_pecker_quota / self._scenario.get_scenario_max_peckers()
            int_max_peckers -= int_pecker_quota
            int_spawners_num -= 1
            self.spawners[str_spawner]['rescale_ratio'] = dbl_pecker_quota

    def compress_scenario_folder(self):
        obj_in_memory_zip = StringIO()
        obj_zipfile = zipfile.ZipFile(obj_in_memory_zip, 'w', zipfile.ZIP_DEFLATED)

        # Walk through files and folders
        for root, dirs, files in os.walk(self._scenario_folder):
            for filename in files:
                str_relpath = os.path.relpath(root, self._scenario_folder)
                obj_zipfile.write(os.path.join(root, filename), os.path.join(str_relpath, filename))
        obj_zipfile.close()
        self._compressed_scenario = obj_in_memory_zip.getvalue()

    def dump_compressed_scenario(self, str_dump_path=os.getcwd()):
        os.chdir(str_dump_path)
        with open('.'.join((self._scenario_name, 'zip')), 'w') as obj_fp:
            obj_fp.write(self._compressed_scenario)

    def _send_to_all(self, str_message_type, dic_payload):
        for obj_spawner_data in self.spawners.itervalues():
            obj_spawner_data['sender'].send(str_message_type, dic_payload)

    def send_scenario(self):
        dic_payload = {
            'command': 'scenario_unpack',
            'data': {
                'compressed_scenario_folder': self._compressed_scenario
            }
        }
        self._send_to_all('command', dic_payload)

    def remote_scenario_setup(self):
        for obj_spawner_data in self.spawners.itervalues():
            dic_payload = {
                'command': 'scenario_setup',
                'data': {
                    'scenario_name': self._scenario_name,
                    'rescale_ratio': obj_spawner_data.get('rescale_ratio', 1.0)
                }
            }
            obj_spawner_data['sender'].send('command', dic_payload)

    def send_start(self):
        self._send_to_all('command', {'command': 'start'})

    def send_stop(self):
        self._send_to_all('command', {'command': 'stop'})

    def send_emergency_stop(self):
        self._send_to_all('command', {'command': 'emergency_stop'})

    def send_shutdown(self):
        self._send_to_all('command', {'command': 'shutdown'})
