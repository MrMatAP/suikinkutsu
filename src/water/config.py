#  MIT License
#
#  Copyright (c) 2022 Mathieu Imfeld
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
import argparse
import typing
import pathlib
import enum
import collections
import pydantic
import water.constants


class WaterConfiguration(pydantic.BaseModel):
    config_dir: str = pydantic.Field(description='Directory into which water generates configuration files',
                                     default=None)
    default_output: str = pydantic.Field(description='Default output format', default=None)
    default_platform: str = pydantic.Field(description='Default platform', default=None)

    def display_dict(self) -> collections.OrderedDict:
        return collections.OrderedDict(self.dict())


@enum.unique
class Source(enum.Enum):
    """
    Sources from which configurable items can be configured from
    """
    DEFAULT = 'Default Value'
    CONFIGURATION = 'Configuration File'
    ENVIRONMENT = 'Environment Variable'
    CLI = 'CLI Parameter'

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'Source.{self.name}'


class ConfigurableItem(object):
    """
    A configurable item with a name, value and source from where it was configured
    """

    def __init__(self,
                 name: str,
                 source: Source,
                 env_override: str,
                 default_value: typing.Any):
        self._name = name
        self._source = source
        self._env_override = env_override
        self._value = default_value
        if env_override in os.environ:
            self._source = Source.ENVIRONMENT
            self._value = os.environ.get(env_override)

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> Source:
        return self._source

    @source.setter
    def source(self, value: Source):
        self._source = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: typing.Any):
        self._value = value

    @property
    def env_override(self):
        return self._env_override

    def update_from_cli(self, cli_value) -> bool:
        """
        Update this configuration item with a value that may have been set via the CLI. Configuration updates
        via CLI override all configuration sources.
        Args:
            cli_value: The CLI value

        Returns:
            True if the CLI has overridden this value, False otherwise
        """
        if cli_value and cli_value != self._value:
            self.source = Source.CLI
            self.value = cli_value
            return True
        return False

    def update_from_file(self, file_value) -> bool:
        """
        Update this configuration item with a value that may have been set via the config file. Configuration updates
        via a config file only override those with a DEFAULT source, but not those with ENV or CLI source
        Args:
            file_value: The config file value

        Returns:
            True if the config file has overriden this value, False otherwise
        """
        if self.source in [Source.CLI, Source.ENVIRONMENT]:
            return False
        self.value = file_value
        self.source = Source.CONFIGURATION

    def __repr__(self):
        return f'ConfigurableItem({self._name}, {self._source}, {self._value})'

    def __str__(self):
        return str(self._value)


class WaterConfig(object):

    def __init__(self):
        self._config_file = ConfigurableItem(
            name='config_file',
            source=Source.DEFAULT,
            env_override=water.constants.ENV_CONFIG_FILE,
            default_value=water.constants.DEFAULT_CONFIG_FILE)
        self._config_dir = ConfigurableItem(
            name='config_dir',
            source=Source.DEFAULT,
            env_override=water.constants.ENV_CONFIG_DIR,
            default_value=water.constants.DEFAULT_CONFIG_DIR)
        self._recipe_file = ConfigurableItem(
            name='recipe_file',
            source=Source.DEFAULT,
            env_override=water.constants.ENV_RECIPE_FILE,
            default_value=water.constants.DEFAULT_RECIPE_FILE)

        config_dir_path = pathlib.Path(self._config_dir.value)
        recipe_file_path = pathlib.Path(self._recipe_file.value)
        self._secrets_file = ConfigurableItem(
            name='secrets_file',
            source=Source.DEFAULT,
            env_override=water.constants.ENV_SECRETS_FILE,
            default_value=str(pathlib.Path(config_dir_path / f'{recipe_file_path.parent.name}.json')))

        if self._config_file.source == Source.ENVIRONMENT:
            self.config_load()

    def cli_prepare(self, parser: argparse.ArgumentParser):
        parser.add_argument('-c',
                            dest=water.constants.CLI_CONFIG_FILE,
                            default=self.config_file.value,
                            required=False,
                            help='Override the water configuration file for this invocation')
        parser.add_argument('-d',
                            dest=water.constants.CLI_CONFIG_DIR,
                            default=self.config_dir.value,
                            required=False,
                            help='Override the directory into which configuration is generated for this invocation')
        parser.add_argument('-r',
                            dest=water.constants.CLI_RECIPE_FILE,
                            default=self.recipe_file.value,
                            required=False,
                            help='Override the recipe file for this invocation')
        parser.add_argument('-s', '--secrets',
                            dest=water.constants.CLI_SECRETS_FILE,
                            default=self.secrets_file.value,
                            required=False,
                            help='Override the secrets file for this invocation')

    def cli_assess(self, args: argparse.Namespace):
        if self._config_file.update_from_cli(args.override_config_file):
            self.config_load()
        self._config_dir.update_from_cli(args.override_config_dir)
        self._recipe_file.update_from_cli(args.override_recipe_file)
        self._secrets_file.update_from_cli(args.override_secrets_file)

    def config_load(self):
        config_file_path = pathlib.Path(self.config_file.value)
        if not config_file_path.exists():
            return
        raw_config = WaterConfiguration.parse_file(config_file_path)
        self._config_dir.update_from_file(raw_config.config_dir)
        # TODO: default_output and default_platform

    @property
    def config_file(self):
        return self._config_file

    @property
    def config_dir(self):
        return self._config_dir

    @property
    def recipe_file(self):
        return self._recipe_file

    @property
    def secrets_file(self):
        return self._secrets_file
