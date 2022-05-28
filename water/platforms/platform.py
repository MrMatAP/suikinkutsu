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

from typing import List
import abc
import subprocess
from water import MurkyWaterException, Volume, Instance


class Platform(abc.ABC):

    executable_name: str = None
    executable: str = None

    @abc.abstractmethod
    def volume_create(self, name: str) -> Volume:
        pass

    @abc.abstractmethod
    def volume_list(self) -> List[Volume]:
        pass

    @abc.abstractmethod
    def volume_remove(self, name: str):
        pass

    @abc.abstractmethod
    def instance_create(self, blueprint) -> Instance:
        pass

    @abc.abstractmethod
    def instance_list(self) -> List[Instance]:
        pass

    @abc.abstractmethod
    def instance_remove(self, blueprint):
        pass

    def execute(self, args: List[str]) -> subprocess.CompletedProcess:
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
