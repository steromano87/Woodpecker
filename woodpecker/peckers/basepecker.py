import abc
import importlib

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

    @abc.abstractmethod
    def mark_for_stop(self):
        pass

    def set_navigation(self, str_name, str_file):
        obj_navigation_module = importlib.import_module(''.join(('.', str_file)),
                                                        'tests.scenario_test_new.navigations')
        self._navigation = getattr(obj_navigation_module, str_name)()

    @abc.abstractmethod
    def _check_for_stop(self):
        pass

    def _run_all(self):
        # Prepare navigation for execution
        self._navigation.prepare_for_run()

        # Execute navigation setup
        self._navigation.run_setup()

        # While the iteration is valid (or no limit is set), execute the main transactions
        while not self.max_iterations or self.iteration <= self.max_iterations:
            if not self._check_for_stop():
                self._navigation.run_main(self.iteration)
                self.iteration += 1
            else:
                break

        # Finally, execute teardown transactions
        self._navigation.run_teardown()
