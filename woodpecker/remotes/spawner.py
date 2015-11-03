import tempfile
import base64
import woodpecker.misc.utils as utils

from woodpecker.remotes.spawn import Spawn
from woodpecker.logging.sender import Sender
from woodpecker.misc.stoppablethread import StoppableThread

__author__ = 'Stefano.Romano'


class Spawner(StoppableThread):

    def __init__(self, str_server_address, str_base64_scenario_serialization):
        # Initialize the father stoppable thread class
        super(Spawner, self).__init__()

        # Instantiates everything
        self.__initialize(server_address=str_server_address)
        # self.__set_scenario_class(str_base64_scenario_serialization)
        self.__arm()

    def run(self):
        self.__run()

    def __initialize(self, **kwargs):
        # Controller and Log collector socket port
        self.port = kwargs.get('port', 7878)

        #  Controller address, void at the beginning
        self.server_address = kwargs.get('server_address', None)

        # Working dir, defaults to standard temp folder (depending on OS)
        self.temp_folder = tempfile.gettempdir()

        # Placeholder for scenario
        self.scenario = None

        # Armed flag, used to start and stop running
        self.armed = False

        # Elapsed time since scenario beginning
        self.elapsed_time = 0

        # Internal message sender placeholder
        self.sender = Sender(self.server_address, self.port, 'UDP') if self.server_address else None

    def __set_scenario_class(self, str_base64_scenario_serialization):
        # Load scenario from ZIP file
        pass

    def __arm(self):
        # Arm itself
        self.armed = True

    def __unarm(self):
        # Disarm itself
        self.armed = False

    def __run(self):
        self.scenario.configure()
        self.scenario.tests_definition()

        self.scenario.scenario_start = utils.get_timestamp(False)
        self.scenario.scenario_duration =\
            self.scenario.get_scenario_duration()
        list_tests = self.scenario.get_test_names()

        while self.elapsed_time <= self.scenario.scenario_duration and self.armed:
            time_elapsed = utils.get_timestamp(False) - self.scenario.scenario_start
            self.elapsed_time = time_elapsed.total_seconds()
            for str_test_name in list_tests:
                self.scenario.tests[str_test_name]['planned_spawns'] =\
                    self.scenario.get_planned_spawns(str_test_name, self.elapsed_time)

                self.scenario.tests[str_test_name]['current_spawns'] =\
                    len(self.scenario.tests[str_test_name]['spawns'])

                int_spawns_difference = self.scenario.tests[str_test_name][
                    'current_spawns'] - self.scenario.tests[
                    str_test_name]['planned_spawns']

                if int_spawns_difference < 0:
                    for int_counter in range(0, -int_spawns_difference):
                        str_test_path = self.scenario.get_test_path(str_test_name)
                        str_id = utils.random_id(16)
                        print(str_id)
                        obj_spawn = Spawn(str_id, str_test_name,
                                          str_test_path, self.scenario.settings)
                        obj_spawn.start()
                        self.scenario.tests[str_test_name]['spawns'].append(obj_spawn)

                elif int_spawns_difference > 0:
                    for int_counter in range(0, int_spawns_difference):
                        obj_spawn = self.scenario.tests[str_test_name]['spawns'].pop(0)
                        obj_spawn.terminate()
                        obj_spawn.join()
                        print('Killed one')
