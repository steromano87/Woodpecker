import abc

from woodpecker.misc.utils import get_timestamp


class Test(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, **kwargs):
        self.name = str_testname
        self.settings = kwargs.get('settings', {})
        self.thread_variables = {}
        self.test_transactions = []
        self.uid = None

    @abc.abstractmethod
    def transactions(self):
        """Insert here the transactions to be included in the test,
        in the execution order"""
        pass

    def add_transaction(self, str_name, str_path):
        obj_transaction = {'name': str_name, 'path': str_path}
        self.test_transactions.append(obj_transaction)

    def run(self, uid=None):
        self.uid = uid
        int_iteration = 0
        for obj_transaction_item in self.test_transactions:
            obj_module = __import__(obj_transaction_item['path'])
            obj_class = getattr(obj_module, obj_transaction_item['path'])
            obj_transaction = obj_class(self.name,
                                        int_iteration,
                                        settings=self.settings,
                                        thread_variables=self.thread_variables)
            self.settings,\
                self.thread_variables = obj_transaction.run()
            del obj_transaction
            int_iteration += 1

            # This line is printed only for debug purposes
            print('ID: ' + str(self.uid) + ' Timestamp: ' + get_timestamp())
