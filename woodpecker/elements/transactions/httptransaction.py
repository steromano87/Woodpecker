import abc
import json

import requests

import woodpecker.misc.utils as utils

from woodpecker.elements.transactions.simpletransaction import SimpleTransaction

__author__ = 'Stefano'


class HttpTransaction(SimpleTransaction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        super(HttpTransaction, self).__init__(**kwargs)

        # Check for existence of '_session' key in thread variables dictionary.
        # If it does not exist a new session is created
        if '_session' not in self.thread_variables:
            self.thread_variables['_session'] = requests.Session()

    def http_request(self, str_request_name, str_url, **kwargs):
        str_method = kwargs.get('method', 'GET')
        obj_data = kwargs.get('data', {})
        obj_headers = kwargs.get('headers', {})
        obj_cookies = kwargs.get('cookies', {})
        bool_redirects = kwargs.get('allow_redirects', True)
        bool_verify_ssl = kwargs.get('verify_ssl', False)

        # Sets the proxy settings
        if 'proxy' in self.settings:
            obj_proxy = self.settings['proxy']
        else:
            obj_proxy = {}

        # If the Verify SSL option is set to false, disables the urllib InsecureRequestWarning message
        if not bool_verify_ssl:
            requests.packages.urllib3.disable_warnings()

        # Build kwargs for request according to method
        dic_request_kwargs = {
            'headers': obj_headers,
            'cookies': obj_cookies,
            'allow_redirects': bool_redirects,
            'proxies': obj_proxy,
            'verify': bool_verify_ssl
        }

        if str_method == 'GET' or str_method == 'DELETE':
            dic_request_kwargs['params'] = obj_data
        elif str_method == 'POST' or str_method == 'PUT' or str_method == 'PATCH':
            if self.is_json(obj_data):
                dic_request_kwargs['json'] = obj_data
            else:
                dic_request_kwargs['data'] = obj_data

        # Send unique request with kwargs defined in dict
        str_timestamp = utils.get_timestamp()
        self.thread_variables['_last_response'] = \
            self.thread_variables['_session'].request(str_method, str_url, **dic_request_kwargs)

        # Send request data using sender object
        self.sender.send('request',
                         {
                             'hostName': utils.get_ip_address(),
                             'spawnID': self.spawn_id,
                             'testName': self.navigation_name,
                             'iteration': self.iteration,
                             'timestamp': str_timestamp,
                             'requestName': str_request_name,
                             'requestType': '_'.join(('HTTP', str_method)),
                             'requestSkeleton': None,
                             'requestSpecs': json.dumps(obj_data),
                             'duration': self.thread_variables['_last_response'].elapsed.total_seconds() * 1000,
                             'status': self.thread_variables['_last_response'].status_code,
                             'responseSize': self.thread_variables['_last_response'].headers.get('content-length',
                                                                                                 None),
                             'assertionResult': 1
                         })

    @staticmethod
    def is_json(str_json):
        try:
            json.loads(str_json)
        except ValueError:
            return False
        return True
