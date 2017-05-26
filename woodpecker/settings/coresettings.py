from configobj import ConfigObj

from woodpecker.misc.contrib.validate import Validator


class CoreSettings(ConfigObj):
    def __init__(self, **kwargs):
        super(CoreSettings, self).__init__(
            {
                'timing': {
                    'skip_think_time': False,
                    'max_think_time': 5.0,
                    'think_time_after_setup': 0.0,
                    'think_time_between_sequences': 0.0,
                    'think_time_before_teardown': 0.0,
                    'think_time_between_iterations': 0.0
                },
                'network': {
                    'controller_port': 7877,
                    'max_pending_connections': 4
                },
                'logging': {
                    'max_entries_before_flush': 10,
                    'max_interval_before_flush': 30.0,
                    'results_file': 'results.sqlite',
                    'sysmonitor_polling_interval': 5.0,
                    'use_compressed_logs': True,
                    'inline_log_format':
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'spawning': {
                    'spawning_mode': 'threads',
                    'pecker_handling_mode': 'passive',
                    'pecker_status_active_polling_interval': 0.1,
                    'spawners': [
                        'localhost'
                    ]
                },
                'runtime': {
                    'raise_error_if_variable_not_defined': False,
                    'each_sequence_is_transaction': True
                }
            },
            interpolation=False,
            configspec=CoreSettings.default_settings_validator(),
            **kwargs
        )

        self.validator = Validator()

    @staticmethod
    def default_settings_validator():
        return ConfigObj({
            'timing': {
                'skip_think_time': 'boolean(default=False)',
                'max_think_time': 'float(min=0.0, default=5.0)',
                'think_time_after_setup': 'float(min=0.0, default=0.0)',
                'think_time_between_sequences': 'float(min=0.0, default=0.0)',
                'think_time_before_teardown': 'float(min=0.0, default=0.0)',
                'think_time_between_iterations': 'float(min=0.0, default=0.0)'
            },
            'network': {
                'controller_port': 'integer(min=1, max=65535 default=7878)',
                'max_pending_connections': 'integer(min=1, default=4)'
            },
            'logging': {
                'max_entries_before_flush': 'integer(min=0, default=30)',
                'max_interval_before_flush': 'float(min=0.0, default=30.0)',
                'results_file': "string(default='results.sqlite')",
                'sysmonitor_polling_interval': 'float(min=0.0, default=5.0)',
                'use_compressed_logs': 'boolean(default=True)',
                'inline_log_format':
                    "string(default='%(asctime)s - %(name)s - "
                    "%(levelname)s - %(message)s')"
            },
            'spawning': {
                'spawning_mode': "option('threads', 'processes', "
                                 "'greenlets', default='threads')",
                'pecker_handling_mode': "option('passive', 'active', "
                                        "default='passive')",
                'pecker_status_active_polling_interval':
                    'float(min=0.0, default=0.1)',
                'spawners': "string_list(min=1, default=['localhost'])"
            },
            'runtime': {
                'raise_error_if_variable_not_defined':
                    'boolean(default=False)',
                'each_sequence_is_transaction': 'boolean(default=True)'
            }
        }, interpolation=False)
