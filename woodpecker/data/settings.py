import os
import six
import abc
import pprint

import yaml
import cerberus


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

        # Validation mask
        self._validation_mask = {} \
            if not self._validation_mask \
            else self._validation_mask

        # Internal validator
        self._validator = cerberus.Validator(self._validation_mask,
                                             purge_unknown=True,
                                             allow_unknown=False)

        # Load settings data
        self.load()

    def load(self):
        if os.path.isfile(self._peckerfile):
            with open(self._peckerfile, 'r') as fp:
                self._data = self._validator.validated(yaml.safe_load(fp))
        else:
            self._data = self._validator.validated({})

    def save(self):
        with open(self._peckerfile, 'w') as pf:
            yaml.dump(self._data, stream=pf)

    def get(self, section, entry):
        if section in six.viewkeys(self._data):
            if entry in six.viewkeys(self._data.get(section, {})):
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
        dic_setting = {section: {entry: value}}
        if self._validator.validate(dic_setting) \
                and section in six.viewkeys(self._data) \
                and entry in six.viewkeys(self._data.get(section, {})):
            self._data[section][entry] = value
        else:
            raise ValueError('Error in input values:\n{error_list}'.format(
                error_list=pprint.pformat(self._validator.errors, indent=2)
            ))

    def dump(self):
        return self._data

    def validate(self):
        try:
            return self._validator.validate(self._data), \
                   pprint.pprint(self._validator.errors)
        except cerberus.DocumentError as error:
            return False, str(error)

    def extend(self, additional_settings):
        if isinstance(additional_settings, Settings):
            additional_settings.load()
            bool_is_valid, str_message = additional_settings.validate()
            if bool_is_valid:
                self._validation_mask.update(
                    additional_settings._validation_mask
                )
            else:
                raise ValueError('Given settings are not self-consistent:\n'
                                 '{errors}'.format(errors=str_message)
                                 )
        else:
            raise TypeError('Wrong type: provided settings are not an '
                            'instance of Woodpecker settings')
        # Reload and validate default settings
        self._data = self._validator.validated(self._data)


class BaseSettings(Settings):
    """
    Base settings for Woodpecker
    """
    def __init__(self, peckerfile='Peckerfile'):
        self._validation_mask = {
            'timing': {
                'type': 'dict',
                'schema': {
                    'skip_think_time': {
                        'type': 'boolean'
                    },
                    'max_think_time': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    },
                    'think_time_after_setup': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    },
                    'think_time_between_transactions': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    },
                    'think_time_before_teardown': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    },
                    'think_time_between_iterations': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    }
                },
                'default': {
                    'skip_think_time': False,
                    'max_think_time': 5.0,
                    'think_time_after_setup': 0.0,
                    'think_time_between_transactions': 0.0,
                    'think_time_before_teardown': 0.0,
                    'think_time_between_iterations': 0.0

                }
            },
            'network': {
                'type': 'dict',
                'schema': {
                    'controller_port': {
                        'type': 'integer',
                        'min': 1,
                        'max': 65536
                    },
                    'max_pending_connections': {
                        'type': 'integer',
                        'min': 1
                    }
                },
                'default': {
                    'controller_port': 7877,
                    'max_pending_connections': 4

                }
            },
            'spawning': {
                'type': 'dict',
                'schema': {
                    'spawning_mode': {
                        'type': 'string',
                        'allowed': [
                            'processes',
                            'threads',
                            'greenlets'
                        ]
                    },
                    'pecker_handling_mode': {
                        'type': 'string',
                        'allowed': [
                            'passive',
                            'active'
                        ]
                    },
                    'pecker_status_active_polling_interval': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    },
                    'spawners': {
                        'type': 'list',
                        'schema': {
                            'type': 'string'
                        },
                        'coerce': list
                    }
                },
                'default': {
                    'spawning_mode': 'threads',
                    'pecker_handling_mode': 'passive',
                    'pecker_status_active_polling_interval': 0.1,
                    'spawners': [
                        'localhost'
                    ]

                }
            },
            'logging': {
                'type': 'dict',
                'schema': {
                    'max_entries_before_flush': {
                        'type': 'integer',
                        'min': 0
                    },
                    'max_interval_before_flush': {
                        'type': 'number',
                        'min': 0,
                        'coerce': float
                    },
                    'results_file': {
                        'type': 'string',
                        'regex': r"[^\/\\]+"
                    },
                    'sysmonitor_polling_interval': {
                        'type': 'number',
                        'min': 0,
                        'coerce': float
                    }
                },
                'default': {
                    'max_entries_before_flush': 10,
                    'max_interval_before_flush': 30.0,
                    'results_file': 'results.sqlite',
                    'sysmonitor_polling_interval': 5.0
                }
            },
            'runtime': {
                'type': 'dict',
                'schema': {
                    'raise_error_if_variable_not_defined': {
                        'type': 'boolean'
                    }
                },
                'default': {
                    'raise_error_if_variable_not_defined': False
                }
            }
        }
        super(BaseSettings, self).__init__(peckerfile)
