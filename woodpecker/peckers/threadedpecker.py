from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.peckers.basepecker import BasePecker


class ThreadedPecker(StoppableThread, BasePecker):

    def __init__(self, **kwargs):
        # Using old-style init calls to ensure the correct inheritance of methods
        StoppableThread.__init__(self)
        BasePecker.__init__(self, **kwargs)

    def _check_for_stop(self):
        return self.is_marked_for_stop()

    def run(self):
        self._run_all()
