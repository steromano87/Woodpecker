import urllib

import dateutil.parser as dateparser
import simplejson as json

from woodpecker.io.parsers.baseparser import BaseParser
from woodpecker.io.resources.htmlresource import HtmlResource


class HarParser(BaseParser):

    def _import_file(self, filename):
        try:
            with open(filename, 'rb') as fp:
                self._raw_data = json.load(fp)
        except IOError:
            raise IOError('File "{file_path}" not found'.format(
                file_path=filename
            ))

    def parse(self):
        entries = self._raw_data.get('log', {}).get('entries', [])

        # Get first entry and retrieve start time
        self._parsed['start_time'] = dateparser.parse(
            entries[0].get('startedDateTime', None)
        )

        for entry in entries:
            # Append the current request to parsed internal variable
            resource = HtmlResource()
            self._parse_request(entry, resource)
            self._parse_response(entry, resource)
            self._parse_timings(entry, resource)
            self._parsed['entries'].append(resource)

        # Return everything
        return self._parsed

    @staticmethod
    def _parse_request(entry, resource):
        """
        Parses a request into HtmlResource

        :param entry:
        :param HtmlResource resource:
        :return: None
        """
        entry_request = entry.get('request', {})

        # Get base URL (reject the query string part)
        url = entry_request.get('url', '')
        if '?' in url:
            url = url.split('?')[0]
        resource.url = url

        # Get request method
        resource.method = entry_request.get('method', 'GET')

        # Get request query string parameters
        if '?' in url:
            query_string = url.split('?')[1]
            resource.request.parse_query_string(query_string)

        # Get request post data
        post_data_fields = entry_request.get('postData', {}).get('params', [])
        for post_data_entry in post_data_fields:
            resource.request.form_data[urllib.unquote_plus(
                post_data_entry['name'])] = \
                urllib.unquote_plus(post_data_entry['value'])

        # Get request cookies
        resource.request.cookies = entry_request.get('cookies', [])

        # Get request headers in key - value format
        for header in entry_request.get('headers', []):
            try:
                header_key = header.get('name', '')
                # If key is 'cookie' or 'Cookie', skip it
                # because cookies are handled in previous section
                # If key is method, skip it for the same reason
                if str(header_key.lower()) == 'user-agent':
                    resource.request.user_agent = header.get('value', '')
                elif str(header_key.lower()) == 'accept':
                    resource.request.mime_type = \
                        header.get('value', '').split(',')
                elif str(header_key.lower()) not in ('cookie', 'method'):
                    resource.request.headers[header.get('name', '')] = \
                        header.get('value', '')
            except KeyError:
                pass

    def _parse_timings(self, entry, resource):
        """
        Parses the timings into HtmlResource

        :param entry:
        :param HtmlResource resource:
        :return: None
        """

        # Get request timestamp
        resource.timings.duration = float(entry.get('time', 0))
        resource.timings.timestamp = \
            dateparser.parse(entry.get('startedDateTime', None))

        # Get request elapsed since first request (in milliseconds)
        resource.timings.elapsed['from_start'] = \
            (resource.timings.timestamp -
             self._parsed['start_time']).total_seconds() * 1000

        # Get request elapsed from previous request (if any)
        # Defaults to elapsed from start
        try:
            resource.timings.elapsed['from_start_of_previous'] = \
                (resource.timings.timestamp -
                    self._parsed['entries'][-1].timings.timestamp
                 ).total_seconds() * 1000
        except (KeyError, IndexError):
            resource.timings.elapsed['from_start_of_previous'] = \
                resource.timings.elapsed['from_start']

        # If elapsed is negative, force it to zero
        resource.timings.elapsed['from_start_of_previous'] = \
            resource.timings.elapsed['from_start_of_previous'] \
            if resource.timings.elapsed['from_start_of_previous'] > 0.0 \
            else 0.0

        # Get request elapsed from end of previous request (if any)
        try:
            resource.timings.elapsed['from_end_of_previous'] = \
                resource.timings.elapsed['from_start_of_previous'] - \
                self._parsed['entries'][-1].timings.duration
        except (KeyError, IndexError):
            resource.timings.elapsed['from_end_of_previous'] = 0.0

        # If elapsed is negative, force it to zero
        resource.timings.elapsed['from_end_of_previous'] = \
            resource.timings.elapsed['from_end_of_previous'] \
            if resource.timings.elapsed['from_end_of_previous'] > 0.0 else 0.0

    @staticmethod
    def _parse_response(entry, resource):
        """
        Parses a response into HtmlResource

        :param entry:
        :param HtmlResource resource:
        :return: None
        """
        entry_response = entry.get('response', {})

        # Start composing response dict starting from HTTP status
        resource.response.status = entry_response.get('status', None)

        # Get request cookies
        resource.response.cookies = entry_response.get('cookies', [])

        # Get content (type, size, value)
        resource.response.content = entry_response.get(
            'content', {}).get('text', '')
        resource.response.mime_type = entry_response.get(
            'content', {}).get('mimeType')
        resource.response.size = entry_response.get(
            'content', {}).get('size', 0)

        # Get request headers in key - value format
        for header in entry_response.get('headers', []):
            try:
                header_key = header.get('name', '')
                # If key is 'cookie' or 'Cookie', skip it
                # because cookies are handled in previous section
                # If key is method, skip it for the same reason
                if str(header_key.lower()) not in (
                        'set-cookie', 'method',
                        'content-type', 'content-length'):
                    resource.response.headers[header.get('name', '')] = \
                        header.get('value', '')
            except KeyError:
                pass
