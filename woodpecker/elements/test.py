import abc

from woodpecker.misc.utils import get_timestamp


class Test(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, **kwargs):
        self.name = str_testname
        self.settings = kwargs.get('settings', {})
        self.thread_variables = {}
        self.test_transactions = []
        self.spawn_id = None
        self.iteration = 0

    @abc.abstractmethod
    def transactions(self):
        """Insert here the transactions to be included in the test,
        in the execution order"""
        pass

    def configure(self):
        pass

    def add_transaction(self, str_name, str_path):
        obj_transaction = {'name': str_name, 'path': str_path}
        self.test_transactions.append(obj_transaction)

    def run(self, str_spawn_id=None):
        self.spawn_id = str_spawn_id
        self.iteration = 1
        for obj_transaction_item in self.test_transactions:
            obj_module = __import__(obj_transaction_item['path'])
            obj_class = getattr(obj_module, obj_transaction_item['path'])
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
            print('ID: ' + str(self.spawn_id) + ' Timestamp: ' + get_timestamp())
