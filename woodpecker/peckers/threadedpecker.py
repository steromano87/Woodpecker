import threading

from woodpecker.peckers.basepecker import BasePecker


class ThreadedPecker(threading.Thread, BasePecker):

    def __init__(self):
        super(ThreadedPecker, self).__init__()
        self.locals = threading.local()
        self.locals.stop_after_iteration = False

    def _check_for_stop(self):
        return self.locals.stop_after_iteration
