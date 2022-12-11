
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

from typing import List, Dict, Optional
import abc
import pathlib
import subprocess
from argparse import Namespace

from suikinkutsu import MurkyWaterException, WaterExtension
from suikinkutsu.blueprints import Blueprint, BlueprintInstance


class WaterPlatform(WaterExtension):

    def __init__(self, runtime: 'Runtime'):
        super().__init__(runtime)
        self._name: str = 'base'
        self._description: str = 'Abstract base for a platform'
        self._executable_name: str = None
        self._executable_path: pathlib.Path = None
        self._executable = None
        self._available = False

    @classmethod
    def factory(cls, runtime: 'Runtime') -> Dict[str, 'WaterPlatform']:
        """
        Some platforms will use the same executable to connect to multiple platform instances (e.g. kubectl).
        Using a factory method permits returning multiple class instances, one per platform instance
        Args:
            runtime: The runtime instance we are associated with

        Returns:
            A list of class instances
        """
        self = cls(runtime)
        return {self.name: self}

    @property
    def runtime(self) -> 'Runtime':
        return self._runtime

    @property
    def executable_name(self) -> str:
        return self._executable_name

    @property
    def executable(self):
        return self._executable

    @property
    def available(self):
        """
        Determine whether the platform is available. This ideally occurs with some caching and is done only once.
        Returns:
            True if the platform is available to schedule instances on, False otherwise
        """
        return self._available

    def cli_prepare(self, parser) -> None:
        """
        Hook to declare CLI arguments
        Args:
            parser: The ArgumentParser to attach CLI arguments to
        """
        pass

    def cli_assess(self, args: Namespace) -> None:
        """
        Hook to parse CLI arguments
        Args:
            args: The namespace containing the parsed CLI arguments
        """
        pass

    @abc.abstractmethod
    def instance_create(self, blueprint_instance: BlueprintInstance):
        pass

    @abc.abstractmethod
    def instance_list(self, blueprint: Optional[Blueprint] = None) -> List[BlueprintInstance]:
        pass

    @abc.abstractmethod
    def instance_show(self, name: str, blueprint: Optional[Blueprint] = None):
        pass

    @abc.abstractmethod
    def instance_remove(self, blueprint_instance: BlueprintInstance):
        pass

    def execute(self, args: List[str]) -> subprocess.CompletedProcess:
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
