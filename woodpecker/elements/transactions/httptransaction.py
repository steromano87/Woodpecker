import abc
import json
import requests
from woodpecker.elements.transactions.simpletransaction import SimpleTransaction

__author__ = 'Stefano'


class HttpTransaction(SimpleTransaction):
    __metaclass__ = abc.ABCMeta

    def __init__(self, str_testname, int_iteration, **kwargs):
        super(HttpTransaction, self).__init__(str_testname, int_iteration, **kwargs)
        self.session = kwargs.get('session', requests.Session())

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

        if str_method == 'GET':
            self.last_response =\
                self.session.get(str_url,
                                 params=obj_data,
                                 headers=obj_headers,
                                 cookies=obj_cookies,
                                 allow_redirects=bool_redirects,
                                 proxies=obj_proxy,
                                 verify=bool_verify_ssl)

        elif str_method == 'POST':
            if self.is_json(obj_data):
                self.last_response =\
                    self.session.post(str_url,
                                      json=obj_data,
                                      headers=obj_headers,
                                      cookies=obj_cookies,
                                      allow_redirects=bool_redirects,
                                      proxies=obj_proxy,
                                      verify=bool_verify_ssl)

            else:
                self.last_response =\
                    self.session.post(str_url,
                                      data=obj_data,
                                      headers=obj_headers,
                                      cookies=obj_cookies,
                                      allow_redirects=bool_redirects,
                                      proxies=obj_proxy,
                                      verify=bool_verify_ssl)

        elif str_method == 'PUT':
            self.last_response =\
                self.session.put(str_url,
                                 params=obj_data,
                                 headers=obj_headers,
                                 cookies=obj_cookies,
                                 allow_redirects=bool_redirects,
                                 verify=bool_verify_ssl)

        elif str_method == 'DELETE':
            self.last_response =\
                self.session.delete(str_url,
                                 params=obj_data,
                                 headers=obj_headers,
                                 cookies=obj_cookies,
                                 allow_redirects=bool_redirects,
                                 proxies=obj_proxy,
                                 verify=bool_verify_ssl)

        # This line is for debug purposes only
        print(str_request_name + ' - ' + str(self.last_response.status_code) + ' - ' + str(self.last_response.elapsed))

    @staticmethod
    def is_json(str_json):
        try:
            json.loads(str_json)
        except ValueError:
            return False
        return True
