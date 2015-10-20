import abc
import requests
from woodpecker.misc.utils import get_timestamp


class Test(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, **kwargs):
        self.name = str_testname
        self.settings = kwargs.get('settings', {})
        self.session = requests.Session()
        self.last_response = False
        self.thread_variables = {}
        self.test_actions = []
        self.uid = None

    @abc.abstractmethod
    def actions(self):
        """Insert here the actions to be included in the test,
        in the execution order"""
        pass

    def add_action(self, str_name, str_path):
        obj_action = {'name': str_name, 'path': str_path}
        self.test_actions.append(obj_action)

    def run(self, uid=None):
        self.uid = uid
        int_iteration = 0
        for obj_action_item in self.test_actions:
            obj_module = __import__(obj_action_item['path'])
            obj_class = getattr(obj_module, obj_action_item['path'])
            obj_action = obj_class(self.name,
                                   int_iteration,
                                   settings=self.settings,
                                   session=self.session,
                                   last_response=self.last_response,
                                   thread_variables=self.thread_variables)
            self.settings,\
                self.session,\
                self.last_response,\
                self.thread_variables = obj_action.run()
            del obj_action
            int_iteration += 1

            # This line is printed only for debug purposes
            print('ID: ' + str(self.uid) + ' Timestamp: ' + get_timestamp())
