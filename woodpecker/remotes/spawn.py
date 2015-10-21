from woodpecker.misc.stoppablethread import StoppableThread

__author__ = 'Stefano.Romano'


class Spawn(StoppableThread):

    def __init__(self, str_id, str_test_name, str_test_path, dic_settings):
        super(Spawn, self).__init__()
        self.ID = str_id
        obj_module = __import__(str_test_path)
        obj_class = getattr(obj_module, str_test_path)
        self.testclass = obj_class(str_test_name, dic_settings)
        self.testclass.configure()
        self.testclass.transactions()
        self.armed = False

    def run(self):
        self.armed = True
        while self.armed:
            self.testclass.run(self.ID)

    def stop(self):
        self.armed = False
