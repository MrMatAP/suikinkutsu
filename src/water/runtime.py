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
from typing import List, Dict, Optional, Any
from argparse import ArgumentParser, Namespace

from water.exceptions import MurkyWaterException
from water.outputs import Output
from water.blueprints import Blueprint, BlueprintInstance, BlueprintInstanceList
from water.platforms import WaterPlatform
from water.schema import WaterConfiguration
from water.constants import DEFAULT_CONFIG_FILE, ENV_CONFIG_FILE, DEFAULT_CONFIG_DIR, ENV_CONFIG_DIR, \
    DEFAULT_OUTPUT_CLASS, ENV_OUTPUT_CLASS, DEFAULT_PLATFORM_CLASS, ENV_PLATFORM_CLASS, DEFAULT_RECIPE_FILE, \
    ENV_RECIPE_FILE, ENV_SECRETS_FILE


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


class ConfigurableItem:
    """
    A configurable item with a name, value and source from where it was configured
    """

    def __init__(self, name: str, source: Source, value: Any):
        self._name = name
        self._source = source
        self._value = value

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
    def value(self, value: Any):
        self._value = value

    def __repr__(self):
        return f'ConfigurableItem({self._name}, {self._source}, {self._value})'

    def __str__(self):
        return str(self._value)


class Runtime:
    """
    The runtime of all platforms, blueprints and their instances
    """

    def __init__(self):
        self._output_class = ConfigurableItem('output_class', Source.DEFAULT, DEFAULT_OUTPUT_CLASS)
        self._platform_class = ConfigurableItem('platform_class', Source.DEFAULT, DEFAULT_PLATFORM_CLASS)
        self._config_file = ConfigurableItem('config_file', Source.DEFAULT, pathlib.Path(DEFAULT_CONFIG_FILE))
        self._config_dir = ConfigurableItem('config_dir', Source.DEFAULT, pathlib.Path(DEFAULT_CONFIG_DIR))
        self._recipe_file = ConfigurableItem('recipe_file', Source.DEFAULT, pathlib.Path(DEFAULT_RECIPE_FILE))
        self._secrets_file = ConfigurableItem('secrets_file',
                                              Source.DEFAULT,
                                              pathlib.Path(self._config_dir.value
                                                           /
                                                           f'{self._recipe_file.value.parent.name}.json'))
        if ENV_CONFIG_FILE in os.environ:
            self._config_file.value = pathlib.Path(os.getenv(ENV_CONFIG_FILE))
            self._config_file.source = Source.ENVIRONMENT
        if ENV_CONFIG_DIR in os.environ:
            self._config_dir.value = pathlib.Path(os.getenv(ENV_CONFIG_DIR))
            self._config_dir.source = Source.ENVIRONMENT
        if ENV_RECIPE_FILE in os.environ:
            self._recipe_file.value = pathlib.Path(os.getenv(ENV_RECIPE_FILE))
            self._recipe_file.source = Source.ENVIRONMENT
        if ENV_SECRETS_FILE in os.environ:
            self._secrets_file.value = pathlib.Path(os.getenv(ENV_SECRETS_FILE))
            self._secrets_file.source = Source.ENVIRONMENT
        if ENV_OUTPUT_CLASS in os.environ:
            self._output_class.value = os.getenv(ENV_OUTPUT_CLASS)
            self._output_class.source = Source.ENVIRONMENT
        if ENV_PLATFORM_CLASS in os.environ:
            self._platform_class.value = os.getenv(ENV_PLATFORM_CLASS)
            self._platform_class.source = Source.ENVIRONMENT

        self._outputs: Dict[str, Output] = self._find_extensions(Output)
        #self._platforms = self._find_extensions(WaterPlatform)
        self._platforms = {}
        self._blueprints = self._find_extensions(Blueprint)
        #self._blueprints = {}
        self._instances: List[BlueprintInstance] = []
        self._secrets = {}

    def cli_prepare(self, parser: ArgumentParser):
        parser.add_argument('-c',
                            dest='override_config_file',
                            default=str(self.config_file),
                            required=False,
                            help='Override the water configuration file for this invocation')
        parser.add_argument('-d',
                            dest='override_config_dir',
                            default=str(self.config_dir),
                            required=False,
                            help='Override the directory into which configuration is generated for this invocation')
        parser.add_argument('-o', '--output',
                            dest='override_output',
                            default=str(self.output_class),
                            choices=[name for name in self.outputs.keys()],
                            required=False,
                            help='Override the output style for this invocation')
        parser.add_argument('-p', '--platform',
                            dest='override_default_platform',
                            default=str(self.platform_class),
                            choices=[name for name in self.platforms.keys()],
                            required=False,
                            help='Override the default platform for this invocation')
        parser.add_argument('-s', '--secrets',
                            dest='override_secrets_file',
                            default=str(self.secrets_file),
                            required=False,
                            help='Override the secrets file for this invocation')

    def cli_assess(self, args: Namespace):
        if args.override_config_file and args.override_config_file != DEFAULT_CONFIG_FILE:
            self._config_file.value = pathlib.Path(args.override_config_file)
            self._config_file.source = Source.CLI
        self.config_load()

        if args.override_config_dir and args.override_config_dir != DEFAULT_CONFIG_DIR:
            self._config_dir.value = pathlib.Path(args.override_config_dir)
            self._config_dir.source = Source.CLI
        if args.override_output and args.override_output != DEFAULT_OUTPUT_CLASS:
            self._output_class.value = args.override_output
            self._output_class.source = Source.CLI
        if args.override_default_platform and args.override_default_platform != DEFAULT_PLATFORM_CLASS:
            self._platform_class.value = args.override_default_platform
            self._platform_class.source = Source.CLI
        if args.override_secrets_file and args.override_secrets_file != str(self.secrets_file.value):
            self._secrets_file.value = pathlib.Path(args.override_secrets_file)
            self._secrets_file.source = Source.CLI

        [self._instances.extend(platform.instance_list()) for platform in self.platforms.values()]
        self.secrets_load()

    @property
    def outputs(self) -> Dict[str, Output]:
        return self._outputs

    @property
    def platforms(self) -> Dict[str, Any]:
        return self._platforms

    @property
    def blueprints(self) -> Dict[str, Any]:
        return self._blueprints

    @property
    def instances(self) -> List[BlueprintInstance]:
        return self._instances

    @property
    def secrets(self) -> Dict[str, Any]:
        return self._secrets

    @secrets.setter
    def secrets(self, value: Dict[str, Any]):
        self._secrets = value
        self.secrets_save()

    @property
    def config_file(self) -> ConfigurableItem:
        return self._config_file

    @property
    def config_dir(self) -> ConfigurableItem:
        return self._config_dir

    @property
    def recipe_file(self) -> ConfigurableItem:
        return self._recipe_file

    @property
    def secrets_file(self) -> ConfigurableItem:
        return self._secrets_file

    @property
    def output_class(self) -> ConfigurableItem:
        return self._output_class

    @property
    def platform_class(self) -> ConfigurableItem:
        return self._platform_class

    @property
    def output(self) -> Output:
        if self.output_class.value not in self.outputs:
            raise MurkyWaterException(msg=f'Desired output class {self.output_class} is not available')
        return self.outputs[self.output_class.value]

    @property
    def platform(self) -> WaterPlatform:
        if self.platform_class.value not in self.platforms:
            raise MurkyWaterException(msg=f'Desired platform class {self.platform_class} is not available')
        return self.platforms[self.platform_class.value]

    def config_load(self):
        raw_config = WaterConfiguration.construct()
        config_file = self.config_file.value
        if config_file.exists():
            raw_config = WaterConfiguration.parse_file(config_file)
        if raw_config.config_dir:
            self.config_dir.value = pathlib.Path(raw_config.config_dir)
            self.config_dir.source = Source.CONFIGURATION
        if raw_config.default_output:
            self.output_class.value = raw_config.default_output
            self.output_class.source = Source.CONFIGURATION
        if raw_config.default_platform:
            self.platform_class.value = raw_config.default_platform
            self.platform_class.source = Source.CONFIGURATION

    def config_save(self):
        config = WaterConfiguration(config_dir=self.config_dir,
                                    default_output=self.output.name,
                                    default_platform=self.platform.name)
        with open(self.config_file.value, 'w+', encoding='UTF-8') as c:
            json.dump(config.dict(), c, indent=2)

    def secrets_load(self):
        secrets_file = self.secrets_file.value
        if secrets_file.exists():
            self._secrets = json.loads(secrets_file.read_text(encoding='UTF-8'))

    def secrets_save(self):
        self.secrets_file.value.parent.mkdir(parents=True, exist_ok=True)
        self.secrets_file.value.write_text(json.dumps(self.secrets, indent=2))

    def instance_create(self, blueprint_instance: BlueprintInstance):
        if self.instance_get(name=blueprint_instance.name,
                             blueprint=blueprint_instance.blueprint,
                             platform=blueprint_instance.platform):
            self.output.error(f'An instance called {blueprint_instance.name} already exists on this platform')
            return
        blueprint_instance.platform.instance_create(blueprint_instance)
        self._instances.append(blueprint_instance)

    def instance_remove(self, blueprint_instance: BlueprintInstance):
        blueprint_instance.platform.instance_remove(blueprint_instance)
        self._instances.remove(blueprint_instance)

    def instance_list(self,
                      blueprint: Optional[Blueprint] = None,
                      platform: Optional[WaterPlatform] = None) -> List[BlueprintInstance]:
        instances = self._instances
        if platform:
            instances = list(filter(lambda _: _.platform == platform, instances))
        if blueprint:
            instances = list(filter(lambda _: _.blueprint == blueprint, instances))
        return instances

    def instance_get(self,
                     name: str,
                     blueprint: Optional[Blueprint] = None,
                     platform: Optional[WaterPlatform] = None) -> Optional[BlueprintInstance]:
        instances = list(filter(lambda _: _.name == name,
                                self.instance_list(blueprint, platform)))
        return instances[0] if len(instances) > 0 else None

    def _find_extensions(self, base):
        """
        Recursively find all subclasses
        Args:
            base: The base class whose subclasses to find

        Returns:
            A dict mapping the fully qualified class name to an instance
        """
        all_subclasses = {}
        for subclass in base.__subclasses__():
            if hasattr(subclass, 'factory'):
                all_subclasses.update(subclass.factory(self))
            else:
                all_subclasses[subclass.name] = subclass(self)
            all_subclasses.update(self._find_extensions(subclass))
        return all_subclasses
