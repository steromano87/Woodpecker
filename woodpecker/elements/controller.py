from __future__ import division
import base64
import os
import time
import zipfile
import click

from StringIO import StringIO

from woodpecker.remotes.sysmonitor import Sysmonitor
from woodpecker.logging.sender import Sender
from woodpecker.logging.logcollector import LogCollectorThread
import woodpecker.misc.utils as utils

__author__ = 'Stefano.Romano'


class Controller(object):

    def __init__(self, str_scenario_name, **kwargs):
        self._initialize(str_scenario_name, **kwargs)

    def __enter__(self, str_scenario_name, **kwargs):
        self._initialize(str_scenario_name, **kwargs)

    def __exit__(self, exc_type, exc_val, exc_tb):
        click.secho('Controller closed', fg='red')

    def __del__(self):
        click.secho('Controller closed', fg='red')

    def _initialize(self, str_scenario_name, **kwargs):
        # Self address
        self.ip_address = kwargs.get('ip_address', utils.get_ip_address())

        # Controller port
        self.port = kwargs.get('port', 7878)

        # Allocate an empty dict to collect spawners data
        self.spawners = {}
        list_spawners = kwargs.get('spawners', [self.ip_address])
        for str_spawner in list_spawners:
            self.spawners[str_spawner] = {}

            # Create a sender for each spawner
            self.spawners[str_spawner]['sender'] = Sender(str_spawner, self.port, 'TCP')

        # Spawning mode (threads or subprocesses), defaults to threads
        self.spawn_mode = kwargs.get('spawn_mode', 'thread')

        # Local flag to run everything on localhost (to be used in the future...), defaults to False
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

        # Scenario duration, o be filled later
        self.scenario_duration = None

        # Result file, defaults to 'results/results.sqlite' file
        self.results_file = kwargs.get('results_file', './results/results.sqlite')

        # Result file path
        self.results_file_path = utils.get_abs_path(self.results_file, self.scenario_folder)

        # Sysmonitor thread
        self.sysmonitor = Sysmonitor(self.ip_address, self.port, str_host_type='controller', bool_debug=False)

        # Log Collector thread
        self.logcollector = LogCollectorThread(self.results_file_path, self.ip_address, self.port)

        # Elapsed time since scenario duration
        self.scenario_elapsed_time = 0

    def _load_scenario(self):
        # Log message
        click.secho(utils.logify('Loading scenario... '), nl=False)

        # Get scenario from path and name
        self.scenario = utils.import_from_path(self.scenario_file_path, self.scenario_name,
                                               {'scenario_folder': self.scenario_folder})

        # Load navs
        self.scenario.navigations_definition()

        # Fill scenario duration
        self.scenario_duration = self.scenario.get_scenario_duration()

    def _scale_ramps(self):
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

        # End of message
        click.secho('DONE', fg='green', bold=True)

    def _zip__scenario_folder(self):
        # Log message
        click.secho(utils.logify('Zipping scenario... '), nl=False)

        # Create a in-memory string file and write Zip file in it
        obj_in_memory_zip = StringIO()
        obj_zipfile = zipfile.ZipFile(obj_in_memory_zip, 'w', zipfile.ZIP_DEFLATED)

        # Walk through files and folders
        for root, dirs, files in os.walk(self.scenario_folder):
            for filename in files:
                str_relpath = os.path.relpath(root, self.scenario_folder)
                obj_zipfile.write(os.path.join(root, filename), os.path.join(str_relpath, filename))
        obj_zipfile.close()
        bin_archive = obj_in_memory_zip.getvalue()
        self.scenario_folder_encoded_zip = base64.b64encode(bin_archive)

        # End of message
        click.secho('DONE', fg='green', bold=True)

    def _send_scenario(self):
        # Cycle through spawners and send serialized scenario class
        for str_spawner_ip in self.spawners.iterkeys():
            click.secho(utils.logify(''.join(('Sending scenario to spawner ', str_spawner_ip, '... '))), nl=False)

            dic_payload = {'scenarioBase64ZippedFolder': self.scenario_folder_encoded_zip,
                           'spawnQuota': self.spawners[str_spawner_ip]['spawn_quota'],
                           'controllerPort': self.port,
                           'scenarioName': self.scenario_name,
                           'scenarioFile': self.scenario_file,
                           'resultsFile': self.results_file}
            self.spawners[str_spawner_ip]['sender'].send('setup', dic_payload)

            click.secho('DONE', fg='green', bold=True)

    def setup_scenario(self):
        self._load_scenario()
        self._scale_ramps()
        self._zip__scenario_folder()
        self._send_scenario()

    def start_scenario(self):
        # Start Logcollector and Sysmonitor threads
        click.secho(utils.logify('Starting Log Collector... '), nl=False)
        self.logcollector.start()
        click.secho('DONE', fg='green', bold=True)

        click.secho(utils.logify('Starting Sysmonitor... '), nl=False)
        self.sysmonitor.start()
        click.secho('DONE', fg='green', bold=True)

        # Cycle through spawners and send serialized scenario class
        dic_payload = {'spawnMode': self.spawn_mode}
        for str_spawner_ip in self.spawners.iterkeys():
            click.secho(utils.logify(''.join(('Starting spawner ', str_spawner_ip, '... '))), nl=False)
            self.spawners[str_spawner_ip]['sender'].send('start', dic_payload)
            click.secho('DONE', fg='green', bold=True)

        # Wait until completion
        click.secho(utils.logify('Waiting for scenario completion...'), fg='green', bold=True)
        while self.scenario_elapsed_time <= self.scenario_duration:
            time.sleep(1)
            self.scenario_elapsed_time += 1

        # Terminate Sysmonitor and Log Collector at the ennd of the scenario
        click.secho(utils.logify('Closing Sysmonitor... '), nl=False)
        self.sysmonitor.terminate()
        self.sysmonitor.join()
        click.secho('DONE', fg='green', bold=True)

        click.secho(utils.logify('Closing Log Collector... '), nl=False)
        self.logcollector.terminate()
        self.logcollector.join()
        click.secho('DONE', fg='green', bold=True)

    def shutdown_remotes(self):
        for str_spawner_ip in self.spawners.iterkeys():
            click.secho(utils.logify(''.join(('Sending shutdown message to spawner ',
                                              str_spawner_ip, '... '))), nl=False)
            self.spawners[str_spawner_ip]['sender'].send('shutdown', {})
            click.secho('DONE', fg='green', bold=True)
