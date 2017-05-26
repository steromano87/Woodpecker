from configobj import ConfigObj

from woodpecker.misc.contrib.validate import Validator


class BaseSequenceSettings(ConfigObj):
    def __init__(self, **kwargs):
        super(BaseSequenceSettings, self).__init__({
                'runtime': {
                    'raise_error_if_variable_not_defined': False,
                    'each_sequence_is_stopwatch': True
                }
            },
            interpolation=False,
            configspec=BaseSequenceSettings.default_settings_validator(),
            **kwargs
        )

        self.validator = Validator()

    @staticmethod
    def default_settings_validator():
        return ConfigObj({
            'runtime': {
                'raise_error_if_variable_not_defined':
                    'boolean(default=False)',
                'each_sequence_is_stopwatch': 'boolean(default=True)'
            }
        }, interpolation=False)
