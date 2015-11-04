import abc
import os

from woodpecker.elements.ramp import Ramp
import woodpecker.misc.utils as utils

__author__ = 'Stefano.Romano'


class Scenario(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.settings = kwargs.get('settings', {})
        self.scenario_start = None
        self.scenario_stop = None
        self.tests = {}
        self.armed = False
        self.scenario_duration = 0
        self.scenario_folder = kwargs.get('scenario_folder', os.getcwd())

    def configure(self):
        pass

    @abc.abstractmethod
    def tests_definition(self):
        pass

    def add_setting(self, str_default_key, str_value):
        """
        Add a setting value to the specified key
        """
        self.settings[str_default_key] = str_value

    def add_test(self, str_testname, str_path):
        self.tests[str_testname] = {}
        self.tests[str_testname]['path'] = str_path
        self.tests[str_testname]['class'] = utils.import_from_path(utils.get_abs_path(str_path, self.scenario_folder),
                                                                   str_testname,
                                                                   {'test_name': str_testname})
        self.tests[str_testname]['ramps'] = []
        self.tests[str_testname]['iteration_limit'] = 0
        self.tests[str_testname]['current_spawns'] = 0
        self.tests[str_testname]['planned_spawns'] = 0
        self.tests[str_testname]['iterations'] = 0
        self.tests[str_testname]['start_time'] = None
        self.tests[str_testname]['elapsed_time'] = 0
        self.tests[str_testname]['threads'] = []

    def add_ramp(self, str_testname, **kwargs):
        int_initial_delay = kwargs.get('initial_delay', 0)
        int_ramp_up = kwargs.get('ramp_up', 30)
        int_spawns = kwargs.get('spawns', 1)
        int_load_duration = kwargs.get('load_duration', 120)
        int_ramp_down = kwargs.get('ramp_down', 10)
        obj_ramp = Ramp(initial_delay=int_initial_delay,
                        spawns=int_spawns,
                        load_duration=int_load_duration,
                        ramp_up=int_ramp_up,
                        ramp_down=int_ramp_down)
        self.tests[str_testname]['ramps'].append(obj_ramp)

    def get_test_names(self):
        return self.tests.keys()

    def get_test_class(self, str_test_name):
        return self.tests[str_test_name]['class']

    def get_test_path(self, str_test_name):
        return self.tests[str_test_name]['path']

    def get_scenario_duration(self):
        list_durations = []
        for obj_test in self.tests.itervalues():
            obj_ramps = obj_test['ramps']
            for obj_ramp in obj_ramps:
                list_durations.append(obj_ramp.get_total_duration())
        return max(list_durations)

    def get_test_duration(self, str_testname):
        list_durations = []
        for obj_ramp in self.tests[str_testname]['ramps']:
            list_durations.append(obj_ramp.get_total_duration())
        return max(list_durations)

    def get_planned_spawns(self, str_testname, dbl_elapsed_time):
        list_spawns = []
        for obj_ramp in self.tests[str_testname]['ramps']:
            list_spawns.append(obj_ramp.get_planned_spawns_at(
                dbl_elapsed_time))
        return sum(list_spawns)

    def get_elapsed_time(self):
        return utils.get_timestamp(False) - self.scenario_start

    def get_max_test_spawns(self, str_testname):
        list_spawns = []
        for obj_ramp in self.tests[str_testname]['ramps']:
            list_spawns.append(obj_ramp.get_max_spawns())
        return sum(list_spawns)

    def get_max_scenario_spawns(self):
        list_spawns = []
        for str_testname in self.tests.iterkeys():
            list_spawns.append(self.get_max_test_spawns(str_testname))
        return sum(list_spawns)

    def rescale_spawns_to(self, int_rescaled_spawns):
        int_max_scenario_spawns = self.get_max_scenario_spawns() if self.get_max_scenario_spawns() > 0 else 1
        dbl_rescale_factor = int_rescaled_spawns / int_max_scenario_spawns
        self.rescale_spawns_by_factor(dbl_rescale_factor)

    def rescale_spawns_by_factor(self, dbl_rescale_factor):
        for str_testname, dic_testdata in self.tests.iteritems():
            for int_index, obj_ramp in enumerate(dic_testdata['ramps']):
                self.tests[str_testname]['ramps'][int_index].rescale_by_factor(dbl_rescale_factor)
