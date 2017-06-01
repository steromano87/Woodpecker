import abc
import os
import six

import msgpack
import simplejson
import autopep8

import woodpecker.misc.functions as functions


class BaseGenerator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parsed_entries):

        # Text buffer for writing code
        self.buffer = six.moves.cStringIO()
        self.buffer_list = []

        # Base name for sequence generation
        self.base_sequence_name = None

        # Internal parsed entries from Correlator
        self._parsed_entries = parsed_entries

    def _clean_buffer(self):
        self.buffer_list.append(self.buffer)
        self.buffer = six.moves.cStringIO()

    def _dump_buffers(self, base_file_name, folder='sequences'):
        for index, buffer_item in enumerate(self.buffer_list):
            buffer_item.seek(0)
            file_content = autopep8.fix_code(buffer_item.read(), options={
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
