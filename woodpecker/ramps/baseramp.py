from __future__ import division

import abc


class BaseRamp(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.initial_delay = kwargs.get('initial_delay', 0)
        self.peckers = kwargs.get('peckers', 1)
        self.load_duration = kwargs.get('load_duration', 120)
        self.ramp_up_duration = kwargs.get('ramp_up_duration', 30)
        self.ramp_down_duration = kwargs.get('ramp_down_duration', 10)

    @abc.abstractmethod
    def get_planned_peckers_at(self, dbl_elapsed_time):
        pass

    def get_duration(self):
        return self.initial_delay + self.ramp_up_duration + self.load_duration + self.ramp_down_duration

    def get_max_peckers(self):
        return self.peckers

    def rescale_by_ratio(self, dbl_ratio):
        self.peckers *= dbl_ratio

    @abc.abstractmethod
    def get_pecker_schedule(self):
        pass
