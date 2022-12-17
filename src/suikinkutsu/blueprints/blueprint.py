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
import abc
import argparse
from collections import OrderedDict
from typing import Optional, List

from suikinkutsu.config import Configuration
from suikinkutsu.outputs import OutputEntry
from suikinkutsu.schema import BlueprintSchema
from suikinkutsu.constants import LABEL_BLUEPRINT


class Blueprint:

    _defaults: BlueprintSchema = BlueprintSchema(
        image='',
        volumes={},
        environment={},
        ports={},
        labels={LABEL_BLUEPRINT: 'Blueprint'},
        depends_on=[]
    )

    def __init__(self, config: Configuration):
        self._config = config

        self._name = 'base'
        self._description = 'An abstract base blueprint'

    def cli_prepare(self, parser, subparsers) -> None:
        """
        Hook to declare CLI arguments
        Args:
            parser: The ArgumentParser to attach top-level CLI arguments to
            subparsers: The subparser to attach subcommands to
        """
        blueprint_parser = subparsers.add_parser(name='blueprint', help='Blueprint commands')
        blueprint_subparsers = blueprint_parser.add_subparsers()
        blueprint_list_parser = blueprint_subparsers.add_parser('list', help='List available blueprints')
        blueprint_list_parser.set_defaults(cmd=self.blueprint_list)

    def cli_assess(self, args: argparse.Namespace) -> None:
        """
        Hook to parse CLI arguments
        Args:
            args: The namespace containing the parsed CLI arguments
        """
        pass

    def blueprint_list(self, runtime, args: argparse.Namespace) -> int:
        output = OutputEntry(title='Blueprints',
                             columns=['Name', 'Description'],
                             msg=[[bp.name, bp.description] for bp in self.blueprints()])
        runtime.output.print(output)
        return 0

    def blueprints(self):
        return [bp(self._config) for bp in Blueprint.__subclasses__()]

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def image(self):
        return self._schema.image

    @property
    def labels(self):
        return self._schema.labels

    @property
    def volumes(self):
        return self._schema.volumes

    @property
    def environment(self):
        return self._schema.environment

    @property
    def ports(self):
        return self._schema.ports

    @property
    def depends_on(self):
        return self._schema.depends_on


class BlueprintVolume:

    def __init__(self, name: str, destination: str):
        self._name = name
        self._destination = destination

    @property
    def name(self):
        return self._name

    @property
    def destination(self):
        return self._destination


class BlueprintInstance():

    def __init__(self,
                 name: str,
                 platform: 'Platform',
                 volumes: Optional[List[BlueprintVolume]] = None,
                 blueprint: Optional[Blueprint] = None):
        self._id = None
        self._name = name
        self._platform = platform
        self._running = False
        self._volumes = volumes or []
        self._blueprint = blueprint

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def name(self):
        return self._name

    @property
    def platform(self) -> 'Platform':
        return self._platform

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool):
        self._running = value

    @property
    def volumes(self) -> List[BlueprintVolume]:
        return self._volumes

    @property
    def blueprint(self) -> Blueprint:
        return self._blueprint

    @blueprint.setter
    def blueprint(self, value: Blueprint):
        self._blueprint = value

    def display_dict(self) -> OrderedDict:
        return OrderedDict({
            'id': self.id,
            'name': self.name,
            'platform': self.platform.name if self.platform else 'Unknown',
            'blueprint': self.blueprint.name if self.blueprint else 'Unknown',
            'running': self.running
        })


class BlueprintInstanceList(list):

    def __init__(self, blueprint_instances: List[Blueprint] = None):
        super().__init__()
        self._blueprint_instances = blueprint_instances or []

    def display_dict(self) -> OrderedDict:
        instances = OrderedDict({
            'id': [],
            'name': [],
            'platform': [],
            'blueprint': [],
            'running': []
        })
        for blueprint_instance in self:
            instances['id'].append(blueprint_instance.id)
            instances['name'].append(blueprint_instance.name)
            instances['platform'].append(blueprint_instance.platform.name if blueprint_instance.platform else 'Unknown')
            instances['blueprint'].append(
                blueprint_instance.blueprint.name if blueprint_instance.blueprint else 'Unknown')
            instances['running'].append(blueprint_instance.running)
        return instances
