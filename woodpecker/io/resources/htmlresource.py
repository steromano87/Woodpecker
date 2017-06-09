import urllib

from woodpecker.io.resources.baseresource import BaseResource


class HtmlResource(BaseResource):
    def __init__(self, name=None):
        # Call to BaseResource init method
        super(HtmlResource, self).__init__(name)

        # Resource URL
        self.url = None

        # Resource call HTTP method
        self.method = 'GET'

        # Resource HTTP request specs
        self.request = HtmlRequest()

        # Resource HTTP response specs
        self.response = HtmlResponse()

    def __repr__(self):
        return '{classname} - {method} - {name}'.format(
            classname=self.__class__.__name__,
            method=self.method,
            name=self.url,
        )

    def mime_type(self):
        if self.response.mime_type is None:
            return self.request.mime_type
        elif self.response.mime_type in self.request.mime_type \
                or '*/*' in self.request.mime_type \
                or '{first}/*'.format(
                    first=self.response.mime_type.split('/')[0]) \
                or '*/{second}'.format(
                    second=self.response.mime_type.split('/')[1]):
            return self.response.mime_type
        else:
            return self.request.mime_type, self.response.mime_type


class HtmlRequest(object):
    def __init__(self):
        self.params = dict()
        self.form_data = dict()
        self.cookies = []
        self.headers = dict()
        self.user_agent = None
        self.mime_type = []
        self.payload = None

    def parse_query_string(self, query_string):
        for param_couple in query_string.split('&'):
            split_params = param_couple.split('=')
            self.params[urllib.unquote_plus(split_params[0])] = \
                urllib.unquote_plus(split_params[1])

    def parse_form_data(self, form_data):
        for param_couple in form_data.split('&'):
            split_params = param_couple.split('=')
            self.form_data[urllib.unquote_plus(split_params[0])] = \
                urllib.unquote_plus(split_params[1])

    def parse_cookie_header(self, cookie_string):
        cookies = cookie_string.split(';')
        for cookie in cookies:
            self.cookies.append({
                'name': urllib.unquote_plus(cookie.split('=')[0].strip()),
                'value': urllib.unquote_plus(cookie.split('=')[1].strip()),
                'expires': None,
                'httponly': False,
                'secure': False
            })


class HtmlResponse(object):
    def __init__(self):
        self.status = None
        self.cookies = []
        self.content = None
        self.size = 0
        self.headers = dict()
        self.mime_type = None

    def parse_set_cookie_header(self, cookie_string):
        cookie_dict = {}
        cookie_pairs = cookie_string.split('; ')
        for cookie_entry in cookie_pairs:
            cookie_couple = cookie_entry.split('=')
            if cookie_couple[0].lower() \
                    not in ('expires', 'max-age', 'domain', 'path',
                            'secure', 'httponly', 'samesite'):
                cookie_dict['name'] = urllib.unquote_plus(cookie_couple[0])
                cookie_dict['value'] = urllib.unquote_plus(cookie_couple[1])
            elif cookie_couple[0].lower() in ('secure', 'httponly'):
                cookie_dict[cookie_couple[0].lower()] = True
            else:
                cookie_dict[cookie_couple[0].lower()] = \
                    urllib.unquote_plus(cookie_couple[1])
        self.cookies.append(cookie_dict)
