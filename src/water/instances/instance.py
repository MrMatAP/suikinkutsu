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

from typing import Optional

from water.blueprints import Blueprint
from water.platforms import Platform


class Instance:

    def __init__(self,
                 id: str,
                 name: str,
                 platform: Platform,
                 running: bool,
                 blueprint: str = None):
        self._id = id
        self._name = name
        self._platform = platform
        self._running = running
        self.blueprint = blueprint

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def platform(self):
        return self._platform

    @property
    def running(self):
        return self._running

    @running.setter
    def running(self, value: bool):
        self._running = value

    @property
    def blueprint(self):
        return self._blueprint

    @blueprint.setter
    def blueprint(self, value: str):
        self._blueprint = value
