from woodpecker.misc.stoppablethread import StoppableThread

__author__ = 'Stefano.Romano'


class Spawn(StoppableThread):

    def __init__(self, str_id, str_test_name, str_test_path):
        super(Spawn, self).__init__()
        self.ID = str_id
        self.testpath = str_test_path
        obj_module = __import__(self.testpath)
        obj_class = getattr(obj_module, self.testpath)
        self.testclass = obj_class(str_test_name)
        self.testclass.actions()
        self.armed = False

    def run(self):
        self.armed = True
        while self.armed:
            self.testclass.run(self.ID)

    def stop(self):
        self.armed = False
