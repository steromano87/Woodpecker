from woodpecker.misc.utils import get_timestamp, random_id
from woodpecker.remotes.spawn import Spawn

__author__ = 'Stefano.Romano'


class Spawner(object):

    def __init__(self, str_scenario_path, str_host='', str_port=7777):
        self.host = str_host
        self.port = str_port
        # self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.elapsed_time = 0
        self.armed = False

        obj_module = __import__(str_scenario_path)
        obj_class = getattr(obj_module, str_scenario_path)
        self.scenario = obj_class()

    def arm(self):
        # self.socket.bind((self.host, self.port))
        # self.socket.listen(5)
        self.armed = True

    def run(self):
        self.scenario.configure()
        self.scenario.tests_definition()

        self.scenario.scenario_start = get_timestamp(False)
        self.scenario.scenario_duration =\
            self.scenario.get_scenario_duration()
        list_tests = self.scenario.get_test_names()

        while self.elapsed_time <= self.scenario.scenario_duration:
            time_elapsed = get_timestamp(False) - self.scenario.scenario_start
            self.elapsed_time = time_elapsed.total_seconds()
            for str_test_name in list_tests:
                self.scenario.tests[str_test_name]['planned_spawns'] =\
                    self.scenario.get_planned_spawns(str_test_name, self.elapsed_time)

                self.scenario.tests[str_test_name]['current_spawns'] =\
                    len(self.scenario.tests[str_test_name]['threads'])

                int_spawns_difference = self.scenario.tests[str_test_name][
                    'current_spawns'] - self.scenario.tests[
                    str_test_name]['planned_spawns']

                if int_spawns_difference < 0:
                    for int_counter in range(0, -int_spawns_difference):
                        str_test_path = self.scenario.get_test_path(str_test_name)
                        str_id = random_id(16)
                        print(str_id)
                        obj_spawn = Spawn(str_id, str_test_name,
                                          str_test_path)
                        obj_spawn.start()
                        self.scenario.tests[str_test_name]['threads'].append(obj_spawn)

                elif int_spawns_difference > 0:
                    for int_counter in range(0, int_spawns_difference):
                        obj_spawn = self.scenario.tests[str_test_name]['threads'].pop(0)
                        obj_spawn.terminate()
                        obj_spawn.join()
                        print('Killed one')
