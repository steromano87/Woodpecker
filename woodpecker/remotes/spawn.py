import woodpecker.misc.utils as utils

from woodpecker.misc.stoppablethread_old import StoppableThread

__author__ = 'Stefano.Romano'


class Spawn(StoppableThread):

    def __init__(self,
                 str_id,
                 str_navigation_name,
                 str_navigation_path,
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
        self.navclass = utils.import_from_path(utils.get_abs_path(str_navigation_path, str_scenario_folder),
                                               str_navigation_name,
                                               {
                                                   'scenario_folder': str_scenario_folder,
                                                   'controller_address': self.server_address,
                                                   'controller_port': self.port
                                               })
        self.navclass.configure()
        self.navclass.transactions()

    def run(self):
        self.armed = True
        while self.armed:
            self.navclass.run(self.ID)

    def stop(self):
        self.armed = False
