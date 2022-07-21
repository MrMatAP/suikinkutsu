
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

from typing import List, Optional
import shutil
import abc
import subprocess
import pathlib
from argparse import Namespace
from water import MurkyWaterException


class Platform(abc.ABC):

    name: str = 'base'
    executable_name: str = None
    _executable: pathlib.Path = None
    _available: bool = False

    def __init__(self):
        executable_path = shutil.which(self.executable_name)
        self._executable = pathlib.Path(executable_path) or None
        self._available = bool(self._executable)

    @classmethod
    def cli_prepare(cls, parser) -> None:
        """
        Hook to declare CLI arguments
        Args:
            parser: The ArgumentParser to attach CLI arguments to
        """
        pass

    @classmethod
    def cli_assess(cls, args: Namespace) -> None:
        """
        Hook to parse CLI arguments
        Args:
            args: The namespace containing the parsed CLI arguments
        """
        pass

    def executable(self) -> Optional[pathlib.Path]:
        return self._executable

    def available(self):
        return self._available

    @abc.abstractmethod
    def instance_list(self):
        pass

    @abc.abstractmethod
    def blueprint_create(self, blueprint):
        pass

    @abc.abstractmethod
    def blueprint_show(self, blueprint):
        pass

    @abc.abstractmethod
    def blueprint_remove(self, blueprint):
        pass

    @abc.abstractmethod
    def volume_create(self, name: str):
        pass

    @abc.abstractmethod
    def volume_list(self):
        pass

    @abc.abstractmethod
    def volume_show(self):
        pass

    @abc.abstractmethod
    def volume_remove(self, name: str):
        pass

    @abc.abstractmethod
    def service_create(self, blueprint):
        pass

    @abc.abstractmethod
    def service_list(self, name: Optional[str] = None):
        pass

    @abc.abstractmethod
    def service_show(self, blueprint):
        pass

    @abc.abstractmethod
    def service_remove(self, blueprint):
        pass

    def _execute(self, args: List[str]) -> subprocess.CompletedProcess:
        if not self.executable():
            raise MurkyWaterException(msg=f'Unable to find {self.executable_name} on your path')
        try:
            args.insert(0, str(self.executable()))
            return subprocess.run(args=args,
                                  capture_output=True,
                                  check=True,
                                  encoding='UTF-8')
        except subprocess.CalledProcessError as cpe:
            raise MurkyWaterException(code=cpe.returncode, msg=cpe.output)
