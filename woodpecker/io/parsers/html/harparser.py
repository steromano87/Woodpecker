import urllib

import dateutil.parser as dateparser
import simplejson as json

from woodpecker.io.parsers.baseparser import BaseParser


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
            self._parsed['entries'].append({
                'request': self._parse_request(entry),
                'response': self._parse_response(entry),
                'timings': self._parse_timings(entry)
            })

        # Return everything
        return self._parsed

    @staticmethod
    def _parse_request(entry):
        entry_request = entry.get('request', {})

        # Get base URL (reject the query string part)
        url = entry_request.get('url', '')
        if '?' in url:
            url = url.split('?')[0]
        request = dict(url=url)

        # Get request method
        request['method'] = entry_request.get('method', 'GET')

        # Get request query string parameters
        request['params'] = {}
        if '?' in url:
            query_string = url.split('?')[1]
            for param_couple in query_string.split('&'):
                split_params = param_couple.split('=')
                request['params'][urllib.unquote_plus(split_params[0])] = \
                    urllib.unquote_plus(split_params[1])

        # Get request post data
        request['form_data'] = {}
        post_data_fields = entry_request.get('postData', {}).get('params', [])
        for post_data_entry in post_data_fields:
            request['form_data'][urllib.unquote_plus(
                post_data_entry['name'])] = \
                urllib.unquote_plus(post_data_entry['value'])

        # Get request cookies
        request['cookies'] = {}
        cookie_list = entry_request.get('cookies', [])
        for cookie_element in cookie_list:
            request['cookies'][urllib.unquote_plus(cookie_element['name'])] = \
                urllib.unquote_plus(cookie_element['value'])

        # Get request headers in key - value format
        request['headers'] = {}
        for header in entry_request.get('headers', []):
            try:
                header_key = header.get('name', '')
                # If key is 'cookie' or 'Cookie', skip it
                # because cookies are handled in previous section
                # If key is method, skip it for the same reason
                if str(header_key.lower()) == 'cookie' or \
                        str(header_key.lower()) == 'method':
                    pass
                elif str(header_key.lower()) == 'user-agent':
                    request['user_agent'] = header.get('value', '')
                else:
                    request['headers'][header.get('name', '')] = \
                        header.get('value', '')
            except KeyError:
                pass

        return request

    def _parse_timings(self, entry):
        # Get request timestamp
        timings = {
            'timestamp': dateparser.parse(entry.get('startedDateTime', None)),
            'duration': float(entry.get('time', 0))
        }

        # Get request elapsed since first request (in milliseconds)
        timings['elapsed_from_start'] = \
            (timings['timestamp'] -
             self._parsed['start_time']).total_seconds() * 1000

        # Get request elapsed from previous request (if any)
        # Defaults to elapsed from start
        try:
            timings['elapsed_from_previous'] = \
                (timings['timestamp'] -
                    self._parsed['entries'][-1]['timings']['timestamp']
                 ).total_seconds() * 1000
        except (KeyError, IndexError):
            timings['elapsed_from_previous'] = \
                timings['elapsed_from_start']

        # If elapsed is negative, force it to zero
        timings['elapsed_from_previous'] = \
            timings['elapsed_from_previous'] \
            if timings['elapsed_from_previous'] > 0.0 else 0.0

        # Get request elapsed from end of previous request (if any)
        try:
            timings['elapsed_from_end_of_previous'] = \
                timings['elapsed_from_previous'] - \
                self._parsed['entries'][-1]['timings']['duration']
        except (KeyError, IndexError):
            timings['elapsed_from_end_of_previous'] = 0.0

        # If elapsed is negative, force it to zero
        timings['elapsed_from_end_of_previous'] = \
            timings['elapsed_from_end_of_previous'] \
            if timings['elapsed_from_end_of_previous'] > 0.0 else 0.0

        return timings

    @staticmethod
    def _parse_response(entry):
        entry_response = entry.get('response', {})

        # Start composing response dict starting from HTTP status
        response = dict(status=entry_response.get('status', None))

        # Get request cookies
        response['cookies'] = entry_response.get('cookies', [])

        # Get content (type, size, value)
        response['content'] = {
            'size': entry_response.get('content', {}).get('size', 0),
            'mime_type': entry_response.get('content', {}).get('mimeType'),
            'text': entry_response.get('content', {}).get('text', ''),
        }

        # Get request headers in key - value format
        response['headers'] = {}
        for header in entry_response.get('headers', []):
            try:
                header_key = header.get('name', '')
                # If key is 'cookie' or 'Cookie', skip it
                # because cookies are handled in previous section
                # If key is method, skip it for the same reason
                if str(header_key.lower()) not in (
                        'set-cookie', 'method',
                        'content-type', 'content-length'):
                    response['headers'][header.get('name', '')] = \
                        header.get('value', '')
            except KeyError:
                pass

        return response
