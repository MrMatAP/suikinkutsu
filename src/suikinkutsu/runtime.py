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

import typing
import argparse

from suikinkutsu.outputs import Output
from suikinkutsu.blueprints import Blueprint, BlueprintInstance
from suikinkutsu.platforms import Platform
from suikinkutsu.config import Configuration
from suikinkutsu.secreta import Secreta


class Runtime:
    """
    The runtime object holds all configured actor implementations together
    """

    def __init__(self, config: Configuration, secreta: Secreta):
        self._config = config
        self._secreta = secreta

        self._outputs = {}
        for output in Output.__subclasses__():
            self._outputs[output.name] = output(self._config)
        self._output = None

        self._platforms = {}
        for platform in Platform.__subclasses__():
            self._platforms.update(platform.factory(self._config))
        self._platform = None

        self._blueprints = {}
        for blueprint in Blueprint.__subclasses__():
            self._blueprints[blueprint.name] = blueprint(self._config)

        self._instances = {}


        # #self._platforms = self._find_extensions(WaterPlatform)
        # self._platforms = {}
        # self._blueprints = self._find_extensions(Blueprint)
        # #self._blueprints = {}
        # self._instances: List[BlueprintInstance] = []
        # self._secrets = {}

    def cli_prepare(self, parser, subparsers):
        pass

    def cli_assess(self, args: argparse.Namespace):
        if self._config.output.value not in self._outputs:
            print(f'ERROR: Configured output {self._config.output.value} is not available')
            return 1
        self._output = self._outputs.get(self._config.output.value)

        if self._config.platform.value not in self._platforms:
            self._output.error(f'Configured platform {self._config.platform.value} is not available')
            return 1
        self._platform = self._platforms.get(self._config.platform.value)

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def secreta(self) -> Secreta:
        return self._secreta

    @property
    def outputs(self) -> typing.Dict[str, Output]:
        return self._outputs

    @property
    def output(self) -> Output:
        return self._output

    @property
    def platforms(self) -> typing.Dict[str, Platform]:
        return self._platforms

    @property
    def platform(self) -> Platform:
        return self._platform

    @property
    def blueprints(self) -> typing.Dict[str, Blueprint]:
        return self._blueprints

    # def config_save(self):
    #     config = WaterConfiguration(config_dir=self.config_dir,
    #                                 default_output=self.output.name,
    #                                 default_platform=self.platform.name)
    #     with open(self.config_file.value, 'w+', encoding='UTF-8') as c:
    #         json.dump(config.dict(), c, indent=2)


    def instance_remove(self, blueprint_instance: BlueprintInstance):
        blueprint_instance.platform.instance_remove(blueprint_instance)
        self._instances.remove(blueprint_instance)

    def instance_list(self,
                      blueprint: typing.Optional[Blueprint] = None,
                      platform: typing.Optional[Platform] = None) -> typing.List[BlueprintInstance]:
        instances = self._instances
        if platform:
            instances = list(filter(lambda _: _.platform == platform, instances))
        if blueprint:
            instances = list(filter(lambda _: _.blueprint == blueprint, instances))
        return instances

    def instance_get(self,
                     name: str,
                     blueprint: typing.Optional[Blueprint] = None,
                     platform: typing.Optional[Platform] = None) -> typing.Optional[BlueprintInstance]:
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
