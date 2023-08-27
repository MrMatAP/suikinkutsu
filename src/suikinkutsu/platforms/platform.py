
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

import typing
import abc
import pathlib
import subprocess
import argparse

from suikinkutsu.config import Configuration
from suikinkutsu.blueprints import Blueprint, BlueprintInstance
from suikinkutsu.outputs import OutputEntry
from suikinkutsu.behaviours import CommandLineAware, CommandExecutor


class Platform(CommandLineAware, CommandExecutor):
    """
    A platform to host blueprints on
    """

    def __init__(self, config: Configuration):
        self._config = config

        self._description: str = 'Abstract base for a platform'
        self._executable_name: str = None
        self._executable_path: pathlib.Path = None
        self._executable = None
        self._available = False
        self._platforms = None
        self._platform = None
        self._instances = None

    @classmethod
    def factory(cls, config: Configuration) -> typing.Dict[str, 'Platform']:
        """
        Some platforms will use the same executable to connect to multiple platform instances (e.g. kubectl).
        Using a factory method permits returning multiple class instances, one per platform instance
        Args:
            config: The configuration

        Returns:
            A list of class instances
        """
        self = cls(config)
        return {self.name: self} if self.available else {}

    def cli_prepare(self, parser, subparsers) -> None:
        platform_parser = subparsers.add_parser(name='platform', help='Platform Commands')
        platform_subparser = platform_parser.add_subparsers()
        platform_list_parser = platform_subparser.add_parser('list', help='List platforms')
        platform_list_parser.set_defaults(cmd=self.platform_list)

        platform_instances_parser = platform_subparser.add_parser('instances', help='List instances')
        platform_instances_parser.set_defaults(cmd=self.platform_instances)

    # pylint: disable=unused-argument
    def platform_list(self, runtime, args: argparse.Namespace) -> int:
        output = OutputEntry(title='Platforms',
                             columns=['Name', 'Description', 'Available'],
                             msg=[
                                 [pf.name, pf.description, str(pf.available)] for name, pf in runtime.platforms.items()]
                             )
        runtime.output.print(output)
        return 0

    # pylint: disable=unused-argument
    def platform_instances(self, runtime, args: argparse.Namespace) -> int:
        self.instances()
        return 0

    def instances(self):
        if self._platforms is None:
            return {}
        if self._instances is None:
            self._instances = {}
            for pf in self._platforms.values():
                self._instances.update(pf.instances())
        return self._instances

    @abc.abstractmethod
    def apply(self, blueprint: Blueprint):
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    @abc.abstractmethod
    def available(self):
        """
        Determine whether the platform is available. This ideally occurs with some caching and is done only once.
        Returns:
            True if the platform is available to schedule instances on, False otherwise
        """
        return self._available

    @abc.abstractmethod
    def instance_create(self, instance: BlueprintInstance):
        pass

    def execute(self, args: typing.List[str]) -> subprocess.CompletedProcess:
        return self._execute(self._executable, args)


    # @abc.abstractmethod
    # def instance_create(self, blueprint_instance: BlueprintInstance):
    #     pass
    #
    # @abc.abstractmethod
    # def instance_list(self, blueprint: typing.Optional[Blueprint] = None) -> typing.List[BlueprintInstance]:
    #     pass
    #
    # @abc.abstractmethod
    # def instance_show(self, name: str, blueprint: typing.Optional[Blueprint] = None):
    #     pass
    #
    # @abc.abstractmethod
    # def instance_remove(self, blueprint_instance: BlueprintInstance):
    #     pass


