import uuid

from collections import OrderedDict


class Event(object):
    def __init__(self, event_type):
        # Event type
        self.type = event_type

        # Event unique ID
        self.id = uuid.uuid4()

        # Event data
        self.data = dict()

        # Related events
        self.prepended_events = EventCollection()
        self.appended_events = EventCollection()

    def prepend_event(self, event):
        self.prepended_events.add_event(event)

    def append_event(self, event):
        self.appended_events.add_event(event)

    def has_prepended_events(self):
        return self.prepended_events.event_count() > 0

    def has_appended_events(self):
        return self.appended_events.event_count() > 0


class EventCollection(object):
    def __init__(self):
        # Inner events list
        self.events = OrderedDict()

        # Recursive counter
        self._event_counter = 0

    def _increase_counter(self):
        self._event_counter += 1

    def add_event(self, event):
        # Raise exception if teh entry is not an event
        if not isinstance(event, Event):
            raise TypeError('Only events can be added to an Event Collection')

        self.events[event.id] = event
        self._increase_counter()

    def prepend_event(self, main_event_id, prepended_event):
        # Raise exception if teh entry is not an event
        if not isinstance(prepended_event, Event):
            raise TypeError('Only events can be added to an Event Collection')

        try:
            self.events[main_event_id].prepend_event(prepended_event)
        except KeyError:
            raise KeyError('Event {id} not found'.format(id=main_event_id))

    def append_event(self, main_event_id, appended_event):
        # Raise exception if teh entry is not an event
        if not isinstance(appended_event, Event):
            raise TypeError('Only events can be added to an Event Collection')

        try:
            self.events[main_event_id].append_event(appended_event)
        except KeyError:
            raise KeyError('Event {id} not found'.format(id=main_event_id))

    def event_count(self):
        return self._event_counter
