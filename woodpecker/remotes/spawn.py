import woodpecker.misc.utils as utils

from woodpecker.misc.stoppablethread import StoppableThread

__author__ = 'Stefano.Romano'


class Spawn(StoppableThread):

    def __init__(self,
                 str_id,
                 str_test_name,
                 str_test_path,
                 str_scenario_folder,
                 str_server_address,
                 int_server_port,
                 dic_settings=None):
        super(Spawn, self).__init__()

        # Navigation and sender variables
        self.ID = str_id
        self.settings = dic_settings
        self.server_address = str_server_address
        self.port = int_server_port
        self.armed = False

        # Navigation class instantiation
        self.testclass = utils.import_from_path(utils.get_abs_path(str_test_path, str_scenario_folder),
                                                str_test_name,
                                                {
                                                    'scenario_folder': str_scenario_folder,
                                                    'server_address': self.server_address,
                                                    'server_port': self.port
                                                })
        self.testclass.configure()
        self.testclass.transactions()

    def run(self):
        self.armed = True
        while self.armed:
            self.testclass.run(self.ID)

    def stop(self):
        self.armed = False
