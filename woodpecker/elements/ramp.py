from __future__ import division

__author__ = 'Stefano.Romano'


class Ramp(object):

    def __init__(self, **kwargs):
        self.initial_delay = kwargs.get('initial_delay', 0)
        self.spawns = kwargs.get('spawns', 1)
        self.load_duration = kwargs.get('load_duration', 120)
        self.ramp_up = kwargs.get('ramp_up_duration', 30)
        self.ramp_down = kwargs.get('ramp_down_duration', 10)

    def rescale_by_factor(self, dbl_scaling_factor):
        self.spawns = self.spawns * dbl_scaling_factor

    def get_planned_spawns_at(self, dbl_elapsed_time):
        if dbl_elapsed_time < self.initial_delay:
            int_result = 0

        elif self.initial_delay <= dbl_elapsed_time < \
                (self.ramp_up + self.initial_delay):
            int_result = self.spawns / self.ramp_up * (
                dbl_elapsed_time - self.initial_delay)

        elif (self.ramp_up + self.initial_delay) <= dbl_elapsed_time < \
                (self.ramp_up + self.initial_delay +
                 self.load_duration):
            int_result = self.spawns

        elif (self.ramp_up +
                self.initial_delay + self.load_duration) <= \
                dbl_elapsed_time < (self.ramp_up +
                                    self.initial_delay +
                                    self.load_duration +
                                    self.ramp_down):
            int_result = self.spawns - self.spawns / self.ramp_down * (
                dbl_elapsed_time - self.initial_delay - self.ramp_up - self.load_duration)

        elif dbl_elapsed_time >= self.initial_delay + self.ramp_up + \
                self.load_duration + self.ramp_down:
            int_result = 0

        else:
            int_result = False

        return int(round(int_result))

    def get_total_duration(self):
        return self.initial_delay + self.ramp_up + self.load_duration\
            + self.ramp_down

    def get_max_spawns(self):
        return self.spawns
