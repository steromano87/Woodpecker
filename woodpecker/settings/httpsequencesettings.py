from configobj import ConfigObj

from woodpecker.misc.contrib.validate import Validator


class HttpSequenceSettings(ConfigObj):
    def __init__(self, **kwargs):
        super(HttpSequenceSettings, self).__init__({
                'http': {
                    'user_agent': 'Google Chrome 58',
                    'allow_redirects': True,
                    'ignore_ssl_errors': True,
                    'http_proxy': None,
                    'https_proxy': None,
                    'default_timeout': 5.0,
                    'max_async_concurrent_requests': 10
                }
            },
                interpolation=False,
                configspec=HttpSettings.default_settings_validator(),
                **kwargs
            )

        self.validator = Validator()

    @staticmethod
    def default_settings_validator():
        return ConfigObj({
            'http': {
                'user_agent': "string(min=0, default='Google Chrome 58')",
                'allow_redirects': 'boolean(default=True)',
                'ignore_ssl_errors': 'boolean(default=True)',
                'http_proxy': 'string',
                'https_proxy': 'string',
                'default_timeout': 'float(min=0.0, default=5.0)',
                'max_async_concurrent_requests': 'integer(min=0, default=10)'
            }
        }, interpolation=False)
