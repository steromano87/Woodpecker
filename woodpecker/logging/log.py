from woodpecker.logging.sender import Sender
from woodpecker.options import Options


class Log(object):

    def __init__(self, **kwargs):
        # Internal data storage
        self._data = self._get_clean_log()

        # Internal data count, used to provide faster access to data size
        self._data_count = 0

        # Internal options
        self._options = kwargs.get('options', Options())

        # Internal sender to flush data
        self._sender = Sender(self._options.get('logging', 'logger_host'),
                              self._options.get('logging', 'logger_port'),
                              self._options.get('logging', 'logger_protocol'))

    @staticmethod
    def _get_clean_log():
        return {
            'steps': [],
            'events': [],
            'peckers': [],
            'sysmonitor': [],
            'transactions': [],
            'sla': []
        }

    def append_to(self, str_section, dic_value):
        self._data[str_section].append(dic_value)
        self._data_count += 1
        # Automatic data flushing
        if self._data_count > self._options.get('logging',
                                                'max_entries_before_flush'):
            self.flush()

    def flush(self):
        # Send data with sender
        self._sender.send('log', self._data)
        # Clean log
        self._data = self._get_clean_log()
        self._data_count = 0

    def __del__(self):
        self.flush()
