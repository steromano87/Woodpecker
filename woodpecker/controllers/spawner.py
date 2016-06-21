import importlib
import time

from woodpecker.logging.log import Log
from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.options import Options


class Spawner(StoppableThread):

    def __init__(self, obj_scenario, **kwargs):
        super(Spawner, self).__init__()

        # Internal log
        self.log = Log()

        # Options
        self.options = kwargs.get('options', Options())

        # Loaded scenario
        self._scenario = obj_scenario

        # Peckers list
        self._peckers = {}

        # Schedule list (only if in passive mode)
        self._schedules = {}

        # Elapsed time counter
        self.elapsed_time = 0.0

        # Spawning mode, to choose between threads and greenlet
        self.spawning_mode = kwargs.get('spawning_mdoe', self.options.get('execution', 'spawning_mode'))
        if self.spawning_mode == 'threads':
            self.pecker_class = getattr(importlib.import_module('woodpecker.peckers.threadedpecker'), 'ThreadedPecker')
        elif self.spawning_mode == 'greenlet':
            self.pecker_class = getattr(importlib.import_module('woodpecker.peckers.greenletpecker'), 'GreenletPecker')

        # Pecker handling mode, it may be active or passive
        self.pecker_handling_mode = kwargs.get('pecker_handling_mode',
                                               self.options.get('execution', 'pecker_handling_mode'))

    def initialize_peckers_list(self):
        for str_nav_name in self._scenario.get_navigation_names():
            self._peckers[str_nav_name] = []
            if self.pecker_handling_mode == 'passive':
                self._schedules[str_nav_name] = self._scenario.get_navigation_pecker_schedule(str_nav_name)

    def start_pecker_for(self, str_nav_name):
        dic_navigation = self._scenario.get_navigation(str_nav_name)
        obj_pecker = self.pecker_class(max_iterations=dic_navigation.get('max_iterations', None),
                                       pecker_handling_mode=self.pecker_handling_mode)

        if self.pecker_handling_mode == 'passive':
            dic_schedule = self._schedules[str_nav_name].pop(0)[0]
            obj_pecker.set_schedule(dic_schedule['scheduled_start'],
                                    dic_schedule['scheduled_stop'])

        obj_pecker.set_navigation(str_nav_name, dic_navigation.get('file'))
        self._peckers[str_nav_name].append(obj_pecker)
        self._peckers[str_nav_name][-1].start()

    def stop_pecker_for(self, str_nav_name):
        self._peckers[str_nav_name][0].mark_for_stop()
        self._peckers[str_nav_name].pop(0)

    def check_running_peckers(self):
        if self.pecker_handling_mode == 'active':
            for str_nav_name in self._scenario.get_navigation_names():
                self._check_running_peckers_active(str_nav_name)
            time.sleep(self.options.get('execution', 'pecker_status_active_polling_interval'))
        elif self.pecker_handling_mode == 'passive':
            for str_nav_name in self._scenario.get_navigation_names():
                self._check_running_peckers_passive(str_nav_name)

    def _check_running_peckers_active(self, str_nav_name):
        int_scheduled_peckers = self._scenario.get_navigation_planned_peckers_at(self.elapsed_time)
        int_running_peckers = len(self._peckers[str_nav_name])
        int_peckers_diff = int_scheduled_peckers - int_running_peckers

        if int_peckers_diff > 0:
            for int_counter in range(0, int_peckers_diff):
                self.start_pecker_for(str_nav_name)
        elif int_peckers_diff < 0:
            for int_counter in range(0, -int_peckers_diff):
                self.stop_pecker_for(str_nav_name)

    def _check_running_peckers_passive(self, str_nav_name):
        # Run only if there are some unscheduled peckers
        if len(self._schedules[str_nav_name]) > 0:
            int_max_peckers = self._scenario.get_navigation_max_peckers(str_nav_name)
            for int_counter in range(0, int_max_peckers):
                self.start_pecker_for(str_nav_name)

    def run(self):
        while True:
            if not self.is_marked_for_stop():
                self.check_running_peckers()
            else:
                for str_nav_name in self._scenario.get_navigation_names():
                    for obj_pecker in self._peckers[str_nav_name]:
                        obj_pecker.mark_for_stop()
                break
