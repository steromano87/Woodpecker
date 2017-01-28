import abc
import six
import sys

import requests
import grequests

from woodpecker.settings.httpsettings import HttpSettings
from woodpecker.settings.basesettings import BaseSettings
from woodpecker.data.variablejar import VariableJar
from woodpecker.sequences.basesequence import BaseSequence


class HttpSequence(BaseSequence):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=HttpSettings(),
                 log_queue=six.moves.queue.Queue(),
                 variables=VariableJar(),
                 parameters=None,
                 transactions=None,
                 debug=False,
                 inline_log_sinks=(sys.stdout,)):
        # Extend the standard settings
        obj_settings = BaseSettings()
        settings.extend(obj_settings)
        super(HttpSequence, self).__init__(settings=settings,
                                           log_queue=log_queue,
                                           variables=variables,
                                           parameters=parameters,
                                           transactions=transactions,
                                           debug=debug,
                                           inline_log_sinks=inline_log_sinks)
        if not self.variables.is_set('__http_session'):
            self.variables.set('__http_session', requests.Session())
        if not self.variables.is_set('__last_response'):
            self.variables.set('__last_response', None)

    @staticmethod
    def default_settings():
        return HttpSettings()

    def http_request(self,
                     url,
                     method='GET',
                     **kwargs):
        """
        Generic HTTP request

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

        # Add logging hook
        kwargs['hooks'] = {'response': self._request_log_hook}

        # Execute the request
        obj_session = self.variables.get('__http_session')
        try:
            obj_last_response = obj_session.request(method, url, **kwargs)
            self.variables.set('__last_response', obj_last_response)
        except requests.exceptions.SSLError as error:
            self._inline_logger.error(
                'SSL error - {method} - {url} - {message}'.format(
                    method=method,
                    url=url,
                    message=str(error)
                )
            )
        finally:
            self.variables.set('__http_session', obj_session)

    def get(self,
            url,
            **kwargs):
        """
        Shorthand for GET requests

        :param name: the name of the request (useful for logging)
        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url, method='GET', **kwargs)

    def post(self,
             url,
             **kwargs):
        """
        Shorthand for POST requests

        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url, method='POST', **kwargs)

    def put(self,
            url,
            **kwargs):
        """
        Shorthand for PUT requests

        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url, method='PUT', **kwargs)

    def patch(self,
              url,
              **kwargs):
        """
        Shorthand for PATCH requests

        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url, method='PATCH', **kwargs)

    def delete(self,
               url,
               **kwargs):
        """
        Shorthand for DELETE requests

        :param url: the URL of the request
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url, method='DELETE', **kwargs)

    def _request_log_hook(self, response, **kwargs):
        # Log request status in inline logger
        self._inline_logger.debug(
            'HTTP Request - {method} - {url} - '
            '{status} - {elapsed} ms - {size} bytes'.format(
                method=response.request.method,
                url=response.request.url,
                status=' '.join((str(response.status_code), response.reason)),
                elapsed=response.elapsed.total_seconds() * 1000,
                size=len(response.content)
            ))

        # Log the result of the request
        self.log('step', {
            'step_type': 'http_request',
            'active_transactions': self._transactions.keys(),
            'step_content': {
                'url': response.request.url,
                'method': response.request.method,
                'body': response.request.body,
                # Conversion from CaseInsensitive dict to normal dict
                'headers': dict(response.request.headers),
                'response_url': response.url,
                'response_status': ' '.join((str(response.status_code),
                                             response.reason)),
                'response_size': len(response.content),
                'elapsed': response.elapsed.total_seconds() * 1000
            }
        })
