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
        self.scenario_folder = kwargs.get('scenario_folder',
                                          utils.get_abs_path('/'.join(
                                              (
                                                  os.getcwd(),
                                                  '..'
                                              )
                                          )))

        # Sender data
        self.controller_address = kwargs.get('controller_address', 'localhost')
        self.controller_port = kwargs.get('controller_port', 7878)
        self.sender = Sender(self.controller_address, self.controller_port, 'UDP')

        # Internal variables
        self.thread_variables = {}
        self.test_transactions = []
        self.pecker_id = None
        self.iteration = 1
        self.debug = False

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

    def add_transaction(self, str_name, str_path):
        str_abspath = utils.get_abs_path(str_path, self.scenario_folder)
        obj_transaction = {
            'name': str_name,
            'path': str_abspath,
            'class': utils.import_from_path(str_abspath, str_name, {'navigation_name': self.name}),
            'controller_address': self.controller_address,
            'controller_port': self.controller_port
        }
        self.test_transactions.append(obj_transaction)

    def run(self, str_pecker_id=None):
        self.pecker_id = str_pecker_id

        # Cycle through transactions
        for obj_transaction_item in self.test_transactions:
            # Send transaction start message
            self.sender.send('transactionStart',
                             {
                                 'hostName': utils.get_ip_address(),
                                 'peckerID': self.pecker_id,
                                 'navigationName': self.name,
                                 'iteration': self.iteration,
                                 'transactionName': obj_transaction_item['name'],
                                 'startTimestamp': utils.get_timestamp()
                             })

            # Run the transaction
            self.settings,\
                self.thread_variables = \
                obj_transaction_item['class'].run(self.pecker_id, self.iteration, self.settings, self.thread_variables)

            # Send transaction end message
            self.sender.send('transactionEnd',
                             {
                                 'hostName': utils.get_ip_address(),
                                 'peckerID': self.pecker_id,
                                 'navigationName': self.name,
                                 'iteration': self.iteration,
                                 'transactionName': obj_transaction_item['name'],
                                 'endTimestamp': utils.get_timestamp()
                             })

        self.iteration += 1

        # Print line if in Debug mode
        if self.debug:
            print('ID: ' + str(self.pecker_id) + ' Timestamp: ' + utils.get_timestamp())
