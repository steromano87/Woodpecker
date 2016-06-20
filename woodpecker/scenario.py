import abc
import os
import ConfigParser


class Scenario(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        # Options, retrieved from file if present
        self.options = self._retrieve_options(kwargs.get('peckerfile', None))

        # Navigations
        self._navigations = {}

        # Overall scenario duration
        self.scenario_duration = 0

        # Overall peckers
        self.total_peckers = 0

        # Default options name, defaults to 'Peckerfile'
        self._options_file_name = 'Peckerfile'

    def _retrieve_options(self, str_file_path=None):
        str_file_path = self._options_file_name if not str_file_path else str_file_path

        if os.path.isfile('/'.join((os.getcwd(), str_file_path))):
            obj_conf_parser = ConfigParser.ConfigParser()
            obj_conf_parser.readfp(open(str_file_path))
            for str_section in obj_conf_parser.sections():
                for str_option in obj_conf_parser.options(str_section):
                    return {str_option: str_value
                            for str_option, str_value in obj_conf_parser.get(str_section, str_option)}
        else:
            return {}

    def configure(self):
        pass

    def add_navigation(self, str_name, str_file, **kwargs):
        arr_ramps = kwargs.get('ramps', [])

        self._navigations[str_name] = {
            'file': str_file,
            'ramps': arr_ramps,
            'max_iterations': None
        }

    def get_navigations(self):
        return self._navigations

    def add_ramp(self, str_nav_name, mix_ramp):
        if isinstance(mix_ramp, list):
            self._navigations[str_nav_name]['ramps'] += mix_ramp
        else:
            self._navigations[str_nav_name]['ramps'].append(mix_ramp)

    # Calculation methods
    def get_navigation_max_peckers(self, str_nav_name):
        return sum([obj_ramp.get_max_peckers() for obj_ramp in self._navigations[str_nav_name]['ramps']])

    def get_navigation_duration(self, str_nav_name):
        return max([obj_ramp.get_duration() for obj_ramp in self._navigations[str_nav_name]['ramps']])

    def get_navigation_planned_peckers_at(self, str_nav_name, dbl_elapsed_time):
        return sum([obj_ramp.get_planned_peckers_at(dbl_elapsed_time)
                    for obj_ramp in self._navigations[str_nav_name]['ramps']])

    def get_scenario_max_peckers(self):
        return sum([self.get_navigation_max_peckers(str_nav_name) for str_nav_name in self._navigations.iterkeys()])

    def get_scenario_duration(self):
        return max([self.get_navigation_duration(str_nav_name) for str_nav_name in self._navigations.iterkeys()])

    def get_scenario_planned_peckers_at(self, dbl_elapsed_time):
        return sum([self.get_navigation_planned_peckers_at(str_nav_name, dbl_elapsed_time)
                    for str_nav_name in self._navigations.iterkeys()])

    # Rescaling methods
    def get_rescale_ratio(self, int_new_max_peckers):
        return int_new_max_peckers / self.get_scenario_max_peckers()

    def rescale_by_ratio(self, dbl_rescale_ratio):
        for str_nav_name in self._navigations.iterkeys():
            for obj_ramp in self._navigations[str_nav_name]['ramps']:
                obj_ramp.rescale_by_factor(dbl_rescale_ratio)
