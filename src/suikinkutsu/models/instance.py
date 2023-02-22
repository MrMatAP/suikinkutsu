#  MIT License
#
#  Copyright (c) 2023 Mathieu Imfeld
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

from suikinkutsu.blueprints import Blueprint
from suikinkutsu.models import PortBinding, VolumeBinding


class Instance(object):
    """
    A blueprint instance
    """

    def __init__(self, instance_id: str, name: str, running: bool):
        self._id = instance_id
        self._name = name
        self._running = running
        self._blueprint = None
        self._port_bindings = []
        self._volume_bindings = []

    @property
    def instance_id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool):
        self._running = value

    @property
    def blueprint(self) -> Blueprint:
        return self._blueprint

    @blueprint.setter
    def blueprint(self, value: Blueprint):
        self._blueprint = value

    @property
    def port_bindings(self) -> typing.List[PortBinding]:
        return self._port_bindings

    @port_bindings.setter
    def port_bindings(self, value: typing.List[PortBinding]):
        self._port_bindings = value

    @property
    def volume_bindings(self) -> typing.List[VolumeBinding]:
        return self._volume_bindings

    @volume_bindings.setter
    def volume_bindings(self, value: typing.List[VolumeBinding]):
        self._volume_bindings = value
