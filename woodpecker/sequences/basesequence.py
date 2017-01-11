import six
import abc
import random
import time

from woodpecker.data.settings import BaseSettings
from woodpecker.data.variablejar import VariableJar


class BaseSequence(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=BaseSettings(),
                 log_queue=six.moves.queue(),
                 variables=VariableJar(),
                 parameters=None):
        # Settings
        self.settings = settings

        # Variables
        self.variables = variables

        # Internal log queue
        self._log_queue = log_queue

        # Parameters (passed from outside)
        self._parameters = parameters

    @abc.abstractmethod
    def steps(self):
        """Method to be overridden by real steps"""
        pass

    # Think times
    @staticmethod
    def think_time(duration='fixed',
                   amount=5,
                   **kwargs):

        # Determine the amount of time to wait from the type of think time
        if duration == 'fixed':
            dbl_amount_final = amount
        elif duration == 'gaussian':
            dbl_std = kwargs.get('std', 0.5 * amount)
            dbl_amount_final = abs(random.gauss(dbl_std))
        else:
            dbl_amount_final = amount

        # Now, wait
        time.sleep(dbl_amount_final)
