import os
import six
import pprint

import yaml
import cerberus


class Settings(object):
    """
    Abstract class that is subclassed by the settings specific
    to each sequence type
    """
    def __init__(self, configfile='woodpecker.yml'):
        # Absolute path to Config file
        self._configfile = os.path.abspath(configfile)

        # Settings data
        self._data = {}

        # Validation mask
        self._validation_mask = self.validation_mask()

        # Default data
        self._default_values = self.default_values()

        # Internal validator
        self._validator = cerberus.Validator(self._validation_mask,
                                             purge_unknown=True,
                                             allow_unknown=False,
                                             root_allow_unknown=False)

        # Load settings data
        self.load()

    def load(self):
        if os.path.isfile(self._configfile):
            with open(self._configfile, 'r') as fp:
                self._data = self._validator.validated(yaml.safe_load(fp))
        else:
            self._data = self._validator.validated(self._default_values)

    def save(self):
        with open(self._configfile, 'w') as pf:
            yaml.dump(self._data, stream=pf)

    def get(self, section, entry):
        if section in six.viewkeys(self._data):
            if entry in six.viewkeys(self._data.get(section, {})):
                return self._data.get(section).get(entry)
            else:
                raise KeyError(
                    'The entry {entry} does not exist '
                    'in section {section}'.format(entry=entry, section=section)
                )
        else:
            raise KeyError('The section {section} does not exist'.format(
                section=section
            ))

    def set(self, *args):
        # If there are exactly 3 args, treat them as section - key - value
        if len(args) == 3:
            dic_setting = {args[0]: {args[1]: args[2]}}
        # If there is only one arg, treat it as dict
        elif len(args) == 1:
            dic_setting = args[0]
        # Raise exception otherwise
        else:
            raise ValueError('Only dicts or section-key-value form is allowed')

        if self._validator.validate(dic_setting) \
                and self._validator.validated(dic_setting) == dic_setting:
            # Iterate over keys to set the values
            for str_section in six.iterkeys(
                    self._validator.validated(dic_setting)):
                for str_key, str_value in six.iteritems(
                        dic_setting[str_section]):
                    self._data[str_section][str_key] = str_value
        else:
            raise ValueError('Error in input values:\n{error_list}'.format(
                error_list=pprint.pformat(self._validator.errors, indent=2)
            ))

    def dump(self):
        return self._data

    def __repr__(self):
        return self.dump()

    def validate(self):
        try:
            return self._validator.validate(self._data), \
                   pprint.pformat(self._validator.errors)
        except cerberus.DocumentError as error:
            return False, str(error)

    def extend(self, additional_settings):
        if isinstance(additional_settings, Settings):
            additional_settings.load()
            (bool_is_valid, str_message) = additional_settings.validate()
            if bool_is_valid:
                self._validation_mask.update(
                    additional_settings._validation_mask
                )
                self._default_values.update(
                    additional_settings._default_values
                )
            else:
                raise ValueError('Given settings are not self-consistent:\n'
                                 '{errors}'.format(errors=str_message)
                                 )
        else:
            raise TypeError('Wrong type: provided settings are not an '
                            'instance of Woodpecker settings')
        # Reload and validate default settings
        self._data = self._validator.validated(self._default_values)

    @staticmethod
    def validation_mask():
        return {}

    @staticmethod
    def default_values():
        return {}
