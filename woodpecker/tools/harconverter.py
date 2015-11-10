from __future__ import division

import json
import dateutil.parser as parser

__author__ = 'Stefano'


class HarConverter(object):

    def __init__(self, **kwargs):
        self.__initialize(**kwargs)

    def __enter__(self, **kwargs):
        self.__initialize(**kwargs)

    def __initialize(self, **kwargs):
        # Thresholds
        self.transaction_threshold = kwargs.get('transaction_threshold', 5)
        self.think_time_threshold = kwargs.get('think_time_threshold', 1)

        # Placeholder for transactions
        self.transactions = []

    def __load_har(self, str_filepath):
        # Open file and import raw data
        with open(str_filepath, 'r') as obj_fp:
            self.raw_data = obj_fp.read()

        # Skips binary header if present (present if HAR is exported from Fiddler)
        skip = 3 if '\xef\xbb\xbf' == self.raw_data[:3] else 0
        self.data = json.loads(self.raw_data[skip:])
        self.raw_data = None

    def __parse_har(self):
        # Cycle through all requests and parse them into a more concise structure
        arr_current_transaction = []
        int_transaction_elapsed = 0
        int_think_time_elapsed = 0
        date_last_request_time = None

        for dic_entry in self.data['log']['entries']:
            # Calculate elapsed time from last request
            date_current_request_time = parser.parse(dic_entry['startedDateTime'])
            dbl_elapsed = (date_current_request_time - date_last_request_time).total_seconds() \
                if date_last_request_time else 0

            dic_current_request = {
                'url': dic_entry['request']['url'],
                'method': dic_entry['request']['method'],
                'queryString': dic_entry['request']['queryString'],
                'postData': dic_entry['request']['postData'],
                'headers': dic_entry['request']['headers'],
                'expectedStatus': dic_entry['response']['status'],
                'expectedMimeType': dic_entry['response']['content']['mimeType'],
                'timeStamp': parser.parse(dic_entry['startedDateTime']),
                'elapsedTime': dbl_elapsed
            }

            # Check if another transaction has to be created to store the current request
            if dbl_elapsed > self.transaction_threshold:
                self.transactions.append(arr_current_transaction)
                arr_current_transaction = []
            arr_current_transaction.append(dic_current_request)

            # Update the last request time
            date_last_request_time = parser.parse(dic_entry['startedDateTime'])

        # Append the last transaction
        if len(arr_current_transaction) > 0:
            self.transactions.append(arr_current_transaction)

    def convert(self, str_filepath):
        self.__load_har(str_filepath)
        self.__parse_har()

if __name__ == '__main__':
    obj_har_converter = HarConverter()
    obj_har_converter.convert('D:/Data/Varie/Programmi Python/Woodpecker/tests/test.har')

