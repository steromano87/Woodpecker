import json
import sys
import os
import urllib

import dateutil.parser as dateparser

from woodpecker.parsers.baseparser import BaseParser


class HarParser(BaseParser):
    def __init__(self, har_file):
        try:
            with open(os.path.abspath(har_file), 'rb') as fp:
                self._raw_data = json.load(fp)
        except IOError:
            sys.stdout.write('File "{file_path}" not found'.format(
                file_path=har_file
            ))
        else:
            self._parsed = {
                'start_time': None,
                'entries': []
            }

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
                'response': None
            })

        # Return everything
        return self._parsed

    def _parse_request(self, entry):
        entry_request = entry.get('request', {})

        # Get base URL (reject the query string part)
        url = entry_request.get('url', '')
        if '?' in url:
            url = url.split('?')[0]
        request = dict(url=url)

        # Get request method
        request['method'] = entry_request.get('method', 'GET')

        # Get request duration
        request['duration'] = float(entry.get('time', 0))

        # Get request query string parameters
        request['params'] = {}
        if '?' in url:
            query_string = url.split('?')[1]
            for param_couple in query_string.split('&'):
                split_params = param_couple.split('=')
                request['params'][urllib.unquote_plus(split_params[0])] = \
                    urllib.unquote_plus(split_params[1])

        # Get request cookies
        request['cookies'] = entry_request.get('cookies', [])

        # Get request timestamp
        request['timestamp'] = entry.get('startedDateTime', None)

        # Get request elapsed since first request (in milliseconds)
        request['elapsed_from_start'] = (
            dateparser.parse(
                request['timestamp']
            ) - self._parsed['start_time']
        ).total_seconds() * 1000

        # Get request elapsed from previous request (if any)
        # Defaults to elapsed from start
        try:
            request['elapsed_from_previous'] = (
               dateparser.parse(
                   request['timestamp']
               ) -
               dateparser.parse(
                   self._parsed['entries'][-1]['request']['timestamp']
               )
            ).total_seconds() * 1000
        except (KeyError, IndexError):
            request['elapsed_from_previous'] = \
                request['elapsed_from_start']

        # If elapsed is negative, force it to zero
        request['elapsed_from_previous'] = request['elapsed_from_previous'] \
            if request['elapsed_from_previous'] > 0 else 0.0

        # Get request elapsed from end of previous request (if any)
        try:
            request['elapsed_from_end_of_previous'] = \
                request['elapsed_from_previous'] - \
                self._parsed['entries'][-1]['request']['duration']
        except (KeyError, IndexError):
            request['elapsed_from_end_of_previous'] = 0.0

        # If elapsed is negative, force it to zero
        request['elapsed_from_end_of_previous'] = \
            request['elapsed_from_end_of_previous'] \
            if request['elapsed_from_end_of_previous'] > 0 else 0.0

        return request
