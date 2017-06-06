import uuid

from collections import OrderedDict


class Event(object):
    def __init__(self, event_type):
        # Event type
        self.type = event_type

        # Event unique ID
        self.id = uuid.uuid4()

        # Related events
        self.related_events = EventCollection()

    def add_related_event(self, event):
        self.related_events.add_event(event)

    def has_related_events(self):
        return self.related_events.event_count() > 0


class EventCollection(object):
    def __init__(self):
        # Inner events list
        self._events = OrderedDict()

        # Recursive counter
        self._event_counter = 0

    def _increase_counter(self):
        self._event_counter += 1

    def add_event(self, event, related_event=None):
        # Raise exception if teh entry is not an event
        if not isinstance(event, Event):
            raise TypeError('Only events can be added to an Event Collection')

        # If no related event is provided, add the event as main event
        if related_event is None:
            self._events[event.id] = event
        else:
            try:
                self._events[related_event].add_related_event(event)
            except KeyError:
                raise KeyError('Event {id} not found'.format(id=related_event))
        self._increase_counter()

    def event_count(self):
        return self._event_counter
