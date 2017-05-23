import abc


class BaseParser(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def parse(self):
        pass
