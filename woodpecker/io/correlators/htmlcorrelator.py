from __future__ import division

import six

from copy import deepcopy

from woodpecker.io.correlators.event import Event
from woodpecker.io.correlators.basecorrelator import BaseCorrelator
from woodpecker.io.resources.htmlresource import HtmlResource


class HtmlCorrelator(BaseCorrelator):

    resource_mime_types = (
        'text/css',
        'application/x-javascript',
        'application/javascript',
        'image/png',
        'image/jpeg',
        'image/gif',
        'image/tiff'
    )

    excluded_headers = (
        'Host',
        'Connection',
        'Content-Length',
        'X-Requested-With'
    )

    def __init__(self, parsed_entries):
        super(HtmlCorrelator, self).__init__(parsed_entries)

        # User agent
        self.user_agent = None

        # List of referers
        self.referers = set()

        # List of redirect locations
        self.redirects = set()

        # List of "white-noise" headers
        self.wn_headers = dict()

    def correlate(self):
        self.get_user_agent()
        self.get_referers()
        self.get_redirects()
        self.get_wn_headers()
        self.calculate_events()
        return self.events

    def get_user_agent(self):
        self.user_agent = \
            self._parsed_entries.get('entries', [])[0].request.user_agent

        self._add_set_user_agent_event(self.user_agent)

    def get_wn_headers(self):
        # Retrieve white noise headers
        for index, entry in enumerate(self._parsed_entries.get('entries', [])):
            if index == 0:
                self.wn_headers = entry.request.headers
            else:
                orig_wn_headers = deepcopy(self.wn_headers)
                for wnh_name, wnh_value in six.iteritems(orig_wn_headers):
                    if entry.request.headers.get(wnh_name, '') != wnh_value:
                        del self.wn_headers[wnh_name]

        # Add white noise headers to event collection
        self._add_set_headers_event(self.wn_headers)

    def get_referers(self):
        # Start reading the loaded entries and getting the Referers
        for entry in self._parsed_entries.get('entries', []):
            # If the call has a referer, add the referer to list
            for header_name, header_value \
                    in six.viewitems(entry.request.headers):
                if header_name.lower() in ('referer', 'referrer'):
                    self.referers.add(header_value)

    def get_redirects(self):
        for entry in self._parsed_entries.get('entries', []):
            # If the response has a Location and the status is a 3XX,
            # add the location to redirects
            for header_name, header_value \
                    in six.viewitems(entry.response.headers):
                if header_name.lower() == 'location' \
                        and entry.response.status in six.moves.range(300, 400):
                    self.redirects.add(header_value.split('?')[0])

    def calculate_events(self,
                         think_time_threshold=3.0,
                         new_sequence_threshold=7.0):
        previous_entry = HtmlResource()

        # Cycle through the calls and set the proper events
        for entry in self._parsed_entries.get('entries', []):
            # Check if a think time should be inserted
            if entry.timings.elapsed['from_end_of_previous'] / 1000 > \
                    new_sequence_threshold:
                self._add_sequence_break()
            elif entry.timings.elapsed['from_end_of_previous'] / 1000 > \
                    think_time_threshold:
                self._add_think_time_event(
                    round(entry.timings.elapsed['from_end_of_previous']))

            if entry.url in self.redirects:
                self._add_http_redirect_event(entry, previous_entry)
            elif entry.request.headers.get(
                    'X-Requested-With', None) == 'XMLHttpRequest':
                self._add_http_async_request_event(entry)
            elif entry.request.headers.get('Referer', '') in self.referers:
                self._add_http_load_resource_event(entry)
            elif 'text/html' in entry.mime_type():
                event = self._create_http_request_event(entry,
                                                        'http_load_page')
                self.events.add_event(event)
            else:
                event = self._create_http_request_event(entry, 'http_request')
                self.events.add_event(event)

            previous_entry = deepcopy(entry)

    def _create_http_request_event(self, entry, type_name):
        event = Event(type_name, event_id=entry.url)

        # Clean headers from white noise headers
        cleaned_headers = deepcopy(entry.request.headers)
        for key, item in six.iteritems(self.wn_headers):
            if cleaned_headers.get(key, '') == item:
                del cleaned_headers[key]

        # Clean headers from excluded ones
        for key in cleaned_headers.keys():
            if key in HtmlCorrelator.excluded_headers:
                del cleaned_headers[key]

        event.data.update({
            'url': entry.url,
            'query_params': entry.request.params,
            'form_data': entry.request.form_data,
            'headers': cleaned_headers,
            'method': entry.method
        })
        return event

    def _add_set_user_agent_event(self, user_agent):
        event = Event('http_set_user_agent')
        event.data.update({
            'user_agent': user_agent
        })
        self.events.add_event(event)

    def _add_set_headers_event(self, headers):
        event = Event('http_set_headers')
        event.data.update(headers)
        self.events.add_event(event)

    def _add_set_cookie_event(self, cookie):
        event = Event('http_set_cookies')
        event.data.update(cookie)
        self.events.add_event(event)

    def _add_http_redirect_event(self, entry, previous_entry=HtmlResource()):
        event = self._create_http_request_event(entry, 'http_redirect')
        if entry.url in \
                previous_entry.response.headers.get('Location', ''):
            # Try to add the redirect to the direct first level event
            try:
                self.events.append_event(
                    previous_entry.url,
                    event
                )
            except KeyError:
                # If not found, try to append the redirect
                # to the second level events
                try:
                    self.events.events[
                        self.events.last_event()
                    ].appended_events.append_event(
                        previous_entry.url,
                        event
                    )
                except KeyError:
                    # If no event is found, append to last element
                    self.events.append_event(
                        self.events.last_event(),
                        event
                    )
        else:
            self.events.append_event(
                self.events.last_event(),
                event
            )

    def _add_http_async_request_event(self, entry):
        event = self._create_http_request_event(entry,
                                                'http_async_request')
        try:
            self.events.append_event(
                entry.request.headers.get('Origin', None),
                event
            )
        except KeyError:
            self.events.append_event(
                self.events.last_event(),
                event
            )

    def _add_http_load_resource_event(self, entry):
        if entry.mime_type() in HtmlCorrelator.resource_mime_types:
            event = self._create_http_request_event(
                entry, 'http_load_resource')
        else:
            event = self._create_http_request_event(
                entry, 'http_request')
        try:
            self.events.append_event(
                entry.request.headers.get('Referer', None),
                event
            )
        except KeyError:
            self.events.append_event(
                self.events.last_event(),
                event
            )
