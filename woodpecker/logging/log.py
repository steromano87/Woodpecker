from woodpecker.logging.sender import Sender
from woodpecker.options import Options


class Log(object):

    def __init__(self, **kwargs):
        # Internal data storage
        self._data = self._get_clean_log()

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
        # Automatic data flushing
        if self.get_record_count() > self._options.get('logging', 'max_entries_before_flush'):
            self.flush()

    def get_record_count(self):
        return sum([len(lst_section) for lst_section in self._data.iterkeys()])

    def flush(self):
        # Send data with sender
        self._sender.send('log', self._data)
        # Clean log
        self._data = self._get_clean_log()
