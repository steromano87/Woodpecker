import os
import six
import abc

import yaml


class Settings(object):
    """
    Abstract class that is subclassed by the settings specific
     to each transaction type
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, peckerfile='Peckerfile'):
        # Absolute path to Peckerfile
        self._peckerfile = os.path.abspath(peckerfile)

        # Settings data
        self._data = {}

        # Load settings data
        self.load()

    def load(self):
        if os.path.isfile(self._peckerfile):
            with open(self._peckerfile, 'r') as fp:
                self._data = yaml.safe_load(fp)
        else:
            self._data = self.default_settings()

    def save(self):
        with open(self._peckerfile, 'w') as pf:
            yaml.dump(self._data, stream=pf)

    def get(self, section, entry):
        if section in six.viewkeys(self._data):
            if entry in six.viewkeys(self._data.get(section)):
                return self._data.get(section).get(entry)
            else:
                raise KeyError(
                    'The entry {entry} does not exist ',
                    'in section {section}'.format(entry=entry, section=section)
                )
        else:
            raise KeyError('The section {section} does not exist'.format(
                section=section
            ))

    def set(self, section, entry, value):
        if section in six.viewkeys(self._data):
            if entry in six.viewkeys(self._data.get(section)):
                self._data[section][entry] = value
            else:
                raise KeyError(
                    'The entry {entry} does not exist ',
                    'in section {section}'.format(entry=entry, section=section)
                )
        else:
            raise KeyError('The section {section} does not exist'.format(
                section=section
            ))

    def dump(self):
        return self._data

    def extend(self, additional_settings):
        if isinstance(additional_settings, Settings):
            self._data.update(additional_settings.dump())
        else:
            raise TypeError('Wrong type: provided settings are not an '
                            'instance of Woodpecker settings')

    @staticmethod
    @abc.abstractmethod
    def default_settings():
        pass


class BaseSettings(Settings):
    """
    Base settings for Woodpecker
    """
    @staticmethod
    def default_settings():
        return {
            'timing': {
                'skip_think_time': False,
                'max_think_time': 5.0,
                'think_time_after_setup': 0.0,
                'think_time_between_transactions': 0.0,
                'think_time_before_teardown': 0.0,
                'think_time_between_iterations': 0.0
            },
            'network': {
                'controller_port': 7877,
                'max_pending_connections': 4
            },
            'spawning': {
                'spawning_mode': 'threads',
                'pecker_handling_mode': 'passive',
                'pecker_status_active_polling_interval': 0.1,
                'spawners': [
                    'localhost'
                ]
            },
            'logging': {
                'max_entries_before_flush': 10,
                'max_interval_before_flush': 30.0,
                'results_file': 'results',
                'sysmonitor_polling_interval': 5.0
            }
        }
