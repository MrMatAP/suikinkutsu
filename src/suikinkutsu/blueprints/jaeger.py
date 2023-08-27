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

import argparse

from suikinkutsu.models import VolumeBinding, PortBinding
from suikinkutsu.blueprints.blueprint import Blueprint, BlueprintInstance


class Jaeger(Blueprint):
    """
    Jaeger blueprint
    """

    name = 'jaeger'

    def __init__(self):
        super().__init__()
        self._description = 'Jaeger Tracing'

        self._image = 'jaegertracing/all-in-one'
        self._version = '1.41'
        self._volume_bindings = [
            VolumeBinding(name='jaeger_tmpvol', mount_point='/tmp')
        ]
        self._environment = {'COLLECTOR_ZIPKIN_HOST_PORT': ':9411', 'COLLECTOR_OLTP_ENABLED': 'true'}
        self._port_bindings = [
            PortBinding(container_port=6831, host_port=6831, host_ip='127.0.0.1', protocol='udp'),
            PortBinding(container_port=6832, host_port=6832, host_ip='127.0.0.1', protocol='udp'),
            PortBinding(container_port=5778, host_port=5778, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=16686, host_port=16686, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=4317, host_port=4317, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=4318, host_port=4318, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=14250, host_port=14250, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=14268, host_port=14268, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=14269, host_port=14269, host_ip='127.0.0.1', protocol='tcp'),
            PortBinding(container_port=9411, host_port=9411, host_ip='127.0.0.1', protocol='tcp')
        ]

    def cli_prepare(self, parser, subparsers) -> None:
        jaeger_parser = subparsers.add_parser(name='jaeger', help='Jaeger Commands')
        jaeger_subparser = jaeger_parser.add_subparsers()
        jaeger_create_parser = jaeger_subparser.add_parser(name='create', help='Create a Jaeger instance')
        jaeger_create_parser.set_defaults(cmd=self.jaeger_create)
        jaeger_create_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          default='jaeger',
                                          required=False,
                                          help='Instance name')
        jaeger_remove_parser = jaeger_subparser.add_parser(name='remove', help='Remove a Jaeger instance')
        jaeger_remove_parser.set_defaults(cmd=self.jaeger_remove)
        jaeger_remove_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          required=True,
                                          help='Instance name')

    def jaeger_create(self, runtime: 'Runtime', args: argparse.Namespace) -> int:
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secreta
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:16686'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:16686'
        self.runtime.secreta = runtime_secrets

    # pylint: disable=unused-argument
    def jaeger_remove(self, runtime: 'Runtime', args: argparse.Namespace) -> int:
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
