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

import json
from typing import List, Dict, Optional, Any
from argparse import ArgumentParser, Namespace

from suikinkutsu.exceptions import MurkyWaterException
from suikinkutsu.outputs import Output, HumanWaterOutput
from suikinkutsu.blueprints import Blueprint, BlueprintInstance
from suikinkutsu.platforms import Platform
from suikinkutsu.config import Configuration


class Runtime:
    """
    The runtime of all platforms, blueprints and their instances
    """

    def __init__(self, config: Configuration):
        self._config = config

        self._outputs: Dict[str, Output] = self._find_extensions(Output)
        self._output = HumanWaterOutput()

        #self._platforms = self._find_extensions(WaterPlatform)
        self._platforms = {}
        self._blueprints = self._find_extensions(Blueprint)
        #self._blueprints = {}
        self._instances: List[BlueprintInstance] = []
        self._secrets = {}

    def cli_prepare(self, parser: ArgumentParser):
        pass

    def cli_assess(self, args: Namespace):
        self._output = self._outputs.get(self.config.output.value)
        #[self._instances.extend(platform.instance_list()) for platform in self.platforms.values()]
        #self.secrets_load()

    # def config_save(self):
    #     config = WaterConfiguration(config_dir=self.config_dir,
    #                                 default_output=self.output.name,
    #                                 default_platform=self.platform.name)
    #     with open(self.config_file.value, 'w+', encoding='UTF-8') as c:
    #         json.dump(config.dict(), c, indent=2)

    def secrets_load(self):
        secrets_file = self.config.secrets_file.value
        if secrets_file.exists():
            self._secrets = json.loads(secrets_file.read_text(encoding='UTF-8'))

    def secrets_save(self):
        self.config.secrets_file.value.parent.mkdir(parents=True, exist_ok=True)
        self.config.secrets_file.value.write_text(json.dumps(self.secrets, indent=2))

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
                      platform: Optional[Platform] = None) -> List[BlueprintInstance]:
        instances = self._instances
        if platform:
            instances = list(filter(lambda _: _.platform == platform, instances))
        if blueprint:
            instances = list(filter(lambda _: _.blueprint == blueprint, instances))
        return instances

    def instance_get(self,
                     name: str,
                     blueprint: Optional[Blueprint] = None,
                     platform: Optional[Platform] = None) -> Optional[BlueprintInstance]:
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

    @property
    def config(self) -> Configuration:
        return self._config

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        if value not in self.outputs:
            raise MurkyWaterException(f'The desired output {value} is not available')
        self._output = self._outputs.get(self.config.output.value)

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
