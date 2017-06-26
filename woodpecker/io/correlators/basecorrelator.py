import abc

from woodpecker.io.correlators.event import Event, EventCollection


class BaseCorrelator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, parsed_entries):
        self._correlated = None

        self._parsed_entries = parsed_entries

        # Events
        self.events = EventCollection()

    @abc.abstractmethod
    def correlate(self):
        pass

    def _add_think_time_event(self, think_time):
        event = Event('think_time')
        event.data.update({'think_time': think_time})
        self.events.add_event(event)

    def _add_sequence_break(self):
        self.events.add_event(Event('sequence_break'))
