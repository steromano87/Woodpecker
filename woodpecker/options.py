import os
import ConfigParser


class Options(object):

    def __init__(self, str_peckerfile=None):
        # Inner options container
        self._data = {}

        # Configuration file, defaults to 'Peckerfile'
        self._peckerfile = str_peckerfile or 'Peckerfile'

        # Automatically updates options from file (if present) or load default values
        self._retrieve_options()

    @staticmethod
    def _set_default_options():
        return {
            'generic': {
                'skip_think_time': False,
                'max_think_time': 5.0,
                'think_time_after_setup': 0.0,
                'think_time_between_transactions': 0.0,
                'think_time_before_teardown': 0.0,
                'think_time_between_iterations': 0.0
            },
            'http': {
                'ignore_ssl_errors': True,
                'follow_redirects': True,
                'default_request_method': 'GET',
                'default_request_headers': {},
                'default_request_cookies': {},
                'proxy': {}
            },
            'execution': {
                'spawning_mode': 'threads',
                'pecker_handling_mode': 'passive',
                'pecker_status_active_polling_interval': 0.1,
                'controller_port': 7877,
                'controller_protocol': 'TCP',
                'controller_socket_max_pending_connections': 4
            },
            'logging': {
                'max_entries_before_flush': 100,
                'logger_host': 'localhost',
                'logger_port': 7878,
                'logger_protocol': 'UDP'
            }
        }

    def _retrieve_options(self):
        if os.path.isfile('/'.join((os.getcwd(), self._peckerfile))):
            obj_conf_parser = ConfigParser.ConfigParser()
            obj_conf_parser.readfp(open(self._peckerfile))

            for str_section in obj_conf_parser.sections():
                for str_option in obj_conf_parser.options(str_section):
                    self._data.update({str_option: str_value
                                       for str_option, str_value in obj_conf_parser.get(str_section, str_option)})
        else:
            self._data.update(self._set_default_options())

    def get(self, str_section, str_option):
        return self._data.get(str_section, {}).get(str_option, None)

    def set(self, str_section, str_option, str_value):
        self._data[str_section][str_option] = str_value
