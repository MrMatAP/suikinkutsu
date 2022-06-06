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

from typing import List, Optional
import abc
import subprocess
import argparse
from rich.table import Table
from rich.box import ROUNDED
from water import MurkyWaterException, console


class Platform(abc.ABC):
    name: str
    executable_name: str = None
    executable: str = None

    def __init__(self, runtime):
        if self.available():
            runtime.available_platforms.append(self)

    def available(self) -> bool:
        return False

    def cli(self, parser):
        pass

    @abc.abstractmethod
    def volume_create(self, name: str):
        pass

    @abc.abstractmethod
    def volume_list(self):
        pass

    @abc.abstractmethod
    def volume_remove(self, name: str):
        pass

    @abc.abstractmethod
    def service_create(self, blueprint):
        pass

    @abc.abstractmethod
    def service_list(self, name: Optional[str]):
        pass

    @abc.abstractmethod
    def service_show(self, blueprint):
        pass

    @abc.abstractmethod
    def service_remove(self, blueprint):
        pass

    @classmethod
    def platform_list(cls, runtime, args: argparse.Namespace):
        table = Table(title='Available Platforms', box=ROUNDED)
        table.add_column('Platform')
        table.add_column('Description')
        [table.add_row(rt.name, rt.description) for rt in runtime.available_platforms]
        console.print(table)

    def _execute(self, args: List[str]) -> subprocess.CompletedProcess:
        if not self.executable:
            raise MurkyWaterException(msg=f'Unable to find {self.executable_name} on your path')
        try:
            args.insert(0, self.executable)
            return subprocess.run(args=args,
                                  capture_output=True,
                                  check=True,
                                  encoding='UTF-8')
        except subprocess.CalledProcessError as cpe:
            raise MurkyWaterException(code=cpe.returncode, msg=cpe.output)
