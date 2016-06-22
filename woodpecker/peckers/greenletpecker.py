import gevent

from woodpecker.peckers.basepecker import BasePecker


class GreenletPecker(gevent.Greenlet, BasePecker):

    def __init__(self, **kwargs):
        gevent.Greenlet.__init__(self)
        BasePecker.__init__(self, **kwargs)
        self._marked_for_stop = False

    def mark_for_stop(self):
        self._marked_for_stop = True
        self.kill()

    def _check_for_stop(self):
        return self._marked_for_stop

    def _run(self):
        self._run_all()
