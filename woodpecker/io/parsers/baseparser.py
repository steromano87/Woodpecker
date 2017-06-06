import abc
import os
import msgpack
import simplejson

import woodpecker.misc.functions as functions


class BaseParser(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, filename):
        self._file_path = os.path.abspath(filename)
        self._import_file(self._file_path)

        self._parsed = {
            'start_time': None,
            'entries': []
        }

    @abc.abstractmethod
    def parse(self):
        pass

    @abc.abstractmethod
    def _import_file(self, filename):
        pass
