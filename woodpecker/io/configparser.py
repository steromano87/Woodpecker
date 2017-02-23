import yaml
import os

from woodpecker.settings.basesettings import BaseSettings


class ConfigParser(object):
    def __init__(self, configfile='woodpecker.yml'):
        # Absolute path to config file
        self._config_file_path = os.path.abspath(configfile)

        # Unparsed config file content
        self._config_file_content = None

        # Scenarios and navs section
        self._scenarios = {}

        # Global settings
        self._global_settings = {}

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
            output_data = dict(settings=BaseSettings.default_values())
            yaml.safe_dump(output_data, fp, default_flow_style=False)
        self._parse_content()

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
            return {
                sequence_type: self._scenarios.get(scenario, {})[
                    'sessions'][session][sequence_type]
                for sequence_type in ['set_up', 'sequences', 'tear_down']
            }

    def _parse_content(self):
        self._scenarios = self._config_file_content.get('scenarios', {})
        self._global_settings = self._config_file_content.get('settings', {})
