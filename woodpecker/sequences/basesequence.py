import abc
import datetime
import logging
import random
import sys
import time

import msgpack
import six
import gevent

from woodpecker.data.variablejar import VariableJar
from woodpecker.settings.basesettings import BaseSettings


class BaseSequence(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=BaseSettings(),
                 log_queue=six.moves.queue.Queue(),
                 variables=VariableJar(),
                 parameters=None,
                 transactions=None,
                 debug=False,
                 inline_log_sinks=(sys.stdout,)):
        # Settings
        self.settings = settings

        # Variables
        self.variables = variables

        # Internal log queue
        self._log_queue = log_queue

        # Parameters (passed from outside)
        self._parameters = parameters or {}

        # Transactions (passed from outside)
        self._transactions = transactions or {}

        # Async Greenlets pool
        self._async_greenlets = []

        # Inline logger (to debug and replay the sequences)
        self._inline_logger = logging.getLogger(self.__class__.__name__)
        if debug:
            self._inline_logger.setLevel(logging.DEBUG)
        else:
            self._inline_logger.setLevel(logging.INFO)

        # Cycle through all the given streams and add them to logger
        for obj_log_sink in inline_log_sinks:
            obj_inline_handler = logging.StreamHandler(obj_log_sink)
            obj_inline_handler.setFormatter(
                logging.Formatter(
                    self.settings.get('logging', 'inline_log_format')
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
            dbl_amount_final = abs(random.gauss(dbl_std))
        else:
            dbl_amount_final = amount

        # Now, wait
        time.sleep(dbl_amount_final)
        self._inline_logger.debug('Think time: {amount} ({kind})'.format(
            amount=amount,
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
        if self.settings.get('logging', 'use_compressed_logs'):
            mix_message = msgpack.packb(mix_message)
        self._log_queue.put(mix_message)
        self._log_queue.task_done()

    def log_inline(self, level, message):
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

    @staticmethod
    def default_settings():
        return BaseSettings()

    def run_steps(self):
        # If each sequence is treated as a transaction, add the sequence itself
        # to the list of active transactions
        if self.settings.get('runtime', 'each_sequence_is_transaction'):
            self.start_transaction('{sequence}_transaction'.format(
                sequence=self.__class__.__name__
            ))

        self._inline_logger.debug('Sequence started')
        self.steps()
        gevent.joinall(self._async_greenlets)
        self._inline_logger.debug('Sequence ended')

        # If each sequence is treated as a transaction, end the current sequence
        if self.settings.get('runtime', 'each_sequence_is_transaction'):
            self.end_transaction('{sequence}_transaction'.format(
                sequence=self.__class__.__name__
            ))

        return self.settings, \
            self.variables, \
            self._parameters, \
            self._transactions
