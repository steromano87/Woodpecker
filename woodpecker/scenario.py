import abc

from woodpecker.options import Options


class Scenario(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_peckerfile=None):
        # Options, retrieved from file if present
        self.options = Options(str_peckerfile)

        # Navigations
        self._navigations = {}

        # Overall scenario duration
        self.scenario_duration = 0

        # Overall peckers
        self.total_peckers = 0

    def configure(self):
        pass

    def add_navigation(self, str_name, str_file, **kwargs):
        arr_ramps = kwargs.get('ramps', [])
        int_max_iterations = kwargs.get('max_iterations', None)

        self._navigations[str_name] = {
            'file': str_file,
            'ramps': arr_ramps,
            'max_iterations': int_max_iterations
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
