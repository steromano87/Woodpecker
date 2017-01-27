from woodpecker.settings.settings import Settings


class HttpSettings(Settings):
    @staticmethod
    def default_values():
        return {
            'http': {
                'default_request_headers': {},
                'allow_redirects': True,
                'ignore_ssl_errors': True,
                'proxies': {},
                'default_timeout': 5.0
            }
        }

    @staticmethod
    def validation_mask():
        return {
            'http': {
                'type': 'dict',
                'schema': {
                    'default_request_headers': {
                        'type': 'dict'
                    },
                    'allow_redirects': {
                        'type': 'boolean'
                    },
                    'ignore_ssl_errors': {
                        'type': 'boolean'
                    },
                    'proxies': {
                        'type': 'dict'
                    },
                    'default_timeout': {
                        'type': 'number',
                        'min': 0.0,
                        'coerce': float
                    }
                }
            }
        }
