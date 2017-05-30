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

        if isinstance(parsed_entries, dict):
            # If a dict is passed, instance it directly
            self._parsed_entries = parsed_entries
        elif isinstance(parsed_entries, str):
            filename = os.path.abspath(parsed_entries)
            # If a string is passed, try to load the specified file
            try:
                with open(filename) as fp:
                    self._load_file(fp)
            except IOError:
                raise IOError('File "{file_path}" not found'.format(
                    file_path=filename
                ))
        else:
            raise IOError('Unsupported input type')

    def _load_file(self, stream):
        try:
            self._parsed_entries = msgpack.load(
                stream, object_hook=functions.decode_datetime
            )
        except ValueError:
            self._parsed_entries = simplejson.load(
                stream, object_hook=functions.decode_datetime
            )

    def _fix_code(self):
        self.buffer.seek(0)
        return autopep8.fix_code(self.buffer.read())

    @abc.abstractmethod
    def generate(self, filename, sequence_name='NewSequence'):
        pass
