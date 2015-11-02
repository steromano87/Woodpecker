import abc
import os

import woodpecker.misc.utils as utils


class Test(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        self.name = kwargs.get('test_name', self.__class__.__name__)

        self.settings = kwargs.get('settings', {})
        self.scenario_folder = kwargs.get('scenario_folder', os.getcwd())
        self.thread_variables = {}
        self.test_transactions = []
        self.spawn_id = None
        self.iteration = 0

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
        obj_transaction = {'name': str_name, 'path': utils.get_abs_path(str_path, self.scenario_folder)}
        self.test_transactions.append(obj_transaction)

    def run(self, str_spawn_id=None):
        self.spawn_id = str_spawn_id
        self.iteration = 1
        for obj_transaction_item in self.test_transactions:
            obj_class = utils.import_from_path(os.path.abspath(obj_transaction_item['path']),
                                               obj_transaction_item['name'])
            obj_transaction = obj_class(self.name,
                                        self.spawn_id,
                                        self.iteration,
                                        self.settings,
                                        self.thread_variables)
            self.settings,\
                self.thread_variables = obj_transaction.run()
            del obj_transaction

        self.iteration += 1

        # This line is printed only for debug purposes
        print('ID: ' + str(self.spawn_id) + ' Timestamp: ' + utils.get_timestamp())
