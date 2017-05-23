import abc


class BaseGenerator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parsed_entries):
        self._parsed_entries = parsed_entries

    @abc.abstractmethod
    def generate(self):
        pass
