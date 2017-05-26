import abc
import os

import msgpack
import simplejson

import woodpecker.misc.functions as functions


class BaseCorrelator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parsed_entries):
        self._correlated = None

        if isinstance(parsed_entries, dict):
            # If a dict is passed, instance it directly
            self._parsed_entries = parsed_entries
        elif isinstance(parsed_entries, str):
            filename = os.path.abspath(parsed_entries)
            # If a string is passed, try to load the specified file
            try:
                with open(filename, 'r') as fp:
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
        except IOError:
            self._parsed_entries = simplejson.load(
                stream, object_hook=functions.decode_datetime, encoding='UTF-8'
            )

    @abc.abstractmethod
    def correlate(self):
        pass
