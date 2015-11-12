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
        self.navigations = {}
        self.armed = False
        self.scenario_duration = 0
        self.scenario_folder = kwargs.get('scenario_folder', os.getcwd())

    def configure(self):
        pass

    @abc.abstractmethod
    def navigations_definition(self):
        pass

    def add_setting(self, str_default_key, str_value):
        """
        Add a setting value to the specified key
        """
        self.settings[str_default_key] = str_value

    def add_navigation(self, str_navigationname, str_path):
        self.navigations[str_navigationname] = {}
        self.navigations[str_navigationname]['path'] = str_path
        self.navigations[str_navigationname]['class'] = utils.import_from_path(utils.get_abs_path(str_path, self.scenario_folder),
                                                                   str_navigationname,
                                                                   {'navigation_name': str_navigationname})
        self.navigations[str_navigationname]['ramps'] = []
        self.navigations[str_navigationname]['iteration_limit'] = 0
        self.navigations[str_navigationname]['current_spawns'] = 0
        self.navigations[str_navigationname]['planned_spawns'] = 0
        self.navigations[str_navigationname]['iterations'] = 0
        self.navigations[str_navigationname]['start_time'] = None
        self.navigations[str_navigationname]['elapsed_time'] = 0
        self.navigations[str_navigationname]['threads'] = []

    def add_ramp(self, str_navigationname, **kwargs):
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
        self.navigations[str_navigationname]['ramps'].append(obj_ramp)

    def get_navigation_names(self):
        return self.navigations.keys()

    def get_navigation_class(self, str_navigation_name):
        return self.navigations[str_navigation_name]['class']

    def get_navigation_path(self, str_navigation_name):
        return self.navigations[str_navigation_name]['path']

    def get_scenario_duration(self):
        list_durations = []
        for obj_navigation in self.navigations.itervalues():
            obj_ramps = obj_navigation['ramps']
            for obj_ramp in obj_ramps:
                list_durations.append(obj_ramp.get_total_duration())
        return max(list_durations)

    def get_navigation_duration(self, str_navigationname):
        list_durations = []
        for obj_ramp in self.navigations[str_navigationname]['ramps']:
            list_durations.append(obj_ramp.get_total_duration())
        return max(list_durations)

    def get_planned_spawns(self, str_navigationname, dbl_elapsed_time):
        list_spawns = []
        for obj_ramp in self.navigations[str_navigationname]['ramps']:
            list_spawns.append(obj_ramp.get_planned_spawns_at(
                dbl_elapsed_time))
        return sum(list_spawns)

    def get_elapsed_time(self):
        return utils.get_timestamp(False) - self.scenario_start

    def get_max_navigation_spawns(self, str_navigationname):
        list_spawns = []
        for obj_ramp in self.navigations[str_navigationname]['ramps']:
            list_spawns.append(obj_ramp.get_max_spawns())
        return sum(list_spawns)

    def get_max_scenario_spawns(self):
        list_spawns = []
        for str_navigationname in self.navigations.iterkeys():
            list_spawns.append(self.get_max_navigation_spawns(str_navigationname))
        return sum(list_spawns)

    def rescale_spawns_to(self, int_rescaled_spawns):
        int_max_scenario_spawns = self.get_max_scenario_spawns() if self.get_max_scenario_spawns() > 0 else 1
        dbl_rescale_factor = int_rescaled_spawns / int_max_scenario_spawns
        self.rescale_spawns_by_factor(dbl_rescale_factor)

    def rescale_spawns_by_factor(self, dbl_rescale_factor):
        for str_navigationname, dic_navigationdata in self.navigations.iteritems():
            for int_index, obj_ramp in enumerate(dic_navigationdata['ramps']):
                self.navigations[str_navigationname]['ramps'][int_index].rescale_by_factor(dbl_rescale_factor)
