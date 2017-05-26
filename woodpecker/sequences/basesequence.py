import abc
import datetime
import logging
import random
import sys
import time
from string import Template

import coloredlogs
import msgpack
import six
import verboselogs

from woodpecker.io.variablejar import VariableJar
from woodpecker.settings.basesequencesettings import BaseSequenceSettings
from woodpecker.settings.coresettings import CoreSettings


class BaseSequence(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=None,
                 log_queue=six.moves.queue.Queue(),
                 variables=VariableJar(),
                 stopwatches=None,
                 debug=False,
                 inline_log_sinks=(sys.stdout,)):
        # Settings
        self.settings = settings or BaseSequence.default_settings()
        self.settings.merge(CoreSettings())

        # Variables
        self.variables = variables

        # Internal log queue
        self._log_queue = log_queue

        # Stopwatches (passed from outside)
        self._stopwatches = stopwatches or {}

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

    def start_stopwatch(self, name):
        str_start_timestamp = str(datetime.datetime.now())
        self._stopwatches[name] = {
            'start': str_start_timestamp,
            'end': None
        }
        self.log('event', {
            'event_type': 'start_stopwatch',
            'event_content': {
                'stopwatch_name': name,
                'timestamp': str_start_timestamp
            }
        })
        self._inline_logger.debug(
            'Stopwatch "{stopwatch}" started'.format(
                stopwatch=name
            ))

    def end_stopwatch(self, name):
        try:
            str_end_timestamp = str(datetime.datetime.now())
            self._stopwatches[name]['end'] = str_end_timestamp
            self.log('event', {
                'event_type': 'end_stopwatch',
                'event_content': {
                    'stopwatch_name': name,
                    'timestamp': str_end_timestamp
                }
            })
            self._inline_logger.debug(
                'Stopwatch "{stopwatch}" ended'.format(
                    stopwatch=name
                ))
            self._stopwatches.pop(name)
        except KeyError:
            str_error_message = \
                'Stopwatch {name} set to end, but never started'.format(
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
        # If each sequence is treated as a stopwatch, add the sequence itself
        # to the list of active stopwatches
        self._inline_logger.debug('Sequence started')
        if self.settings['runtime']['each_sequence_is_stopwatch']:
            self.start_stopwatch('{sequence}_stopwatch'.format(
                sequence=self.__class__.__name__
            ))

        # Run the setup hooks
        for hook in self._setup_hooks:
            hook()

        self.steps()

        # Run teardown hooks
        for hook in self._teardown_hooks:
            hook()

        # If each sequence is treated as a stopwatch,
        # end the current sequence
        if self.settings['runtime']['each_sequence_is_stopwatch']:
            self.end_stopwatch('{sequence}_stopwatch'.format(
                sequence=self.__class__.__name__
            ))
        self._inline_logger.debug('Sequence ended')

        return self.settings, \
            self.variables, \
            self._stopwatches

    @staticmethod
    def default_settings():
        return BaseSequenceSettings()
