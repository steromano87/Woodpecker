import abc
import six

import requests

from woodpecker.data.settings import Settings
from woodpecker.data.variablejar import VariableJar
from woodpecker.sequences.basesequence import BaseSequence


class HttpSequence(BaseSequence):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=HttpSettings(),
                 log_queue=six.moves.queue(),
                 variables=VariableJar(),
                 parameters=None):
        super(HttpSequence, self).__init__(settings=settings,
                                           log_queue=log_queue,
                                           variables=variables,
                                           parameters=parameters)
        if not self.variables.is_set('__http_session'):
            self.variables.set('__http_session', requests.Session())
        if not self.variables.is_set('__last_response'):
            self.variables.set('__last_response', None)

    @staticmethod
    def default_settings():
        return HttpSettings()

    def http_request(self,
                     name,
                     url,
                     method='GET',
                     **kwargs):
        """
        Generic HTTP request

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param method: a standard HTTP request method
        :param kwargs: arguments to be passed to requests library
        """

        # Request headers
        kwargs['headers'] = kwargs.get(
            'headers', self.settings.get('http', 'default_request_headers'))

        # Option to follow redirects or not
        kwargs['allow_redirects'] = kwargs.get(
            'allow_redirects', self.settings.get('http', 'allow_redirects'))

        # Option to verify SSL certificates
        kwargs['verify'] = kwargs.get(
            'verify', not self.settings.get('http', 'ignore_ssl_errors'))

        # Proxy settings
        kwargs['proxies'] = kwargs.get(
            'proxies', self.settings.get('http', 'proxies'))

        # Default timeout
        kwargs['timeout'] = kwargs.get(
            'timeout', self.settings.get('http', 'default_timeout'))

        # If the Ignore SSL errors option is set to true,
        # disables the urllib InsecureRequestWarning message
        if not kwargs['verify']:
            requests.packages.urllib3.disable_warnings()

        # Execute the request
        obj_session = self.variables.get('__http_session')
        try:
            obj_last_response = obj_session.request(method, url, **kwargs)
            self.variables.set('__last_response', obj_last_response)
        except requests.exceptions.SSLError:
            obj_last_response = None
        self.variables.set('__http_session', obj_session)

        # Log the result of the request
        self.log('step', {
            'step_type': 'http_request',
            'active_transactions': self._transactions.keys(),
            'step_content': {
                'name': name,
                'url': url,
                'method': method,
                'params': kwargs.get('params', None),
                'data': kwargs.get('data', None) or kwargs.get('json', None),
                'headers': kwargs['headers'],
                'response_status': obj_last_response.status_code,
                'response_size': obj_last_response.content
            }
        })

    def get(self,
            name,
            url,
            **kwargs):
        """
        Shorthand for GET requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(name, url, method='GET', **kwargs)

    def post(self,
             name,
             url,
             **kwargs):
        """
        Shorthand for POST requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(name, url, method='POST', **kwargs)

    def put(self,
            name,
            url,
            **kwargs):
        """
        Shorthand for PUT requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(name, url, method='PUT', **kwargs)

    def patch(self,
              name,
              url,
              **kwargs):
        """
        Shorthand for PATCH requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(name, url, method='PATCH', **kwargs)

    def delete(self,
               name,
               url,
               **kwargs):
        """
        Shorthand for DELETE requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(name, url, method='DELETE', **kwargs)


class HttpSettings(Settings):
    pass
