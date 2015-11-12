import abc
import os

import woodpecker.misc.utils as utils

from woodpecker.logging.sender import Sender


class Navigation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        # Navigation name, defaults to class name
        self.name = kwargs.get('navigation_name', self.__class__.__name__)

        # Navigation settings and scenario
        self.settings = kwargs.get('settings', {})
        self.scenario_folder = kwargs.get('scenario_folder', os.getcwd())

        # Sender data
        self.server_address = kwargs.get('server_address', 'localhost')
        self.server_port = kwargs.get('server_port', 7878)
        self.sender = Sender(self.server_address, self.server_port, 'UDP')

        # Internal variables
        self.thread_variables = {}
        self.test_transactions = []
        self.spawn_id = None
        self.iteration = 1

    @abc.abstractmethod
    def transactions(self):
        """
        Insert here the transactions to be included in the test,
        in the execution order
        """
        pass

    def configure(self):
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

    def add_transaction(self, str_name, str_path):
        str_abspath = utils.get_abs_path(str_path, self.scenario_folder)
        obj_transaction = {
            'name': str_name,
            'path': str_abspath,
            'class': utils.import_from_path(str_abspath, str_name, {'navigation_name': self.name}),
            'server_address': self.server_address,
            'server_port': self.server_port
        }
        self.test_transactions.append(obj_transaction)

    def run(self, str_spawn_id=None):
        self.spawn_id = str_spawn_id

        # Cycle through transactions
        for obj_transaction_item in self.test_transactions:
            # Send transaction start message
            self.sender.send('transactionStart',
                             {
                                 'hostName': utils.get_ip_address(),
                                 'spawnID': self.spawn_id,
                                 'testName': self.name,
                                 'iteration': self.iteration,
                                 'transactionName': obj_transaction_item['name'],
                                 'startTimestamp': utils.get_timestamp()
                             })

            # Run the transaction
            self.settings,\
                self.thread_variables = \
                obj_transaction_item['class'].run(self.spawn_id, self.iteration, self.settings, self.thread_variables)

            # Send transaction end message
            self.sender.send('transactionEnd',
                             {
                                 'hostName': utils.get_ip_address(),
                                 'spawnID': self.spawn_id,
                                 'testName': self.name,
                                 'iteration': self.iteration,
                                 'transactionName': obj_transaction_item['name'],
                                 'endTimestamp': utils.get_timestamp()
                             })

        self.iteration += 1

        # This line is printed only for debug purposes
        print('ID: ' + str(self.spawn_id) + ' Timestamp: ' + utils.get_timestamp())
