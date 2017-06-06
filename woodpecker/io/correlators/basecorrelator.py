import abc
import os

import msgpack
import simplejson

import woodpecker.misc.functions as functions


class BaseCorrelator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parsed_entries):
        self._correlated = None

        self._parsed_entries = parsed_entries

    @abc.abstractmethod
    def correlate(self):
        pass
