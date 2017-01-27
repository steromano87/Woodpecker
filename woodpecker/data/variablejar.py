import datetime

import six

from woodpecker.settings.basesettings import BaseSettings


class VariableJar(object):
    def __init__(self, settings=BaseSettings()):
        # Internal public variables storage
        self._public_variables = {}

        # Reserved variables
        self._reserved_variables = {}

        # Internal settings object
        self._settings = settings

        # Set (reset) the default values
        self.reset()

    def set(self, name, value):
        if name not in six.viewkeys(self._reserved_variables):
            self._public_variables[name] = value
            self._reserved_variables['last_updated_on'] = \
                datetime.datetime.now()
            self._reserved_variables['last_updated_item'] = name
        else:
            raise KeyError("The variable name '{name}' is reserved "
                           "and cannot be used".format(name=name))

    def get(self, name):
        if name not in six.viewkeys(self._reserved_variables):
            if name in six.viewkeys(self._public_variables):
                return self._public_variables.get(name)
            else:
                if self._settings.get('runtime',
                                      'raise_error_if_variable_not_defined'):
                    raise KeyError("The variable '{name}' "
                                   "is not defined".format(name=name))
                else:
                    # FIXME: understand how to show warning and return the value
                    return name
        else:
            raise KeyError("The variable name '{name}' is reserved "
                           "and cannot be used".format(name=name))

    def is_set(self, name):
        return name in six.viewkeys(self._public_variables)

    def delete(self, name):
        if name not in six.viewkeys(self._reserved_variables):
            if name in six.viewkeys(self._public_variables):
                self._public_variables.pop(name)
                self._reserved_variables['last_updated_on'] = \
                    datetime.datetime.now()
                self._reserved_variables['last_updated_item'] = name
            else:
                if self._settings.get('runtime',
                                      'raise_error_if_variable_not_defined'):
                    raise KeyError("The variable '{name}' "
                                   "is not defined".format(name=name))
        else:
            raise KeyError("The variable name '{name}' is reserved "
                           "and cannot be used".format(name=name))

    def reset(self):
        self._public_variables = {}
        self._reserved_variables = {
            'last_updated_on': datetime.datetime.now(),
            'last_updated_item': None,
            'pecker_id': None,
            'current_sequence': None,
            'current_iteration': 0
        }

    def set_pecker_id(self, pecker_id):
        self._reserved_variables['pecker_id'] = pecker_id

    def set_current_sequence(self, sequence_name):
        self._reserved_variables['current_sequence'] = sequence_name

    def set_current_iteration(self, iteration):
        self._reserved_variables['current_iteration'] = iteration

    def get_pecker_id(self):
        return self._reserved_variables['pecker_id']

    def get_current_sequence(self):
        return self._reserved_variables['current_sequence']

    def get_current_iteration(self):
        return self._reserved_variables['current_iteration']
