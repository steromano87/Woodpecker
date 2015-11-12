import os
import click

import woodpecker.misc.utils as utils

from woodpecker.remotes.spawn import Spawn
from woodpecker.logging.sender import Sender
from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.remotes.sysmonitor import Sysmonitor

__author__ = 'Stefano.Romano'


class Spawner(StoppableThread):

    def __init__(self,
                 str_server_address,
                 int_controller_port,
                 str_scenario_folder,
                 str_scenario_name,
                 str_scenario_file_path,
                 str_results_file_path,
                 dbl_spawn_quota):
        # Initialize the father stoppable thread class
        super(Spawner, self).__init__()

        # Instantiates everything
        self.__initialize(controller_ip_address=str_server_address,
                          controller_port=int_controller_port,
                          scenario_folder=str_scenario_folder,
                          scenario_file=str_scenario_file_path,
                          scenario_name=str_scenario_name,
                          results_file=str_results_file_path,
                          spawn_quota=dbl_spawn_quota)
        self.__set_scenario_class()
        self.__arm()

    def run(self):
        self.__run()

    def __initialize(self, **kwargs):
        # Controller and Log collector socket port
        self.port = kwargs.get('controller_port', 7878)

        #  Controller address, void at the beginning
        self.server_address = kwargs.get('controller_ip_address', None)

        # Scenario folder, defaults to current directory
        self.scenario_folder = kwargs.get('scenario_folder', os.getcwd())

        # Scenario file name, defaults to './scenario.py'
        self.scenario_file_path = utils.get_abs_path(kwargs.get('scenario_file', './scenario.py'),
                                                     self.scenario_folder)

        # Results file path, defaults to './results/results.sqlite'
        self.results_file_path = utils.get_abs_path(kwargs.get('results_file', './results/results.sqlite'),
                                                    self.scenario_folder)

        # Scenario name, defaults to 'Scenario'
        self.scenario_name = kwargs.get('scenario_name', 'Scenario')

        # Spawn quota for local spawner
        self.spawn_quota = kwargs.get('spawn_quota', 1)

        # Placeholder for scenario
        self.scenario = None

        # Armed flag, used to start and stop running
        self.armed = False

        # Elapsed time since scenario beginning
        self.elapsed_time = 0

        # Internal message sender placeholder
        self.sender = Sender(self.server_address, self.port, 'UDP') if self.server_address else None

        # Sender spawn message poll interval
        self.sender_spawn_polling_interval = kwargs.get('sender_spawn_polling_interval', 5)
        self.sender_spawn_elapsed_time = 0.0

        # Internal Sysmonitor object and related thread
        self.sysmonitor_polling_interval = kwargs.get('sysmonitor_polling_interval', 1.0)

        click.secho(utils.logify('Setting up Sysmonitor... ', 'Spawner'))
        self.sysmonitor = Sysmonitor(self.server_address, self.port, self.sysmonitor_polling_interval)
        click.secho(utils.logify('Sysmonitor created', 'Spawner'), fg='green', bold=True)

    def __set_scenario_class(self):
        # Load scenario from temporary folder
        self.scenario = utils.import_from_path(self.scenario_file_path, self.scenario_name,
                                               {'scenario_folder': self.scenario_folder})
        self.scenario.rescale_spawns_by_factor(self.spawn_quota)

    def __arm(self):
        # Arm itself
        self.armed = True

    def __unarm(self):
        # Disarm itself
        self.armed = False

    def __run(self):
        click.secho(utils.logify('Starting Sysmonitor... ', 'Spawner'), nl=False)
        self.sysmonitor.start()
        click.secho('DONE', fg='green', bold=True)

        self.scenario.configure()
        self.scenario.navigations_definition()

        self.scenario.scenario_start = utils.get_timestamp(False)
        self.scenario.scenario_duration =\
            self.scenario.get_scenario_duration()
        list_navigations = self.scenario.get_navigation_names()

        # Update sender spawn message elapsed time
        self.sender_spawn_elapsed_time += self.elapsed_time

        # Write beginning message
        click.secho(utils.logify('Running scenario...', 'Spawner'), fg='green')

        while self.elapsed_time <= self.scenario.scenario_duration and self.armed:
            # Get elapsed time
            time_elapsed = utils.get_timestamp(False) - self.scenario.scenario_start
            self.elapsed_time = time_elapsed.total_seconds()

            # Cycle through navigations
            for str_navigation_name in list_navigations:
                # Get planned and current spawn number
                self.scenario.navigations[str_navigation_name]['planned_spawns'] =\
                    self.scenario.get_planned_spawns(str_navigation_name, self.elapsed_time)

                self.scenario.navigations[str_navigation_name]['current_spawns'] =\
                    len(self.scenario.navigations[str_navigation_name]['threads'])

                # Send spawn message, but only if is passed enough time from last sending
                if self.sender_spawn_elapsed_time >= self.sender_spawn_polling_interval:
                    self.sender.send('spawns',
                                     {
                                         'hostName': utils.get_ip_address(),
                                         'timestamp': utils.get_timestamp(),
                                         'navigationName': str_navigation_name,
                                         'plannedSpawns':
                                             self.scenario.navigations[str_navigation_name]['planned_spawns'],
                                         'runningSpawns':
                                             self.scenario.navigations[str_navigation_name]['current_spawns']
                                     })
                    self.sender_spawn_elapsed_time = 0.0

                int_spawns_difference = self.scenario.navigations[str_navigation_name][
                    'current_spawns'] - self.scenario.navigations[
                    str_navigation_name]['planned_spawns']

                # If there are less spawns than planned, add some spawns
                if int_spawns_difference < 0:
                    for int_counter in range(0, -int_spawns_difference):
                        str_navigation_path = self.scenario.get_navigation_path(str_navigation_name)
                        str_id = utils.random_id(16)

                        # Create and launch spawn
                        obj_spawn = Spawn(str_id,
                                          str_navigation_name,
                                          str_navigation_path,
                                          self.scenario_folder,
                                          self.server_address,
                                          self.port,
                                          self.scenario.settings)

                        click.secho(utils.logify(''.join(('Starting spawn ', str_id, '... ')), 'Spawner'), nl=False)
                        obj_spawn.start()
                        self.scenario.navigations[str_navigation_name]['threads'].append(obj_spawn)
                        click.secho('DONE', fg='green', bold=True)

                # If there are more spawns than planned, start killing older spawns
                elif int_spawns_difference > 0:
                    for int_counter in range(0, int_spawns_difference):
                        obj_spawn = self.scenario.navigations[str_navigation_name]['threads'].pop(0)

                        click.secho(utils.logify(''.join(('Terminating spawn ', obj_spawn.ID, '... ')), 'Spawner'),
                                    nl=False)
                        obj_spawn.terminate()
                        obj_spawn.join()
                        click.secho('DONE', fg='green', bold=True)

        self.__unarm()

        # Clean all the remaining threads
        click.secho(utils.logify('Cleaning up... ', 'Spawner'))
        for str_navigation_name in list_navigations:
            for int_counter in range(0, len(self.scenario.navigations[str_navigation_name]['threads'])):
                obj_spawn = self.scenario.navigations[str_navigation_name]['threads'].pop(0)

                click.secho(utils.logify(''.join(('Cleaning spawn ', obj_spawn.ID, '... ')), 'Spawner'),
                            nl=False)
                obj_spawn.terminate()
                obj_spawn.join()
                click.secho('DONE', fg='green', bold=True)
        click.secho(utils.logify('Cleaning completed', 'Spawner'), fg='green', bold=True)

        # Close Sysmonitor thread
        click.secho(utils.logify('Closing Sysmonitor... ', 'Spawner'), nl=False)
        self.sysmonitor.terminate()
        self.sysmonitor.join()
        click.secho('DONE', fg='green', bold=True)

        click.secho(utils.logify('Scenario gracefully completed!', 'Spawner'), fg='green', bold=True)
