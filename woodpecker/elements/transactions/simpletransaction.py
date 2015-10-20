import abc

__author__ = 'Stefano.Romano'


class SimpleTransaction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, int_iteration, **kwargs):
        self.settings = kwargs.get('settings', {})
        self.last_response = False
        self.thread_variables = kwargs.get('thread_variables', {})

    def configure(self):
        """Insert here the configuration script"""
        pass

    @abc.abstractmethod
    def steps(self):
        """Insert here the calls to be performed"""
        pass

    def add_setting(self, str_default_key, str_default_value):
        self.settings[str_default_key] = str_default_value

    def set_variable(self, str_name, str_value):
        self.thread_variables[str_name] = str_value

    def run(self):
        self.configure()
        self.steps()
        return self.settings,\
            self.session,\
            self.last_response,\
            self.thread_variables
