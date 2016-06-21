from __future__ import division

from woodpecker.ramps.baseramp import BaseRamp


class LinearRamp(BaseRamp):

    def __init__(self, **kwargs):
        super(LinearRamp, self).__init__(**kwargs)

    def get_planned_peckers_at(self, dbl_elapsed_time):
        if dbl_elapsed_time < self.initial_delay \
                or dbl_elapsed_time >= self.initial_delay + self.ramp_up_duration + \
                self.load_duration + self.ramp_down_duration:
            int_result = 0

        elif self.initial_delay <= dbl_elapsed_time < \
                (self.ramp_up_duration + self.initial_delay):
            int_result = self.peckers / self.ramp_up_duration * (
                dbl_elapsed_time - self.initial_delay)

        elif (self.ramp_up_duration + self.initial_delay) <= dbl_elapsed_time < \
                (self.ramp_up_duration + self.initial_delay +
                 self.load_duration):
            int_result = self.peckers

        elif (self.ramp_up_duration +
                self.initial_delay + self.load_duration) <= \
                dbl_elapsed_time < (self.ramp_up_duration +
                                    self.initial_delay +
                                    self.load_duration +
                                    self.ramp_down_duration):
            int_result = self.peckers - self.peckers / self.ramp_down_duration * (
                dbl_elapsed_time - self.initial_delay - self.ramp_up_duration - self.load_duration)

        else:
            int_result = None

        return int(round(int_result))

    def get_pecker_schedule(self):
        lst_peckers = []
        for int_pecker_index in range(0, self.get_max_peckers() - 1):
            lst_peckers.append({
                'scheduled_start': self.ramp_up_duration / self.get_max_peckers() * int_pecker_index,
                'scheduled_stop':
                    self.ramp_down_duration + self.load_duration +
                    self.ramp_down_duration / self.get_max_peckers() * int_pecker_index
            })
