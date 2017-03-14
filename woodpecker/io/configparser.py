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

        # Scenarios and tasks section
        self._scenarios = None

        # Global settings
        self._global_settings = None

    def load(self):
        """
        Opens the specified file and loads its content

        :rtype: None
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

    def init(self, forced=False):
        """
        Initializes the config file using the default settings

        :rtype: None
        """
        # If file already exists and forced mode is not set, raise an exception
        if os.path.isfile(self._config_file_path) and not forced:
            raise IOError('Config file already exists, cannot initialize')

        # If file is not present, or forced mode is set, write file
        with open(self._config_file_path, 'wb') as fp:
            self._config_file_content = dict(
                settings=BaseSettings.default_values()
            )
            yaml.safe_dump(self._config_file_content,
                           fp,
                           default_flow_style=False)
        self._parse_content()

    def dump(self):
        """
        Writes to file the existing data

        :rtype: None
        """
        with open(self._config_file_path, 'wb') as fp:
            self._config_file_content = {
                'scenarios': self._scenarios,
                'settings': self._global_settings
            }
            yaml.safe_dump(self._config_file_content,
                           fp,
                           default_flow_style=False)

    def update(self):
        """
        Updates the existing config file by rebuilding the global settings

        :rtype: None
        """
        # Load the actual file content
        self.load()

        # Update global settings
        global_settings_class = self.build_global_settings()
        global_settings_class.set(self._global_settings)
        self._global_settings = global_settings_class.dump()

        # Dump the updated content to file
        self.dump()

    def list_scenarios(self):
        """
        Lists all the available scenarios

        :rtype: list
        :return: list
        """
        return self._scenarios.keys()

    def list_tasks_for(self, scenario):
        """
        Lists all the available tasks for the given scenario

        :rtype: list
        :param scenario: the given scenario
        :return: list
        """
        try:
            tasks = self._scenarios[scenario]['tasks'].keys()
        except KeyError:
            raise KeyError(
                'Scenario {scenario} not found'.format(
                    scenario=scenario
                )
            )
        else:
            return tasks

    def list_sequences_for(self, scenario, task):
        """
        Lists all the available sequences for the given scenario and task

        :rtype: list
        :param scenario: the given scenario
        :param task: the given task
        :return: list
        """
        try:
            sequence_types = \
                self._scenarios.get(scenario, {})['tasks'][task].keys()
        except KeyError:
            raise KeyError(
                'Task {task} not found '
                'inside scenario {scenario}'.format(
                    task=task,
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
                    'tasks'][task][sequence_type]
                for sequence_type in list(available_sequence_types)
            }

    def _parse_content(self):
        """
        Parses the raw file content into internal scenarios and settings

        :rtype: None
        """
        self._scenarios = self._config_file_content.get('scenarios', {})
        self._global_settings = self._config_file_content.get('settings', {})

    def build_global_settings(self):
        """
        Builds a settings class based on all loaded sequence types

        :rtype: woodpecker.settings.settings.Settings
        :return: Global settings class
        """
        # Initialize the classes list
        settings_classes = []

        # Retrieve all the scenarios
        scenarios = self.list_scenarios()

        # Retrieve all tasks for the current scenario
        for scenario in scenarios:
            tasks = self.list_tasks_for(scenario)

            # Retrieve settings class for each sequence
            for task in tasks:
                sequences = self.list_sequences_for(scenario, task)
                for sequence_lists in six.itervalues(sequences):
                    for sequence in sequence_lists:
                        sequence_class = functions.import_sequence(
                            sequence['file'],
                            sequence['class']
                        )
                        settings_classes.append(
                            sequence_class().default_settings()
                        )

        # Build the master scenario settings class
        # by coalescing all the settings classes
        global_settings = BaseSettings()
        for setting in settings_classes:
            global_settings.extend(setting)

        # Update master settings with the settings from the config file
        global_settings.set(self._global_settings)
        return global_settings

    def build_scenario_settings(self, scenario):
        """
        Builds the specific scenario settings

        :rtype: woodpecker.settings.settings.Settings
        :param scenario: the given scenario
        :return: scenario settings
        """

        # Retrieve global settings
        global_settings = self.build_global_settings()
        try:
            # Try to get scenario settings from file
            scenario_settings = self._scenarios[scenario].get('settings', {})
        except KeyError:
            raise KeyError(
                'Scenario {scenario} not found'.format(
                    scenario=scenario
                )
            )
        else:
            # If everything is ok, update settings
            global_settings.extend(scenario_settings)
            return global_settings

    def build_task_settings(self, scenario, task):
        """
        Builds the specific task settings

        :rtype: woodpecker.settings.settings.Settings
        :param scenario: the given scenario
        :param task: the given task
        :return: task settings
        """

        # First, retrieve scenario settings
        scenario_settings = self.build_scenario_settings(scenario)
        try:
            task_settings = \
                self._scenarios[scenario]['tasks'][task].get('settings', {})
        except KeyError:
            raise KeyError(
                'Task {task} not found '
                'inside scenario {scenario}'.format(
                    task=task,
                    scenario=scenario
                )
            )
        else:
            scenario_settings.extend(task_settings)
            return scenario_settings
