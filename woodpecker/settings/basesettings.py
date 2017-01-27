from woodpecker.settings.settings import Settings


class BaseSettings(Settings):
    @staticmethod
    def default_values():
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
        }

    @staticmethod
    def validation_mask():
        return {
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
                        }
                    }
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
                    },
                    'use_compressed_logs': {
                        'type': 'boolean'
                    },
                    'inline_log_format': {
                        'type': 'string'
                    }
                }
            },
            'runtime': {
                'type': 'dict',
                'schema': {
                    'raise_error_if_variable_not_defined': {
                        'type': 'boolean'
                    },
                    'each_sequence_is_transaction': {
                        'type': 'boolean'
                    }
                }
            }
        }
