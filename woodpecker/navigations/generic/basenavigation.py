import abc

import woodpecker.misc.utils as utils


class BaseNavigation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        # Navigation settings
        self.options = kwargs.get('options', {})

        # Pecker variables shared between transactions
        self.pecker_variables = kwargs.get('pecker_variables', {})

        # Internal iteration counter, can be passed from outside
        self.iteration = kwargs.get('iteration', 0)

        # Maximum iterations number
        self.max_iterations = kwargs.get('max_iterations', 0)

        # Navigation name
        self.navigation_name = self.__class__.__name__

        # Internal pecker ID
        self.pecker_id = kwargs.get('pecker_id', None)

        # Transactions
        self._transactions = []

        # Internal log, used to send data at the end of the navigation
        self.log = kwargs.get('log', {
            'steps': [],
            'events': [],
            'peckers': [],
            'sysmonitor': [],
            'transactions': [],
            'sla': []
        })

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

    # Options methods
    def set_option(self, str_name, str_value):
        self.options[str_name] = str_value

    def get_option(self, str_name, mix_default=None):
        return self.options.get(str_name, mix_default)

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

    def add_transaction(self, str_name, str_path):
        self._transactions.append({
            'name': str_name,
            'path': str_path
        })

    def run(self):
        # First, configure the navigation
        self.configure()

        # Then, add transactions
        self.transactions()

        # Then, start running the transactions in order
        while self.iteration <= self.max_iterations or self.max_iterations == 0:
            for dic_transaction in self._transactions:
                obj_current_transaction = utils.import_from_path(
                    dic_transaction['path'],
                    dic_transaction['name'],
                    {
                        'options': self.options,
                        'pecker_variables': self.pecker_variables,
                        'iteration': self.iteration,
                        'max_iterations': self.max_iterations,
                        'navigation_name': self.navigation_name,
                        'pecker_id': self.pecker_id,
                        'log': self.log
                    }
                )

                self.options, self.pecker_variables, self.log = obj_current_transaction.run()

            self.iteration += 1
