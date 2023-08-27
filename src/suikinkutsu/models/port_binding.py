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

import re
import typing

from suikinkutsu.exceptions import UnparseableInstanceException


class PortBinding(object):
    """
    A Port Binding
    """

    def __init__(self,
                 host_port: int,
                 container_port: int,
                 host_ip: typing.Optional[str] = '0.0.0.0',
                 protocol: typing.Optional[str] = 'tcp'):
        self._host_port = host_port
        self._container_port = container_port
        self._host_ip = host_ip
        self._protocol = protocol

    @property
    def host_port(self) -> int:
        return self._host_port

    @property
    def container_port(self) -> int:
        return self._container_port

    @property
    def host_ip(self) -> str:
        return self._host_ip

    @property
    def protocol(self) -> str:
        return self._protocol

    @classmethod
    def from_mapping(cls, container: str, host: typing.List) -> 'PortBinding':
        c = re.fullmatch(r'(?P<port>\d+)(/(?P<protocol>\w+))?', container)
        if c is None:
            raise UnparseableInstanceException(code=500, msg=f'Instance port container mapping "{container}"'
                                                             f' is unparseable')
        if len(host) != 1 or 'HostIp' not in host[0] or 'HostPort' not in host[0]:
            raise UnparseableInstanceException(code=500, msg='Instance port host mapping is unparseable')
        return cls(container_port=c.group('port'),
                   host_ip=host[0].get('HostIp'),
                   host_port=host[0].get('HostPort'),
                   protocol=c.group('protocol'))

    def to_mapping(self) -> str:
        return f'{self.host_ip}:{self.container_port}:{self.host_port}/{self.protocol}'

    def __repr__(self):
        return f'PortBinding(host_port={self.host_port},container_port={self.container_port},' \
               f'host_ip={self.host_ip},protocol={self.protocol})'
