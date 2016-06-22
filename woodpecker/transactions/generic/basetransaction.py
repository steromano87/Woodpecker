import abc
import time
import random

from woodpecker.options import Options
from woodpecker.logging.log import Log


class BaseTransaction(object):
    __metaclass__ = abc.ABCMeta

    # Initialization
    def __init__(self, **kwargs):
        # Navigation settings
        self.options = kwargs.get('options', None) or Options()

        # Pecker variables shared between transactions
        self.pecker_variables = kwargs.get('pecker_variables', {})

        # Internal iteration counter
        self.iteration = 1

        # Navigation name
        self.navigation_name = kwargs.get('navigation_name', None)

        # Transaction name
        self.transaction_name = self.__class__.__name__

        # Internal pecker ID
        self.pecker_id = kwargs.get('pecker_id', None)

        # Internal log, used to send data at the end of the navigation
        self.log = kwargs.get('log', Log())

    # Variables methods
    def set_variable(self, str_name, mix_value):
        self.pecker_variables[str_name] = mix_value

    def get_variable(self, str_name, mix_default=None):
        return self.pecker_variables.get(str_name, mix_default)

    def exist_variable(self, str_name):
        if self.pecker_variables.get(str_name, None):
            return True
        else:
            return False

    def import_variable_from_file(self, str_file_path, **kwargs):
        # TODO: add variable retrieval from file (like LoadRunner's parameters)
        pass

    # Think times
    @staticmethod
    def think_time(dbl_amount, **kwargs):
        str_type = kwargs.get('type', 'fixed')

        # Determine the amount of time to wait from the type of think time
        if str_type == 'fixed':
            dbl_amount_final = dbl_amount
        elif str_type == 'random_gaussian':
            dbl_std = kwargs.get('std', 0.5 * dbl_amount)
            dbl_amount_final = abs(random.gauss(dbl_std))
        else:
            dbl_amount_final = dbl_amount

        # Now, wait
        time.sleep(dbl_amount_final)

    # Configuration of transaction
    def configure(self):
        pass

    @abc.abstractmethod
    def steps(self):
        pass

    def check_assertions(self, dic_assertions):
        # TODO: add assertions support
        return None

    def run(self, int_iteration):
        self.iteration = int_iteration

        # First, configure the transaction if some is present
        self.configure()
        self.steps()

        return self.options, self.pecker_variables, self.log
