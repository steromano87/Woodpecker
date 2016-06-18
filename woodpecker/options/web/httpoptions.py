def http_options():
    return {
        'ignore_ssl_errors': True,
        'follow_redirects': True,
        'default_request_method': 'GET',
        'default_request_headers': {},
        'default_request_cookies': {},
        'proxy': {}
    }
