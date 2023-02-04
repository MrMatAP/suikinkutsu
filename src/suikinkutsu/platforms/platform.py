
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

from suikinkutsu import MurkyWaterException
from suikinkutsu.config import Configuration
from suikinkutsu.blueprints import Blueprint
from suikinkutsu.outputs import OutputEntry


class Platform:
    """
    A platform to host blueprints on
    """

    def __init__(self, config: Configuration):
        self._config = config

        self._name: str = 'base'
        self._description: str = 'Abstract base for a platform'
        self._executable_name: str = None
        self._executable_path: pathlib.Path = None
        self._executable = None
        self._available = False
        self._platforms = None
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
        """
        Hook to declare CLI arguments
        Args:
            parser: The ArgumentParser to attach top-level CLI arguments to
            subparsers: The subparser to attached subcommands to
        """
        platform_parser = subparsers.add_parser(name='platform', help='Platform Commands')
        platform_subparser = platform_parser.add_subparsers()
        platform_list_parser = platform_subparser.add_parser('list', help='List platforms')
        platform_list_parser.set_defaults(cmd=self.platform_list)

        platform_instances_parser = platform_subparser.add_parser('instances', help='List instances')
        platform_instances_parser.set_defaults(cmd=self.platform_instances)

    def cli_assess(self, args: argparse.Namespace) -> None:
        """
        Hook to parse CLI arguments
        Args:
            args: The namespace containing the parsed CLI arguments
        """
        pass

    def platform_list(self, runtime, args: argparse.Namespace) -> int:
        output = OutputEntry(title='Platforms',
                             columns=['Name', 'Description', 'Available'],
                             msg=[[name, pf.description, str(pf.available)] for name, pf in self.platforms().items()])
        runtime.output.print(output)
        return 0

    def platform_instances(self, runtime, args: argparse.Namespace) -> int:
        self.platforms()
        self.instances()
        return 0

    def platforms(self) -> typing.Dict[str, 'Platform']:
        if self._platforms is None:
            self._platforms = {}
            for pf in Platform.__subclasses__():
                self._platforms.update(pf.factory(self._config))
        return self._platforms

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

    def execute(self, args: typing.List[str]) -> subprocess.CompletedProcess:
        """
        Execute the platform command with the provided parameters
        Args:
            args: Parameters to the executable

        Returns:
            The completed process output from the subprocess module

        Raises:
            MurkyWaterException when the platform is not unavailable, the platform executable cannot be found or
            the executable did not return with a successful exit code
        """
        if not self._available and self._available is not None:
            raise MurkyWaterException(msg='Platform is not available')
        if not self.executable:
            raise MurkyWaterException(msg=f'Unable to find {self.executable_name} on your path')
        try:
            args.insert(0, str(self.executable))
            return subprocess.run(args=args,
                                  capture_output=True,
                                  check=True,
                                  encoding='UTF-8')
        except subprocess.CalledProcessError as cpe:
            raise MurkyWaterException(code=cpe.returncode, msg=cpe.output) from cpe
