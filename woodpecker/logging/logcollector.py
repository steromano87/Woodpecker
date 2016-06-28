import os

from woodpecker.logging.dbwriter import DBWriter
from woodpecker.misc.stoppablethread import StoppableThread
from woodpecker.options import Options
from woodpecker.logging.messenger import Messenger


class LogCollector(StoppableThread):

    def __init__(self, **kwargs):
        super(LogCollector, self).__init__()

        # Scenario folder
        self._scenario_folder = kwargs.get('scenario_folder', os.getcwd())

        # Options
        self._options = kwargs.get('options', Options())

        # Results file name
        self._results_file = '.'.join((
            '/'.join((
                self._scenario_folder,
                'results',
                kwargs.get('results_file', 'results')
            )),
            'sqlite'
        ))

        # Internal DBWriter
        self._dbwriter = DBWriter(self._results_file)

        # Internal messenger
        self._messenger = \
            Messenger(self._options.get('logging', 'logger_port'),
                      self._options.get('logging', 'logger_protocol'),
                      self._options.get('logging',
                                        'logger_socket_max_pending_connections')
                      )

        # Socket data
        self.message = None

    def _handle_data(self):
        for str_section, lst_data in self.message['payload'].iteritems():
            if len(lst_data) > 0:
                self._dbwriter.insert_in_section(str_section, lst_data)

    def run(self):
        # Run until marked for stop
        while True:
            if not self.is_marked_for_stop():
                self.message = self._messenger.listen()
                self._handle_data()
            else:
                break
