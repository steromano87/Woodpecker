import abc

__author__ = 'Stefano.Romano'


class SimpleTransaction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        """
        Sets up base variables
        """
        self.iteration = 0
        self.test_name = kwargs.get('test_name', 'NONAME')
        self.spawn_id = ''
        self.settings = {}
        self.thread_variables = {}

    def configure(self):
        """
        Insert here the configuration script
        """
        pass

    @abc.abstractmethod
    def steps(self):
        """
        Insert here the calls to be performed
        """
        pass

    def add_setting(self, str_default_key, str_value):
        """
        Add a setting value to the specified key
        """
        self.settings[str_default_key] = str_value

    def set_variable(self, str_name, str_value):
        """
        Add a variable to the thread variables dict
        """
        self.thread_variables[str_name] = str_value

    def run(self, str_spawn_id, int_iteration, dic_settings=None, dic_thread_variables=None):
        self.spawn_id = str_spawn_id
        self.iteration = int_iteration

        if dic_settings:
            self.settings = dic_settings

        if dic_thread_variables:
            self.thread_variables = dic_thread_variables

        self.configure()
        self.steps()

        return self.settings,\
            self.thread_variables
