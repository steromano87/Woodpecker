import abc
import importlib
import time

from woodpecker.options import Options
from woodpecker.logging.log import Log


class Navigation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        # Navigation settings
        self.options = kwargs.get('options', None) or Options()

        # Pecker variables shared between transactions
        self.pecker_variables = kwargs.get('pecker_variables', {})

        # Internal iteration counter
        self.iteration = 1

        # Navigation name
        self.navigation_name = self.__class__.__name__

        # Internal pecker ID
        self.pecker_id = kwargs.get('pecker_id', None)

        # Transactions
        self._transactions = []

        # Setup transactions
        self._setup_transactions = []

        # TearDown transactions
        self._teardown_transactions = []

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

    # Configuration
    def configure(self):
        pass

    # Transaction methods
    @abc.abstractmethod
    def transactions(self):
        """
        Insert here the transactions to be included in the test,
        in the execution order
        """
        pass

    def add_transaction(self, str_name, str_file, **kwargs):
        dic_transaction = {
            'name': str_name,
            'file': str_file
        }
        if kwargs.get('type', None) == 'setup':
            self._setup_transactions.append(dic_transaction)
        elif kwargs.get('type', None) == 'teardown':
            self._teardown_transactions.append(dic_transaction)
        else:
            self._transactions.append(dic_transaction)

    def prepare_for_run(self):
        # First, configure the navigation
        self.configure()

        # Then, add transactions
        self.transactions()

    def run_setup(self):
        # If any setup is present, run it
        for dic_setup in self._setup_transactions:
            self._run_transaction(dic_setup)
        time.sleep(self.options.get('generic', 'think_time_after_setup'))
        return self.log

    def run_main(self, int_iteration):
        self.iteration = int_iteration
        for dic_transaction in self._transactions:
            self._run_transaction(dic_transaction)
            time.sleep(self.options.get('generic', 'think_time_between_transactions'))

        time.sleep(self.options.get('generic', 'think_time_between_iterations'))
        return self.log

    def run_teardown(self):
        # If any teardown is present, run it
        time.sleep(self.options.get('generic', 'think_time_before_teardown'))
        for dic_setup in self._teardown_transactions:
            self._run_transaction(dic_setup)
        return self.log

    def _run_transaction(self, dic_transaction):
        # Import the module containing the transaction class
        obj_transaction_module = importlib.import_module(''.join(('.', dic_transaction['file'])),
                                                         'tests.scenario_test_new.transactions')

        # Get an instance of the transaction class
        obj_current_transaction = getattr(obj_transaction_module, dic_transaction['name'])(
            **{
                'options': self.options,
                'pecker_variables': self.pecker_variables,
                'iteration': self.iteration,
                'navigation_name': self.navigation_name,
                'pecker_id': self.pecker_id,
                'log': self.log
            }
        )

        self.options, self.pecker_variables, self.log = obj_current_transaction.run(self.iteration)
