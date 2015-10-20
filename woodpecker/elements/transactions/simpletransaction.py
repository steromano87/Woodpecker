import abc

__author__ = 'Stefano.Romano'


class SimpleTransaction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, str_spawn_id, int_iteration, **kwargs):
        """Sets up base variables"""

        self.settings = kwargs.get('settings', {})
        self.thread_variables = kwargs.get('thread_variables', {})
        self.iteration = int_iteration
        self.test_name = str_testname

    def configure(self):
        """Insert here the configuration script"""
        pass

    @abc.abstractmethod
    def steps(self):
        """Insert here the calls to be performed"""
        pass

    def add_setting(self, str_default_key, str_default_value):
        """Add a setting value to the specified key"""

        self.settings[str_default_key] = str_default_value

    def set_variable(self, str_name, str_value):
        """Add a variable to the thread variables dict"""

        self.thread_variables[str_name] = str_value

    def run(self):
        self.configure()
        self.steps()
        return self.settings,\
            self.thread_variables
