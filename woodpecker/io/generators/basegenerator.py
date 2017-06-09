import abc
import os
import six

import autopep8

from woodpecker.io.correlators.event import EventCollection


class BaseGenerator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, event_collection):

        # Text buffer for writing code
        self.buffer = six.moves.cStringIO()
        self.buffer_list = []

        # Base name for sequence generation
        self.base_sequence_name = None

        # Internal event collection from Correlator
        if not isinstance(event_collection, EventCollection):
            raise TypeError('Only EventCollection instances can be passed')
        self.events = event_collection

    def _clean_buffer(self):
        self.buffer_list.append(self.buffer)
        self.buffer = six.moves.cStringIO()

    def _dump_buffers(self, base_file_name, folder='sequences'):
        for index, buffer_item in enumerate(self.buffer_list):
            buffer_item.seek(0)
            buffer_content = buffer_item.read()
            file_content = autopep8.fix_code(buffer_content, options={
                'aggressive': 1
            })
            file_name = '{basename}_{index}.py'.format(
                basename=base_file_name,
                index=index - 1
            ) if index > 0 else '{basename}.py'.format(
                basename=base_file_name,
            )
            with open(os.path.join(folder, file_name), 'w') as fp:
                fp.write(file_content)

    @abc.abstractmethod
    def generate(self, filename, sequence_name=None):
        pass


class CommandGenerator(object):
    def __init__(self, command_name, indents=2):
        self._command = command_name
        self._arguments = []
        self._named_arguments = {}
        self._indents = indents

    def __repr__(self):
        return '{classname} - {command}'.format(
            classname=self.__class__.__name__,
            command=self._command
        )

    def add_argument(self, argument):
        self._arguments.append(argument)

    def add_named_argument(self, arg_name, arg_value):
        self._named_arguments[arg_name] = arg_value

    def generate_command(self):
        output = six.moves.cStringIO()

        # Write command
        for _ in six.moves.range(0, self._indents):
            output.write('    ')

        output.write('{command}('.format(command=self._command))

        # Write arguments
        output.write(', '.join(
            ["'{argument}'".format(argument=argument)
             for argument in self._arguments]
        ))

        # Write args separator
        if len(self._named_arguments) > 0:
            output.write(', ')

        # Write named arguments
        name_arg_list = \
            ['='.join((
                key,
                "'{value}'".format(value=value) if not isinstance(value, dict) else str(value)
            ))
             for key, value in six.iteritems(self._named_arguments)]
        output.write(', '.join(name_arg_list))

        # End writing
        output.write(')')

        # Rewind the buffer and return PEP8-formatted command
        output.seek(0)
        return output.read()
