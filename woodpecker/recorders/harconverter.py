from __future__ import division

import json
import os
import re
import dateutil.parser as parser

import woodpecker.misc.utils as utils

__author__ = 'Stefano'


class HarConverter(object):

    def __init__(self, **kwargs):
        self._initialize(**kwargs)

    def __enter__(self, **kwargs):
        self._initialize(**kwargs)

    def _initialize(self, **kwargs):
        # Thresholds
        self.transaction_threshold = kwargs.get('transaction_threshold', 5)
        self.think_time_threshold = kwargs.get('think_time_threshold', 1)

        # Various options
        self.round_think_times = kwargs.get('round_think_times', True)
        self.think_time_limit = kwargs.get('think_time_limit', -1)
        self.tab_size = kwargs.get('tab_size', 4)
        self.user_agent = None

        # Placeholder for transactions
        self.transactions = []

    def _load_har(self, str_filepath):
        # Open file and import raw data
        with open(str_filepath, 'r') as obj_fp:
            self.raw_data = obj_fp.read()

        # Skips binary header if present (present if HAR is exported from Fiddler)
        skip = 3 if '\xef\xbb\xbf' == self.raw_data[:3] else 0
        self.data = json.loads(self.raw_data[skip:])
        self.raw_data = None

    def _parse_har(self):
        # Cycle through all requests and parse them into a more concise structure
        arr_current_transaction = []
        date_last_request_time = None

        for dic_entry in self.data['log']['entries']:
            # Calculate elapsed time from last request
            date_current_request_time = parser.parse(dic_entry['startedDateTime'])
            dbl_elapsed = (date_current_request_time - date_last_request_time).total_seconds() \
                if date_last_request_time else 0

            # Parse headers
            dic_headers = {}
            for dic_header in dic_entry['request']['headers']:
                if dic_header['name'] != 'Cookie':
                    dic_headers[utils.unicode2ascii(dic_header['name'])] = utils.unicode2ascii(dic_header['value'])

            # If User Agent is not set, get the User Agent used during recording and use it
            if not self.user_agent:
                self.user_agent = dic_headers.get('User-Agent', None)

            # If User-Agent key is present, remove it
            if dic_headers['User-Agent']:
                dic_headers.pop('User-Agent')

            # If the request has a query string, extract only the base address and handle arguments separately
            dic_data = {}
            str_url = dic_entry['request']['url']
            if len(dic_entry['request']['queryString']) > 0:
                str_url = re.search("(http[s]?://.+?)\?", dic_entry['request']['url']).group(1)

                for dic_querystring_entry in dic_entry['request']['queryString']:
                    dic_data[utils.unicode2ascii(dic_querystring_entry['name'])] = \
                        utils.unicode2ascii(dic_querystring_entry['value'])

            # If method is POST, PUT or PATCH search for data in POST data and compile dic_data
            elif dic_entry['request']['method'] == 'POST' \
                    or dic_entry['request']['method'] == 'PUT' \
                    or dic_entry['request']['method'] == 'PATCH':

                arr_params = dic_entry['request']['postData'].get('params', [])
                for dic_post_entry in arr_params:
                    dic_data[utils.unicode2ascii(dic_post_entry['name'])] = \
                        utils.unicode2ascii(dic_post_entry['value'])

            dic_current_request = {
                'url': str_url,
                'method': dic_entry['request']['method'],
                'data': dic_data,
                'headers': dic_headers,
                'expectedStatus': dic_entry['response']['status'],
                'expectedMimeType': dic_entry['response']['content']['mimeType'],
                'timeStamp': parser.parse(dic_entry['startedDateTime']),
                'elapsedTime': dbl_elapsed
            }

            # Check if another transaction has to be created to store the current request
            if dbl_elapsed > self.transaction_threshold:
                self.transactions.append(arr_current_transaction)
                arr_current_transaction = []

            # Check if the think time has to be inserted
            if dbl_elapsed > self.think_time_threshold:

                # Calculate think time value
                if self.think_time_limit > 0:
                    dbl_think_time = dbl_elapsed \
                        if dbl_elapsed < self.think_time_limit \
                        else self.think_time_limit
                else:
                    dbl_think_time = dbl_elapsed
                arr_current_transaction.append({
                    'eventType': 'think_time',
                    'payload': {
                        'type': 'fixed',
                        'amount': round(dbl_think_time) if self.round_think_times else dbl_think_time
                    }
                })

            arr_current_transaction.append({
                'eventType': 'request',
                'payload': dic_current_request
            })

            # Update the last request time
            date_last_request_time = parser.parse(dic_entry['startedDateTime'])

        # Append the last transaction
        if len(arr_current_transaction) > 0:
            self.transactions.append(arr_current_transaction)

    def _write_transactions(self, str_transactions_folder=os.getcwd()):
        int_transaction_counter = 1
        for arr_transaction in self.transactions:
            str_filepath = os.path.join(str_transactions_folder,
                                        ''.join(('transaction_', str(int_transaction_counter), '.py')))

            # Open file and start composing the transaction
            with open(str_filepath, 'w') as obj_fp:
                obj_fp.write('from woodpecker.elements.transactions.httptransaction import HttpTransaction\n\n')
                obj_fp.write('""" This file has been automatically generated by Woodpecker HAR Converter """\n\n\n')
                obj_fp.write(''.join((
                    'class AutoHttpTransaction',
                    str(int_transaction_counter),
                    '(HttpTransaction):\n'
                )))

                # If is the first transaction, define User Agent in thread variables
                if int_transaction_counter == 1:
                    obj_fp.write('\tdef configure(self):\n'.replace('\t', ' ' * self.tab_size))
                    obj_fp.write(''.join((
                        '\t\tself.set_variable(\'_user_agent\', '
                        '\'', self.user_agent,
                        '\')\n\n'
                    )).replace('\t', ' ' * self.tab_size))

                obj_fp.write('\tdef steps(self):\n'.replace('\t', ' ' * self.tab_size))

                # Cycle on entries in transaction
                for dic_entry in arr_transaction:
                    if dic_entry['eventType'] == 'request':
                        str_transaction = self.__generate_request(dic_entry['payload'])
                        obj_fp.write(str_transaction)

                    elif dic_entry['eventType'] == 'think_time':
                        str_think_time = self._generate_think_time(dic_entry['payload'])
                        obj_fp.write(str_think_time)

            # Update transaction counter
            int_transaction_counter += 1

    def __generate_request(self, dic_payload):
        # Define indentation width in spaces for arguments and header entries
        int_arguments_indent = len('self.http_request(') + 2 * self.tab_size
        int_headers_indent = len('self.http_request(headers={') + 2 * self.tab_size
        int_data_indent = len('self.http_request(data={') + 2 * self.tab_size

        # Replace URL with partial address as name
        str_host = dic_payload['headers'].get('Host', '')
        str_pattern = re.compile(''.join(('http[s]?://', str_host)))

        # Pretty print headers and data as dict
        str_parsed_headers = \
            repr(dic_payload['headers']).replace('\', \'', ''.join(('\',\n', ' ' * int_headers_indent, '\'')))
        str_parsed_data = \
            repr(dic_payload['data']).replace('\', \'', ''.join(('\',\n', ' ' * int_data_indent, '\'')))

        # Add User-Agent hardcoded line
        str_parsed_headers = str_parsed_headers.replace('}', ''.join((',\n',
                                                                      ' ' * int_headers_indent,
                                                                      '\'User-Agent\': ',
                                                                      'self.get_variable(\'_user_agent\')}'
                                                                      ))
                                                        )

        # Compose the call
        str_request = ''.join((
            'self.http_request(\'',
            re.sub(str_pattern, '', dic_payload['url']),
            '\',\n',
            '\t\'', dic_payload['url'], '\',\n',
            '\tmethod=\'', dic_payload['method'], '\',\n',
            '\theaders=', str_parsed_headers, ',\n',
            '\tdata=', str_parsed_data, ',\n',
            '\t)\n\n'
        ))

        # Add indentations
        return re.sub("^",
                      ' ' * 2 * self.tab_size,
                      str_request.replace('\t', ' ' * int_arguments_indent))

    def _generate_think_time(self, dic_payload):
        # One-line think time generator
        str_think_time = ''.join(('\t\tself.think_time(', str(dic_payload['amount']),
                                  ', type=\'', dic_payload['type'], '\')\n\n'))
        return str_think_time.replace('\t', ' ' * self.tab_size)

    def convert(self, str_filepath, str_destination_folder=os.getcwd()):
        self._load_har(str_filepath)
        self._parse_har()
        self._write_transactions(str_destination_folder)