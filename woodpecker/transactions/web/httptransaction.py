import abc
import json

import requests

import woodpecker.misc.utils as utils

from woodpecker.transactions.generic.basetransaction import BaseTransaction


class HttpTransaction(BaseTransaction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, **kwargs):
        super(HttpTransaction, self).__init__(**kwargs)

        # Check if a session is present, otherwise create a new one
        if not self.exist_variable('_session'):
            self.set_variable('_session', requests.Session())

    def http_request(self, str_request_name, str_url, **kwargs):
        # Request method
        str_method = kwargs.get('method', self.get_option('default_request_method', 'GET'))

        # Request data
        obj_data = kwargs.get('data', {})

        # Request headers
        obj_headers = kwargs.get('headers', self.get_option('default_request_headers', {}))

        # Request cookies
        obj_cookies = kwargs.get('cookies', self.get_option('default_request_cookies', {}))

        # Option to follow redirects or not
        bool_redirects = kwargs.get('allow_redirects', self.get_option('allow_redirects', True))

        # Option to verify SSL certificates
        bool_ignore_ssl_errors = kwargs.get('ignore_ssl_errors', self.get_option('ignore_ssl_errors', True))

        # Proxy settings
        obj_proxy = kwargs.get('proxy', self.get_option('proxy', {}))

        # Assertions for the current step
        dic_assertions = kwargs.get('assertions', {})

        # If the Ignore SSL errors option is set to true, disables the urllib InsecureRequestWarning message
        if bool_ignore_ssl_errors:
            requests.packages.urllib3.disable_warnings()

        # Build kwargs for request according to method
        dic_request_kwargs = {
            'headers': obj_headers,
            'cookies': obj_cookies,
            'allow_redirects': bool_redirects,
            'proxies': obj_proxy,
            'verify': not bool_ignore_ssl_errors
        }

        if str_method in ('GET', 'DELETE'):
            dic_request_kwargs['params'] = obj_data
        elif str_method in ('POST', 'PUT', 'PATCH'):
            if self.is_json(obj_data):
                dic_request_kwargs['json'] = obj_data
            else:
                dic_request_kwargs['data'] = obj_data

        # Send unique request with kwargs defined in dict
        str_timestamp = utils.get_timestamp()
        self.set_variable('_last_response',
                          self.get_variable('_session').request(str_method, str_url, **dic_request_kwargs))

        # Send request data using sender object
        self.add_to_log('steps',
                        {
                            'hostName': utils.get_ip_address(),
                            'peckerID': self.pecker_id,
                            'navigationName': self.navigation_name,
                            'transactionName': self.transaction_name,
                            'iteration': self.iteration,
                            'timestamp': str_timestamp,
                            'stepName': str_request_name,
                            'stepType': '_'.join(('HTTP', str_method)),
                            'stepSkeleton': str_url,
                            'stepData': json.dumps(obj_data),
                            'elapsed': self.get_variable('_last_response').elapsed.total_seconds() * 1000,
                            'status': self.get_variable('_last_response').status_code,
                            'responseSize': len(self.get_variable('_last_response').content),
                            'assertionsResult': self.check_assertions(dic_assertions)
                        })

    @staticmethod
    def is_json(str_json):
        try:
            json.loads(str_json)
        except ValueError:
            return False
        return True

    def check_assertions(self, dic_assertions):
        # TODO: add assertions support
        obj_response = self.get_variable('_last_response')
        return None
