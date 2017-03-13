import yaml
import os
import six

import woodpecker.misc.functions as functions

from woodpecker.settings.basesettings import BaseSettings


class ConfigParser(object):
    def __init__(self, configfile='woodpecker.yml'):
        # Absolute path to config file
        self._config_file_path = os.path.abspath(configfile)

        # Unparsed config file content
        self._config_file_content = None

        # Scenarios and sessions section
        self._scenarios = None

        # Global settings
        self._global_settings = None

    def load(self):
        """
        Opens the specified file and loads its content

        :return: None
        """
        try:
            with open(self._config_file_path, 'rb') as fp:
                self._config_file_content = yaml.safe_load(fp)
        except IOError:
            raise IOError('The specified file {path} cannot be found'.format(
                path=self._config_file_path
            ))
        else:
            self._parse_content()

    def init(self):
        """
        Initializes the config file using the default settings

        :return: None
        """
        with open(self._config_file_path, 'wb') as fp:
            self._config_file_content = dict(
                settings=BaseSettings.default_values()
            )
            yaml.safe_dump(self._config_file_content,
                           fp,
                           default_flow_style=False)
        self._parse_content()

    def dump(self):
        with open(self._config_file_path, 'wb') as fp:
            self._config_file_content = {
                'scenarios': self._scenarios,
                'settings': self._global_settings
            }
            yaml.safe_dump(self._config_file_content,
                           fp,
                           default_flow_style=False)

    def list_scenarios(self):
        return self._scenarios.keys()

    def list_sessions_for(self, scenario):
        try:
            sessions = self._scenarios[scenario]['sessions'].keys()
        except KeyError:
            raise KeyError(
                'Scenario {scenario} not found'.format(
                    scenario=scenario
                )
            )
        else:
            return sessions

    def list_sequences_for(self, scenario, session):
        try:
            sequence_types = \
                self._scenarios.get(scenario, {})['sessions'][session].keys()
        except KeyError:
            raise KeyError(
                'Session {session} not found '
                'inside scenario {scenario}'.format(
                    session=session,
                    scenario=scenario
                )
            )
        else:
            available_sequence_types = \
                set(sequence_types).intersection(
                    ['set_up', 'sequences', 'tear_down']
                )
            return {
                sequence_type: self._scenarios.get(scenario, {})[
                    'sessions'][session][sequence_type]
                for sequence_type in list(available_sequence_types)
            }

    def _parse_content(self):
        self._scenarios = self._config_file_content.get('scenarios', {})
        self._global_settings = self._config_file_content.get('settings', {})

    def _build_scenario_settings(self, scenario):
        # Retrieve all sessions for the current scenario
        settings_classes = []
        sessions = self.list_sessions_for(scenario)

        # Retrieve settings class for each sequence
        for session in sessions:
            sequences = self.list_sequences_for(scenario, session)
            for sequence_lists in six.itervalues(sequences):
                for sequence in sequence_lists:
                    sequence_class = functions.import_sequence(
                        sequence['file'],
                        sequence['class']
                    )
                    settings_classes.append(sequence_class.default_settings())

        # Build the master scenario settings class
        # by coalescing all the settings classes
        master_settings = BaseSettings()
        for setting in settings_classes:
            master_settings.extend(setting)
        return master_settings
