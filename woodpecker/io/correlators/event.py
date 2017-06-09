import uuid
import six

from collections import OrderedDict


class Event(object):
    def __init__(self, event_type, event_id=None):
        # Event type
        self.type = event_type

        # Event unique ID
        self.id = event_id or uuid.uuid4()

        # Event data
        self.data = dict()

        # Related events
        self.prepended_events = EventCollection()
        self.appended_events = EventCollection()

    def __repr__(self):
        return '{classname} - {type} - {id}'.format(
            classname=self.__class__.__name__,
            type=self.type,
            id=self.id
        )

    def prepend_event(self, event):
        self.prepended_events.add_event(event)

    def append_event(self, event):
        self.appended_events.add_event(event)

    def has_prepended_events(self):
        return self.prepended_events.count() > 0

    def has_appended_events(self):
        return self.appended_events.count() > 0


class EventCollection(object):
    def __init__(self):
        # Inner events list
        self.events = OrderedDict()

        # Recursive counter
        self._event_counter = 0

    def _increase_counter(self):
        self._event_counter += 1

    @staticmethod
    def _check_event(event):
        # Raise exception if teh entry is not an event
        if not isinstance(event, Event):
            raise TypeError('Only events can be added to an Event Collection')

    def add_event(self, event):
        EventCollection._check_event(event)
        self.events[event.id] = event
        self._increase_counter()

    def prepend_event(self, main_event_id, prepended_event):
        EventCollection._check_event(prepended_event)
        try:
            self.events[main_event_id].prepend_event(prepended_event)
        except KeyError:
            raise KeyError('Event {id} not found'.format(id=main_event_id))

    def append_event(self, main_event_id, appended_event):
        EventCollection._check_event(appended_event)
        try:
            self.events[main_event_id].append_event(appended_event)
        except KeyError:
            raise KeyError('Event {id} not found'.format(id=main_event_id))

    def count(self):
        return self._event_counter

    def search_by_data(self, event_data):
        if isinstance(event_data, dict):
            found = False
            for event_key, event in six.iteritems(self.events):
                for search_key, search_value in six.iteritems(event_data):
                    if event.data.get(search_key, 'NOTFOUND') == search_value:
                        found = True
                    else:
                        found = False
                if found:
                    return event_key
        else:
            raise TypeError('Event data must be passed as a dict')
