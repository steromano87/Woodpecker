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

    def parse_to_file(self, filename=None, binary=True):
        output_file_path = \
            filename or \
            '.'.join((
                os.path.splitext(self._file_path)[0],
                'pel'
            ))
        with open(output_file_path, 'w+') as fp:
            if binary:
                msgpack.dump(self.parse(),
                             fp,
                             default=functions.encode_datetime)
            else:
                simplejson.dump(self.parse(),
                                fp,
                                default=functions.encode_datetime,
                                indent='\t')

    @abc.abstractmethod
    def _import_file(self, filename):
        pass
