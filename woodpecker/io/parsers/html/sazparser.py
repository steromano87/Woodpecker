import itertools
import re
import urllib
import xml.etree.cElementTree as eTree
import zipfile

import dateutil.parser as dateparser

import woodpecker.misc.functions as functions
from woodpecker.io.parsers.baseparser import BaseParser
from woodpecker.io.resources.htmlresource import HtmlResource


class SazParser(BaseParser):

    def _import_file(self, filename):
        try:
            # Zip file  structure
            self._zip_file = zipfile.ZipFile(filename, 'r')
        except IOError:
            raise IOError('File "{file_path}" not found'.format(
                file_path=filename
            ))

    def __del__(self):
        # Ensure to close Zip file before exiting
        self._zip_file.close()

    def parse(self):
        # Try to open Zip file, else throw exception
        try:
            content_list = self._zip_file.namelist()
        except IOError:
            raise IOError('File {file} does not exist'.format(
                file=self._file_path)
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
            resource = HtmlResource()
            self._parse_request(index, resource)
            self._parse_response(index, resource)
            self._parse_timings(index, resource)
            self._parsed['entries'].append(resource)

        # Return everything
        return self._parsed

    def _parse_request(self, index, resource):
        """
        Parses a request into HtmlResource

        :param index:
        :param HtmlResource resource:
        :return: None
        """

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
                    saz_file=self._file_path
                )
            )

        # If file content can be read, parse it
        first_line = raw_file_content.split('\n', 1)[0].split(' ')

        # Start getting method and URL
        resource.method = first_line[0]
        resource.url = urllib.unquote_plus(first_line[1].split('?')[0])

        # Parse query string parameters
        if '?' in first_line[1]:
            resource.request.parse_query_string(first_line[1].split('?')[1])

        # Parse headers in key - value format
        header_lines = functions.split_by_element(
            raw_file_content.split('\n', 1)[1].splitlines(),
            ''
        )[0]

        # Iterate over elements and save separately user agent and cookies
        for header_line in header_lines:
            header_couple = header_line.split(':', 1)
            if header_couple[0].lower() == 'cookie':
                resource.request.parse_cookie_header(header_couple[1].strip())
            elif header_couple[0].lower() == 'user-agent':
                resource.request.user_agent = header_couple[1].strip()
            else:
                resource.request.headers[header_couple[0].strip()] = \
                    header_couple[1].strip()

        # Parse content lines
        try:
            content_lines = functions.split_by_element(
                raw_file_content.split('\n', 1)[1].splitlines(),
                ''
            )[1]
            # If the content type is www-form-urlencoded, parse the content
            # as POST key-value data
            if 'application/x-www-form-urlencoded' \
                    in resource.request.headers.get('Content-Type', ''):
                resource.request.parse_form_data(content_lines[0])
            else:
                resource.request.payload = \
                    functions.get_eol(raw_file_content).join(content_lines)
        except IndexError:
            resource.request.payload = None

    def _parse_response(self, index, resource):
        """
        Parses a response into HtmlResource

        :param index:
        :param HtmlResource resource:
        :return: None
        """

        # Try to read file content
        try:
            raw_file_content = \
                self._zip_file.read('raw/{index}_s.txt'.format(index=index))
        except IOError:
            # Raise exception if file cannot be found
            raise IOError(
                'Cannot find "raw/{index}_s.txt" inside '
                'file {saz_file}, corrupted archive?'.format(
                    index=index,
                    saz_file=self._file_path
                )
            )

        # If file content can be read, parse it
        first_line = raw_file_content.split('\n', 1)[0].split(' ')

        # Start getting method and URL
        resource.response.status = int(first_line[1])

        # Parse headers in key - value format
        header_lines = functions.split_by_element(
            raw_file_content.split('\n', 1)[1].splitlines(),
            ''
        )[0]

        # Iterate over elements and save separately user agent and cookies
        for header_line in header_lines:
            header_couple = header_line.split(': ', 1)
            if header_couple[0].lower() == 'set-cookie':
                resource.response.parse_set_cookie_header(
                    header_couple[1].strip()
                )
            elif header_couple[0].lower() == 'content-type':
                resource.response.mime_type = header_couple[1].strip()
            elif header_couple[0].lower() == 'content-length':
                resource.response.size = int(header_couple[1].strip())
            else:
                resource.response.headers[header_couple[0].strip()] = \
                    header_couple[1].strip()

        # Try to parse content lines
        try:
            content_lines = \
                list(itertools.chain.from_iterable(functions.split_by_element(
                    raw_file_content.split('\n', 1)[1].splitlines(),
                    ''
                )[1:]))
        except IndexError:
            resource.response.content = None
        else:
            line_sep = functions.get_eol(raw_file_content)
            resource.response.content = line_sep.join(content_lines)

    def _parse_timings(self, index, resource):
        """
        Parses the timings into HtmlResource

        :param index:
        :param HtmlResource resource:
        :return: None
        """

        # Try to read file content
        try:
            raw_file_content = \
                self._zip_file.read('raw/{index}_m.xml'.format(index=index))
        except IOError:
            # Raise exception if file cannot be found
            raise IOError(
                'Cannot find "raw/{index}_m.xml" inside '
                'file {saz_file}, corrupted archive?'.format(
                    index=index,
                    saz_file=self._file_path
                )
            )

        xml_doc = eTree.fromstring(raw_file_content)
        session_timers = xml_doc.findall('.//SessionTimers')[0]
        resource.timings.timestamp = dateparser.parse(
            session_timers.attrib['ClientBeginRequest']
        )

        # If index is 01, set the start time, too
        if index == '01':
            self._parsed['start_time'] = resource.timings.timestamp

        resource.timings.duration = round((dateparser.parse(
            session_timers.attrib['ClientDoneResponse']
        ) - resource.timings.timestamp).total_seconds() * 1000)
        resource.timings.elapsed['from_start'] = \
            round((resource.timings.timestamp -
                   self._parsed['start_time']).total_seconds() * 1000)

        try:
            resource.timings.elapsed['from_start_of_previous'] = \
                round((resource.timings.timestamp -
                       self._parsed['entries'][-1].timings.timestamp
                       ).total_seconds() * 1000)
        except (IndexError, KeyError):
            resource.timings.elapsed['from_start_of_previous'] = 0

        try:
            resource.timings.elapsed['from_end_of_previous'] = \
                resource.timings.elapsed['from_start_of_previous'] - \
                self._parsed['entries'][-1].timings.duration
        except (IndexError, KeyError):
            resource.timings.elapsed['from_end_of_previous'] = 0

            resource.timings.elapsed['from_end_of_previous'] = \
                resource.timings.elapsed['from_end_of_previous'] \
                if resource.timings.elapsed['from_end_of_previous'] > 0 else 0
