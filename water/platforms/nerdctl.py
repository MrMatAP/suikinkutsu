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

from typing import Optional

from water import MurkyWaterException
from .platform import Platform


class Nerdctl(Platform):

    name: str = 'nerdctl'
    description: str = 'nerdctl is a modern CLI for a containerd implementation, brought to you ' \
                       'via Rancher Desktop (for example).'
    executable_name = 'nerdctl'

    def __init__(self):
        super().__init__()
        try:
            self._execute(['ps', '-q'])
        except MurkyWaterException:
            self._available = False

    def volume_create(self, name: str):
        pass

    def volume_list(self):
        pass

    def volume_remove(self, name: str):
        pass

    def service_create(self, blueprint):
        pass

    def service_list(self, name: Optional[str] = None):
        pass

    def service_show(self, blueprint):
        pass

    def service_remove(self, blueprint):
        pass
