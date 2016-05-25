import abc
import time
import random

from woodpecker.logging.sender import Sender

__author__ = 'Stefano.Romano'


class SimpleTransaction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        """
        Sets up base variables
        """
        self.iteration = 0
        self.navigation_name = kwargs.get('navigation_name', 'NONAME')
        self.pecker_id = ''
        self.settings = {}
        self.thread_variables = {}

        # Sender variables
        self.controller_address = kwargs.get('controller_address', 'localhost')
        self.controller_port = kwargs.get('controller_port', 7878)
        self.sender = Sender(self.controller_address, self.controller_port, 'UDP')

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
        :param str_value:
        :param str_default_key:
        """
        self.settings[str_default_key] = str_value

    def set_variable(self, str_name, str_value):
        """
        Add a variable to the thread variables dict
        :param str_value:
        :param str_name:
        """
        self.thread_variables[str_name] = str_value

    def get_variable(self, str_name):
        """
        Gets a variable from the thread variables dict
        :param str_name:
        """
        return self.thread_variables[str_name]

    @staticmethod
    def think_time(int_amount, **kwargs):
        str_type = kwargs.get('type', 'fixed')
        if str_type == 'fixed':
            time.sleep(int_amount)
        elif str_type == 'random_gaussian':
            time.sleep(abs(random.gauss(int_amount, kwargs.get('std', int_amount * 0.5))))

    def run(self, str_spawn_id, int_iteration, dic_settings=None, dic_thread_variables=None):
        self.pecker_id = str_spawn_id
        self.iteration = int_iteration

        if dic_settings:
            self.settings = dic_settings

        if dic_thread_variables:
            self.thread_variables = dic_thread_variables

        self.configure()
        self.steps()

        return self.settings,\
            self.thread_variables
