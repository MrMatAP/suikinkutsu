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
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import os
import pathlib
import enum
import json
from typing import Dict, Type
from argparse import ArgumentParser, Namespace

from water.outputs import WaterOutput
from water.blueprints import Blueprint
from water.platforms import Platform
from water.recipe import Recipe
from water.schema import WaterConfiguration
from water.constants import DEFAULT_CONFIG_FILE, ENV_CONFIG_FILE, DEFAULT_CONFIG_DIR, ENV_CONFIG_DIR, \
    DEFAULT_OUTPUT_CLASS, ENV_OUTPUT_CLASS, DEFAULT_PLATFORM_CLASS, ENV_PLATFORM_CLASS, DEFAULT_RECIPE_FILE, \
    ENV_RECIPE_FILE, ENV_SECRETS_FILE


@enum.unique
class Source(enum.Enum):
    DEFAULT = 'Default Value'
    CONFIGURATION = 'Configuration File'
    ENVIRONMENT = 'Environment Variable'
    CLI = 'CLI Parameter'

    def __str__(self):
        return self.value


class Runtime:
    platform: Platform
    recipe: Recipe

    def __init__(self):
        self.config_file = pathlib.Path(DEFAULT_CONFIG_FILE)
        self.config_file_source = Source.DEFAULT
        self.config_dir = pathlib.Path(DEFAULT_CONFIG_DIR)
        self.config_dir_source = Source.DEFAULT
        self._available_outputs = {clazz.name: clazz for clazz in WaterOutput.__subclasses__()}
        self.output = DEFAULT_OUTPUT_CLASS
        self.output_source = Source.DEFAULT
        self._available_blueprints = {cls.kind: cls for cls in Blueprint.__subclasses__()}
        self._available_platforms = {cls.name: cls() for cls in Platform.__subclasses__()}
        self.platform = DEFAULT_PLATFORM_CLASS
        self.platform_source = Source.DEFAULT
        self.recipe_file = pathlib.Path(DEFAULT_RECIPE_FILE)
        self.recipe_file_source = Source.DEFAULT
        self.recipe = Recipe(self)
        self.secrets_file = self.config_dir / f'{self.recipe_file.parent.name}.json'
        self.secrets_file_source = Source.DEFAULT
        self._secrets = {}
        # TODO
        self.raw_config = WaterConfiguration.construct()

        if ENV_CONFIG_FILE in os.environ:
            self.config_file = pathlib.Path(os.getenv(ENV_CONFIG_FILE))
            self.config_file_source = Source.ENVIRONMENT
        self.config_load()

        if ENV_CONFIG_DIR in os.environ:
            self.config_dir = pathlib.Path(os.getenv(ENV_CONFIG_DIR))
            self.config_dir_source = Source.ENVIRONMENT
        if ENV_OUTPUT_CLASS in os.environ:
            self.output = os.getenv(ENV_OUTPUT_CLASS)
            self.output_source = Source.ENVIRONMENT
        if ENV_PLATFORM_CLASS in os.environ:
            self.platform = os.getenv(ENV_PLATFORM_CLASS)
            self.platform_source = Source.ENVIRONMENT
        if ENV_RECIPE_FILE in os.environ:
            self.recipe_file = os.getenv(ENV_RECIPE_FILE)
            self.recipe_file_source = Source.ENVIRONMENT
        if ENV_SECRETS_FILE in os.environ:
            self.secrets_file = os.getenv(ENV_SECRETS_FILE)
            self.secrets_file_source = Source.ENVIRONMENT

    def cli_prepare(self, parser: ArgumentParser):
        parser.add_argument('-c',
                            dest='override_config_file',
                            required=False,
                            help='Override the water configuration file for this invocation')
        parser.add_argument('-d',
                            dest='override_config_dir',
                            required=False,
                            help='Override the directory into which configuration is generated for this invocation')
        parser.add_argument('-o', '--output',
                            dest='override_output',
                            choices=[name for name in self.available_outputs.keys()],
                            required=False,
                            help='Override the output style for this invocation')
        parser.add_argument('-p', '--platform',
                            dest='override_default_platform',
                            choices=[name for name in self.available_platforms.keys()],
                            required=False,
                            help='Override the default platform for this invocation')
        parser.add_argument('-s', '--secrets',
                            dest='override_secrets_file',
                            required=False,
                            help='Override the secrets file for this invocation')

    def cli_assess(self, args: Namespace):
        if args.override_config_file and args.override_config_file != DEFAULT_CONFIG_FILE:
            self.config_file = pathlib.Path(args.override_config_file)
            self.config_file_source = Source.CLI
            self.config_load()

        if args.override_config_dir and args.override_config_dir != DEFAULT_CONFIG_DIR:
            self.config_dir = args.override_config_dir
            self.config_dir_source = Source.CLI
        if args.override_output and args.override_output != DEFAULT_OUTPUT_CLASS:
            self.output = args.override_output
            self.output_source = Source.CLI
        if args.override_default_platform and args.override_default_platform != DEFAULT_PLATFORM_CLASS:
            self.platform = args.override_default_platform
            self.platform_source = Source.CLI
        if args.override_secrets_file:
            self.secrets_file = args.override_secrets_file
            self.secrets_file_source = Source.CLI
        self.secrets_load()

    def config_load(self):
        self.raw_config = WaterConfiguration.construct()
        if self.config_file.exists():
            raw_config = WaterConfiguration.parse_file(self.config_file)
        if self.raw_config.config_dir:
            self.config_dir = pathlib.Path(self.raw_config.config_dir)
            self.config_dir_source = Source.CONFIGURATION
        if self.raw_config.default_output:
            self.output = self.raw_config.default_output
            self.output_source = Source.CONFIGURATION
        if self.raw_config.default_platform:
            self.platform = raw_config.default_platform
            self.platform_source = Source.CONFIGURATION

    def config_save(self):
        config = WaterConfiguration(config_dir=self.config_dir,
                                    default_output=self.output.name,
                                    default_platform=self.platform.name)
        with open(self.config_file, 'w+', encoding='UTF-8') as c:
            json.dump(config.dict(), c, indent=2)

    def secrets_load(self):
        if self.secrets_file.exists():
            self._secrets = json.loads(self.secrets_file.read_text(encoding='UTF-8'))

    def secrets_save(self):
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)
        self.secrets_file.write_text(json.dumps(self.secrets))

    @property
    def config_file(self) -> pathlib.Path:
        return self._config_file

    @config_file.setter
    def config_file(self, value: pathlib.Path):
        self._config_file = value

    @property
    def config_file_source(self):
        return self._config_file_source

    @config_file_source.setter
    def config_file_source(self, value: Source):
        self._config_file_source = value

    @property
    def config_dir(self):
        return self._config_dir

    @config_dir.setter
    def config_dir(self, value):
        self._config_dir = value

    @property
    def config_dir_source(self):
        return self._config_dir_source

    @config_dir_source.setter
    def config_dir_source(self, value: Source):
        self._config_dir_source = value

    @property
    def available_outputs(self) -> Dict[str, Type[WaterOutput]]:
        return self._available_outputs

    @property
    def output(self) -> WaterOutput:
        return self._output

    @output.setter
    def output(self, value: str):
        if value not in self.available_outputs:
            raise ValueError(f'Configured output {value} is not available. Pick one of '
                             f'{str.join(",", self.available_outputs.keys())}')
        self._output = self.available_outputs.get(value)()

    @property
    def output_source(self):
        return self._output_source

    @output_source.setter
    def output_source(self, value: Source):
        self._output_source = value

    @property
    def available_blueprints(self) -> Dict[str, Type[Blueprint]]:
        return self._available_blueprints

    @property
    def available_platforms(self) -> Dict[str, Platform]:
        return self._available_platforms

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, value: str):
        if value not in self.available_platforms:
            raise ValueError(f'Configured platform {value} is not available. Pick on of '
                             f'{str.join(",", self.available_platforms.keys())}')
        self._platform = self.available_platforms.get(value)

    @property
    def platform_source(self):
        return self._platform_source

    @platform_source.setter
    def platform_source(self, value: Source):
        self._platform_source = value

    @property
    def recipe_file(self) -> pathlib.Path:
        return self._recipe_file

    @recipe_file.setter
    def recipe_file(self, value: pathlib.Path):
        self._recipe_file = value

    @property
    def recipe_file_source(self) -> Source:
        return self._recipe_file_source

    @recipe_file_source.setter
    def recipe_file_source(self, value: Source):
        self._recipe_file_source = value

    @property
    def recipe(self) -> Recipe:
        return self._recipe

    @recipe.setter
    def recipe(self, value: Recipe):
        self._recipe = value

    @property
    def secrets_file(self) -> pathlib.Path:
        return self._secrets_file

    @secrets_file.setter
    def secrets_file(self, value: pathlib.Path):
        self._secrets_file = value

    @property
    def secrets_file_source(self) -> Source:
        return self._secrets_file_source

    @secrets_file_source.setter
    def secrets_file_source(self, value: Source):
        self._secrets_file_source = value

    @property
    def secrets(self) -> Dict:
        return self._secrets
