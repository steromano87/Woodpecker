import abc
import re
import sys

import gevent
import grequests
import requests
import six

from woodpecker.io.variablejar import VariableJar
from woodpecker.sequences.basesequence import BaseSequence
from woodpecker.settings.httpsequencesettings import HttpSequenceSettings
from woodpecker.settings.coresettings import CoreSettings


class HttpSequence(BaseSequence):
    __metaclass__ = abc.ABCMeta

    def __init__(self,
                 settings=None,
                 log_queue=six.moves.queue.Queue(),
                 variables=VariableJar(),
                 stopwatches=None,
                 debug=False,
                 inline_log_sinks=(sys.stdout,)):

        # Call to super constructor
        super(HttpSequence, self).__init__(settings=settings,
                                           log_queue=log_queue,
                                           variables=variables,
                                           stopwatches=stopwatches,
                                           debug=debug,
                                           inline_log_sinks=inline_log_sinks)

        # Settings (automatically extended by the class settings)
        self.settings.merge(HttpSequence.default_settings())

        # Instantiates new session and last response variables in VariableJar
        if not self.variables.is_set('__http_session'):
            self.variables.set('__http_session', requests.Session())
        if not self.variables.is_set('__last_response'):
            self.variables.set('__last_response', None)

        # Add property to check if async pool is active
        self._async_request_pool_active = False
        self._async_request_pool = []

        # Add async request hooks to teardown hooks
        self._teardown_hooks.append(self._async_wait_hook)

    def _patch_kwargs(self, args):
        # Request headers
        args['headers'] = args.get(
            'headers', {'User-Agent': self.settings['http']['user_agent']})

        # Option to follow redirects or not
        args['allow_redirects'] = args.get(
            'allow_redirects', self.settings['http']['allow_redirects'])

        # Option to verify SSL certificates
        args['verify'] = args.get(
            'verify', not self.settings['http']['ignore_ssl_errors'])

        # Proxy settings
        args['proxies'] = args.get(
            'proxies',
            {
                'http-proxy': self.settings['http']['http_proxy'],
                'https-proxy': self.settings['http']['https_proxy']
            }
        )

        # Default timeout
        args['timeout'] = args.get(
            'timeout', self.settings['http']['default_timeout'])

        # If the Ignore SSL errors option is set to true,
        # disables the urllib InsecureRequestWarning message
        if not args['verify']:
            requests.packages.urllib3.disable_warnings()

    def start_async_pool(self):
        """
        Starts async requests pool. The added requests will be performed
        when a end_async call is made.
        """
        self._async_request_pool_active = True
        self._inline_logger.debug('Starting async requests pool')

    def end_async_pool(self):
        """
        End the async requests pool and flushes all the added async requests
        """
        self._async_request_pool_active = False
        grequests.map(self._async_request_pool,
                      size=self.settings['http'][
                          'max_async_concurrent_requests'],
                      exception_handler=self._async_exception_handler)
        self._async_request_pool = []
        self._inline_logger.debug('Async requests pool ended')

    def _async_wait_hook(self):
        # Wait for active Greenlets to complete
        # (but only if there are Greenlets to wait)
        if len(self._async_request_pool) > 0:
            gevent.joinall(self._async_request_pool)
            self._async_request_pool = []

    def set_header(self, header_name, header_value):
        session = self.variables.get('__http_session')
        session.headers.update({header_name, header_value})
        self.variables.set('__http_session', session)

    def set_cookie(self, cookie_name, cookie_value, **kwargs):
        session = self.variables.get('__http_session')
        session.cookies.set(cookie_name, cookie_value, **kwargs)
        self.variables.set('__http_session', session)

    def http_request(self,
                     url,
                     method='GET',
                     is_resource=False,
                     response_hooks=None,
                     with_resources=tuple(),
                     **kwargs):
        """
        Generic HTTP request

        :param url: the URL of the request
        :param method: a standard HTTP request method
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param with_resources: tuple containing the resource URLs
                               to be loaded alongside the main request.
                               The resource can be either a string or a tuple.
                               In the latter case, the second parameter
                               is optional and represents
                               the method to be used (defaults to GET)
        :param kwargs: arguments to be passed to requests library
        """
        # Patches kwargs with settings and defaults
        self._patch_kwargs(kwargs)

        # Add logging hook to existing hooks
        response_hooks = response_hooks or []
        kwargs.setdefault(
            'hooks', {'response': response_hooks}
        )
        kwargs['hooks']['response'].append(
            self._request_log_hook(is_async=False)
        )

        # Automatically replaces parameters in URL
        url = self._inject_variables(url)

        # Execute the request
        obj_session = self.variables.get('__http_session')
        try:
            obj_last_response = obj_session.request(method, url, **kwargs)
            if not is_resource:
                obj_last_response.raise_for_status()
            self.variables.set('__last_response', obj_last_response)

            # If there are resources, call them asynchronously
            if len(with_resources) > 0:
                self.start_async_pool()
                for resource in with_resources:
                    # If the resource is a tuple,
                    # pick both the URL and the method
                    if isinstance(resource, tuple):
                        self.async_http_request(
                            resource[0],
                            method=resource[1],
                            is_resource=True
                        )
                    # If the resource is a string, call it using GET method
                    else:
                        self.async_get(resource, is_resource=True)
                self.end_async_pool()

        except requests.exceptions.RequestException as error:
            self._inline_logger.error(str(error))
            self.log('event', {
                'event_type': 'error',
                'event_content': {
                    'sequence': self.variables.get_current_sequence(),
                    'iteration': self.variables.get_current_iteration(),
                    'pecker_id': self.variables.get_pecker_id(),
                    'url': url,
                    'error': str(error)
                }
            })
            raise error
        finally:
            self.variables.set('__http_session', obj_session)

    def get(self,
            url,
            is_resource=False,
            response_hooks=None,
            with_resources=tuple(),
            **kwargs):
        """
        Shorthand for GET requests

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param with_resources: tuple containing the resource URLs
                               to be loaded alongside the main request.
                               The resource can be either a string or a tuple.
                               In the latter case, the second parameter
                               is optional and represents
                               the method to be used (defaults to GET)
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url,
                          method='GET',
                          is_resource=is_resource,
                          response_hooks=response_hooks,
                          with_resources=with_resources,
                          **kwargs)

    def post(self,
             url,
             is_resource=False,
             response_hooks=None,
             with_resources=tuple(),
             **kwargs):
        """
        Shorthand for POST requests

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param with_resources: tuple containing the resource URLs
                               to be loaded alongside the main request.
                               The resource can be either a string or a tuple.
                               In the latter case, the second parameter
                               is optional and represents
                               the method to be used (defaults to GET)
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url,
                          method='POST',
                          is_resource=is_resource,
                          response_hooks=response_hooks,
                          with_resources=with_resources,
                          **kwargs)

    def put(self,
            url,
            is_resource=False,
            response_hooks=None,
            with_resources=tuple(),
            **kwargs):
        """
        Shorthand for PUT requests

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param with_resources: tuple containing the resource URLs
                               to be loaded alongside the main request.
                               The resource can be either a string or a tuple.
                               In the latter case, the second parameter
                               is optional and represents
                               the method to be used (defaults to GET)
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url,
                          method='PUT',
                          is_resource=is_resource,
                          response_hooks=response_hooks,
                          with_resources=with_resources,
                          **kwargs)

    def patch(self,
              url,
              is_resource=False,
              response_hooks=None,
              with_resources=tuple(),
              **kwargs):
        """
        Shorthand for PATCH requests

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param with_resources: tuple containing the resource URLs
                               to be loaded alongside the main request.
                               The resource can be either a string or a tuple.
                               In the latter case, the second parameter
                               is optional and represents
                               the method to be used (defaults to GET)
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url,
                          method='PATCH',
                          is_resource=is_resource,
                          response_hooks=response_hooks,
                          with_resources=with_resources,
                          **kwargs)

    def delete(self,
               url,
               is_resource=False,
               response_hooks=None,
               with_resources=tuple(),
               **kwargs):
        """
        Shorthand for DELETE requests

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.http_request(url,
                          method='DELETE',
                          is_resource=is_resource,
                          response_hooks=response_hooks,
                          with_resources=with_resources,
                          **kwargs)

    def _request_log_hook(self, is_async=False, is_resource=False):
        def _request_log_hook_gen(response, **kwargs):
            # Log request status in inline logger
            if is_async:
                str_inline_message = \
                    'HTTP Request (async) - {method} - {url} - ' \
                    '{status} - {elapsed} ms - {size} bytes'
            else:
                str_inline_message = 'HTTP Request - {method} - {url} - ' \
                                     '{status} - {elapsed} ms - {size} bytes'
            self._inline_logger.debug(str_inline_message.format(
                    method=response.request.method,
                    url=response.request.url,
                    status=' '.join((str(response.status_code),
                                     response.reason)),
                    elapsed=response.elapsed.total_seconds() * 1000,
                    size=len(response.content)
                ))

            # Log the result of the request
            self.log('step', {
                'step_type': 'http_request',
                'active_stopwatches': list(self._stopwatches.keys()),
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
                    'elapsed': response.elapsed.total_seconds() * 1000,
                    'async': is_async
                }
            })

            if is_async and not is_resource and not response.ok:
                response.raise_for_status()
        return _request_log_hook_gen

    def _async_exception_handler(self, request, exception):
        if not request.kwargs.get('is_resource', False):
            self._inline_logger.error(str(exception))
            self.log('event', {
                'event_type': 'error',
                'event_content': {
                    'sequence': self.variables.get_current_sequence(),
                    'iteration': self.variables.get_current_iteration(),
                    'pecker_id': self.variables.get_pecker_id(),
                    'url': request.url,
                    'error': str(exception)
                }
            })
            raise exception

    def async_http_request(self,
                           url,
                           method='GET',
                           is_resource=False,
                           response_hooks=None,
                           **kwargs):
        """
        Generic async HTTP request

        :param url: the URL of the request
        :param method: a standard HTTP request method
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        # Patches kwargs
        self._patch_kwargs(kwargs)

        # Add specific header for async request (XHR)
        kwargs['headers'].update({'X-Requested-With': 'XMLHttpRequest'})

        # Automatically replaces parameters in URL
        url = self._inject_variables(url)

        # Add async response log hook to existing hooks
        response_hooks = response_hooks or []
        kwargs.setdefault(
            'hooks', {'response': response_hooks}
        )
        kwargs['hooks']['response'].append(
            self._request_log_hook(is_async=True, is_resource=is_resource)
        )

        # Create base request
        obj_session = self.variables.get('__http_session')
        obj_async_request = grequests.AsyncRequest(method,
                                                   url,
                                                   session=obj_session,
                                                   **kwargs)

        # If async pool is active, add the quest to the pool
        if self._async_request_pool_active:
            self._async_request_pool.append(obj_async_request)
        else:
            # If async pool is not active, send the request immediately
            async_greenlet = grequests.send(
                obj_async_request,
                pool=grequests.Pool(
                    self.settings['http']['max_async_concurrent_requests']
                )
            )
            self._async_request_pool.append(async_greenlet)

    def async_get(self,
                  url,
                  is_resource=False,
                  response_hooks=None,
                  **kwargs):
        """
        Shorthand for GET async request

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.async_http_request(url,
                                method='GET',
                                is_resource=is_resource,
                                response_hooks=response_hooks,
                                **kwargs)

    def async_post(self,
                   url,
                   is_resource=False,
                   response_hooks=None,
                   **kwargs):
        """
        Shorthand for POST async request

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.async_http_request(url,
                                method='POST',
                                is_resource=is_resource,
                                response_hooks=response_hooks,
                                **kwargs)

    def async_put(self,
                  url,
                  is_resource=False,
                  response_hooks=None,
                  **kwargs):
        """
        Shorthand for PUT async request

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.async_http_request(url,
                                method='PUT',
                                is_resource=is_resource,
                                response_hooks=response_hooks,
                                **kwargs)

    def async_patch(self,
                    url,
                    is_resource=False,
                    response_hooks=None,
                    **kwargs):
        """
        Shorthand for PATCH async request

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.async_http_request(url,
                                method='PATCH',
                                is_resource=is_resource,
                                response_hooks=response_hooks,
                                **kwargs)

    def async_delete(self,
                     url,
                     is_resource=False,
                     response_hooks=None,
                     **kwargs):
        """
        Shorthand for DELETE async request

        :param url: the URL of the request
        :param is_resource: tells if the requested item is a webpage
                            or a resource. If this parameter is set to true,
                            all HTTP errors will be ignored for this entry
        :param response_hooks: the list of hooks to apply to response
                               (assertions or parameter retrieval)
        :param kwargs: arguments to be passed to requests library
        """
        self.async_http_request(url,
                                method='DELETE',
                                is_resource=is_resource,
                                response_hooks=response_hooks,
                                **kwargs)

    # Assertions
    def assert_http_status(self, status):
        def _assert_hook(response, **kwargs):
            if response.status_code != status:
                raise AssertionError(
                    'Expected HTTP status {expected}, got {actual}'.format(
                        expected=status,
                        actual=response.status_code
                    )
                )
            else:
                self._inline_logger.debug(
                    'HTTP Status matched the expected code '
                    '{status_code}'.format(
                        status_code=status
                    )
                )
        return _assert_hook

    def assert_body_has_text(self, target):
        def _assert_hook(response, **kwargs):
            if target not in response.content.decode(response.encoding):
                raise AssertionError(
                    'Cannot find "{target}" in response body'.format(
                        target=target
                    )
                )
            else:
                self._inline_logger.debug(
                    'Text "{target}" correctly found in response body'.format(
                        target=target
                    )
                )
        return _assert_hook

    def assert_header_value(self, key, value):
        def _assert_hook(response, **kwargs):
            if response.headers.get(key, None) is None:
                raise AssertionError(
                    'The header "{key}" is not present '
                    'in response header'.format(
                        key=key
                    )
                )
            elif response.headers.get(key, None) != value:
                raise AssertionError(
                    'Expected header "{key}" to have value "{value}", '
                    'got "{actual}" instead'.format(
                        key=key,
                        value=value,
                        actual=response.headers.get(key, None)
                    )
                )
            else:
                self._inline_logger.debug(
                    'Header "{key}" matched '
                    'the expected value "{value}"'.format(
                        key=key,
                        value=value
                    )
                )
        return _assert_hook

    def assert_body_has_regex(self, regex):
        def _assert_hook(response, **kwargs):
            if re.search(regex,
                         response.content.decode(response.encoding)) is None:
                raise AssertionError(
                    'Cannot match regex "{regex}" in response body'.format(
                        regex=regex
                    )
                )
            else:
                self._inline_logger.debug(
                    'Regex "{regex}" matched '
                    'successfully in response body'.format(
                        regex=regex
                    )
                )
        return _assert_hook

    def assert_elapsed_within(self, amount_msec):
        def _assert_hook(response, **kwargs):
            if response.elapsed.total_seconds() * 1000 > amount_msec:
                raise AssertionError(
                    'Request did not complete within {amount} ms, '
                    'elapsed time was {real_elapsed} ms'.format(
                        amount=amount_msec,
                        real_elapsed=response.elapsed.total_seconds() * 1000
                    )
                )
            else:
                self._inline_logger.debug(
                    'Request completed within {threshold} ms: '
                    'elapsed time was {elapsed} ms'.format(
                        threshold=amount_msec,
                        elapsed=response.elapsed.total_seconds() * 1000
                    )
                )
        return _assert_hook

    # Variables retrieval
    def var_from_regex(self,
                       name,
                       regex,
                       target='body',
                       instances='first',
                       group=0):
        def _param_hook(response, **kwargs):
            # Find the target of regex
            targets = {
                'url': response.url,
                'body': response.content.decode(response.encoding),
                'headers': '\n'.join(
                    [': '.join((str(key), str(value)))
                     for key, value in six.iteritems(response.headers)]
                ),
                'all': '\n'.join((
                    response.url,
                    '\n'.join(
                        [': '.join((str(key), str(value)))
                         for key, value in six.iteritems(response.headers)]
                    ),
                    response.content.decode(response.encoding)
                ))
            }
            target_string = targets.get(target, response.content)

            # If match is not found, raise exception, else save the parameter
            if re.search(regex, target_string) is None:
                raise IOError(
                    'Cannot save the parameter "{name}", '
                    'no match found for regex "{regex}" in {target}'.format(
                        regex=regex,
                        name=name,
                        target=target
                    )
                )
            else:
                matches = re.findall(regex, target_string)
                if instances == 'first' or len(matches) == 1:
                    parameter = matches[0]
                    # Check for capturing groups, if more are present
                    if isinstance(parameter, tuple):
                        parameter = parameter[group]
                else:
                    parameter = matches
                self.variables.set(name, parameter)
                self._inline_logger.debug(
                    'Saved parameter "{name}": "{value}"'.format(
                        name=name,
                        value=parameter
                    )
                )
        return _param_hook

    @staticmethod
    def default_settings():
        return HttpSequenceSettings()
