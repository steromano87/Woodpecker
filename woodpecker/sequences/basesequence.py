import abc
import datetime
import logging
import random
import sys
import time

import msgpack
import six
import verboselogs
import coloredlogs

from string import Template
from configobj import ConfigObj

from woodpecker.io.validate import Validator
from woodpecker.io.variablejar import VariableJar


class BaseSequence(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=None,
                 log_queue=six.moves.queue.Queue(),
                 variables=VariableJar(),
                 transactions=None,
                 debug=False,
                 inline_log_sinks=(sys.stdout,)):
        # Settings
        self.settings = settings or self.default_settings()

        # Variables
        self.variables = variables

        # Internal log queue
        self._log_queue = log_queue

        # Transactions (passed from outside)
        self._transactions = transactions or {}

        # Internal setup and teardown hooks
        self._setup_hooks = []
        self._teardown_hooks = []

        # Inline logger (to debug and replay the sequences)
        verboselogs.install()
        coloredlogs.install()
        self._inline_logger = logging.getLogger(self.__class__.__name__)
        if debug:
            self._inline_logger.setLevel(logging.DEBUG)
        else:
            self._inline_logger.setLevel(logging.WARNING)

        # Cycle through all the given streams and add them to logger
        for obj_log_sink in inline_log_sinks:
            obj_inline_handler = logging.StreamHandler(obj_log_sink)
            obj_inline_handler.setFormatter(
                logging.Formatter(
                    self.settings['logging']['inline_log_format']
                )
            )
            self._inline_logger.addHandler(obj_inline_handler)

    @abc.abstractmethod
    def steps(self):
        """Method to be overridden by real steps"""
        pass

    # Think times
    def think_time(self,
                   amount,
                   kind='fixed',
                   **kwargs):
        # Determine the amount of time to wait from the type of think time
        if kind == 'fixed':
            dbl_amount_final = amount
        elif kind == 'gaussian':
            dbl_std = kwargs.get('std', 0.5 * amount)
            dbl_amount_final = round(abs(random.gauss(amount, dbl_std)), 3)
        else:
            dbl_amount_final = amount

        # Now, wait
        time.sleep(dbl_amount_final)
        self._inline_logger.debug('Think time: {amount} s ({kind})'.format(
            amount=dbl_amount_final,
            kind=kind
        ))

    def log(self, message_type, log_message):
        mix_message = {
            'message_type': message_type,
            'timestamp': str(datetime.datetime.now()),
            'pecker_id': self.variables.get_pecker_id(),
            'sequence': self.variables.get_current_sequence(),
            'iteration': self.variables.get_current_iteration(),
            'message_content': log_message
        }
        if self.settings['logging']['use_compressed_logs']:
            mix_message = msgpack.packb(mix_message)
        self._log_queue.put(mix_message)
        self._log_queue.task_done()

    def log_inline(self, message, level=logging.INFO):
        self._inline_logger.log(level, message)

    def start_transaction(self, name):
        str_start_timestamp = str(datetime.datetime.now())
        self._transactions[name] = {
            'start': str_start_timestamp,
            'end': None
        }
        self.log('event', {
            'event_type': 'start_transaction',
            'event_content': {
                'transaction_name': name,
                'timestamp': str_start_timestamp
            }
        })
        self._inline_logger.debug(
            'Transaction "{transaction}" started'.format(
                transaction=name
            ))

    def end_transaction(self, name):
        try:
            str_end_timestamp = str(datetime.datetime.now())
            self._transactions[name]['end'] = str_end_timestamp
            self.log('event', {
                'event_type': 'end_transaction',
                'event_content': {
                    'transaction_name': name,
                    'timestamp': str_end_timestamp
                }
            })
            self._inline_logger.debug(
                'Transaction "{transaction}" ended'.format(
                    transaction=name
                ))
            self._transactions.pop(name)
        except KeyError:
            str_error_message = \
                'Transaction {name} set to end, but never started'.format(
                    name=name
                )
            self.log('event', {
                'event_type': 'error',
                'event_content': {
                    'message': str_error_message
                }
            })
            self._inline_logger.error(str_error_message)
            raise KeyError(str_error_message)

    def _inject_variables(self, text):
        return Template(text).safe_substitute(self.variables.dump())

    def run_steps(self):
        # If each sequence is treated as a transaction, add the sequence itself
        # to the list of active transactions
        self._inline_logger.debug('Sequence started')
        if self.settings['runtime']['each_sequence_is_transaction']:
            self.start_transaction('{sequence}_transaction'.format(
                sequence=self.__class__.__name__
            ))

        # Run the setup hooks
        for hook in self._setup_hooks:
            hook()

        self.steps()

        # Run teardown hooks
        for hook in self._teardown_hooks:
            hook()

        # If each sequence is treated as a transaction,
        # end the current sequence
        if self.settings['runtime']['each_sequence_is_transaction']:
            self.end_transaction('{sequence}_transaction'.format(
                sequence=self.__class__.__name__
            ))
        self._inline_logger.debug('Sequence ended')

        return self.settings, \
            self.variables, \
            self._transactions

    @staticmethod
    def default_settings():
        return BaseSettings()


class BaseSettings(ConfigObj):
    def __init__(self):
        super(BaseSettings, self).__init__(
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
            configspec=BaseSettings.default_settings_validator()
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
