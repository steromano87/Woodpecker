import os
import re
import zipfile
import urllib

import woodpecker.misc.functions as functions

from woodpecker.parsers.baseparser import BaseParser


class SazParser(BaseParser):
    def __init__(self, saz_file):
        # Absolute path of Saz file
        self._saz_file_path = os.path.abspath(saz_file)

        # Zip file  structure
        self._zip_file = zipfile.ZipFile(self._saz_file_path, 'r')

        # Parsed data from SAZ file
        self._parsed = {
            'start_time': None,
            'entries': []
        }

    def __del__(self):
        # Ensure to close Zip file before exiting
        self._zip_file.close()

    def parse(self):
        # Try to open Zip file, else throw exception
        try:
            content_list = self._zip_file.namelist()
        except IOError:
            raise IOError('File {file} does not exist'.format(
                file=self._saz_file_path)
            )

        # Sort list in alphabetical order
        content_list.sort()

        # Remove all the useless items from content list
        for list_item in ('_index.htm', '[Content_Types].xml', 'raw/'):
            content_list.remove(list_item)

        # Retrieve all the entries indexes
        index_list = sorted(set([re.findall("\d+", zip_file)[0]
                            for zip_file in content_list]))

        # Cycle through index list and parse each file
        for index in index_list:
            self._parsed['entries'].append(
                {
                    'request': self._parse_request(index),
                    'response': None,
                    'timings': None
                }
            )

    def _parse_request(self, index):
        # Try to read file content
        try:
            raw_file_content = \
                self._zip_file.read('raw/{index}_c.txt'.format(index=index))
        except IOError:
            # Raise exception if file cannot be found
            raise IOError(
                'Cannot find "raw/{index}_c.txt" inside '
                'file {saz_file}, corrupted archive?'.format(
                    index=index,
                    saz_file=self._saz_file_path
                )
            )

        # If file content can be read, parse it
        first_line = raw_file_content.split('\n', 1)[0].split(' ')

        # Start getting method and URL
        request = dict(method=first_line[0])
        request['url'] = first_line[1].split('?')[0]

        # Parse query string parameters
        request['params'] = {}
        if '?' in first_line[1]:
            query_string = first_line[1].split('?')[1]
            for param_couple in query_string.split('&'):
                split_params = param_couple.split('=')
                request['params'][urllib.unquote_plus(split_params[0])] = \
                    urllib.unquote_plus(split_params[1])

        # Parse headers in key - value format
        header_lines = functions.split_by_element(
            raw_file_content.split('\n', 1)[1].splitlines(),
            ''
        )[0]

        # Iterate over elements and save separately user agent and cookies
        request['headers'] = {}
        for header_line in header_lines:
            header_couple = header_line.split(':')
            if header_couple[0].lower() == 'cookie':
                request['cookies'] = \
                    self._parse_cookies(header_couple[1].strip())
            elif header_couple[0].lower() == 'user-agent':
                request['user_agent'] = header_couple[1].strip()
            else:
                request['headers'][header_couple[0].strip()] = \
                    header_couple[1].strip()

        return request

    @staticmethod
    def _parse_cookies(cookie_string):
        cookies = cookie_string.split(';')
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[
                urllib.unquote_plus(cookie.split('=')[0].strip())
            ] = \
                urllib.unquote_plus(cookie.split('=')[1].strip())
        return cookie_dict
