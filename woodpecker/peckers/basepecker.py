import abc
import importlib

import woodpecker.misc.utils as utils

from woodpecker.options import Options
from woodpecker.logging.log import Log


class BasePecker(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        # Iteration
        self.iteration = 1

        # Max iterations for the given navigation
        self.max_iterations = kwargs.get('max_iterations', None)

        # Internal log
        self.log = Log()

        # Pecker options
        self.options = kwargs.get('options', None) or Options()

        # Internal navigation storage
        self._navigation = None

        # Handling mode (active or passive)
        # If active, the spawner continuously checks if the peckers are running
        # If passive, the peckers are scheduled for start and stop one for all
        self._handling_mode = kwargs.get('pecker_handling_mode', self.options.get('execution', 'pecker_handling_mode'))

        # Scheduled start and stop based on elapsed time (used only in passive mode)
        self._scheduled_start = None
        self._scheduled_stop = None

        # Internal elapsed time counter
        self._elapsed_time = 0.0
        self._start_time = None

        # Pecker status
        self.status = 'Initialized'

    @abc.abstractmethod
    def mark_for_stop(self):
        pass

    def set_navigation(self, str_name, str_file):
        obj_navigation_module = importlib.import_module(''.join(('.', str_file)),
                                                        'tests.scenario_test_new.navigations')
        self._navigation = getattr(obj_navigation_module, str_name)()
        self.status = 'Ready'

    def set_schedule(self, dbl_elapsed_start, dbl_elapsed_stop):
        self._scheduled_start = dbl_elapsed_start
        self._scheduled_stop = dbl_elapsed_stop

    @abc.abstractmethod
    def _check_for_stop(self):
        pass

    @abc.abstractmethod
    def get_name(self):
        pass

    def set_elapsed_time(self):
        self._elapsed_time = (utils.get_timestamp(False) - self._start_time).total_seconds()

    def _run_all(self):
        self._start_time = utils.get_timestamp(False)

        # Prepare navigation for execution
        self._navigation.prepare_for_run()

        # If handling mode is set to passive, wait until the start elapsed time is reached
        if self._handling_mode == 'passive':
            self.status = 'Waiting to start'
            while True:
                self.set_elapsed_time()
                if self._elapsed_time >= self._scheduled_start:
                    break

        # Execute navigation setup
        self.status = 'Starting'
        self._navigation.run_setup()
        self.set_elapsed_time()

        # While the iteration is valid (or no limit is set), execute the main transactions
        while not self.max_iterations or self.iteration <= self.max_iterations or (
            self._handling_mode == 'passive' and self._elapsed_time < self._scheduled_stop
        ):
            if not self._check_for_stop():
                self.status = 'Running'
                self._navigation.run_main(self.iteration)
                self.iteration += 1
                self.set_elapsed_time()
            else:
                self.status = 'Stopping'
                break

        # Finally, execute teardown transactions
        self._navigation.run_teardown()
        self.status = 'Stopped'
