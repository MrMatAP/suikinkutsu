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

import argparse

from suikinkutsu.models import VolumeBinding, PortBinding
from .blueprint import Blueprint, BlueprintInstance


class KafkaStore(Blueprint):
    """
    Kafka store blueprint
    """

    name = 'kafkastore'

    def __init__(self):
        super().__init__()
        self._description = 'Schema Registry Store for Apache Kafka'
        self._image = 'confluentinc/cp-schema-registry'
        self._version = '7.3.1'
        self._volume_bindings = [
            VolumeBinding(name='kafkastore_etcvol', mount_point='/etc/schema-registry/secrets')
        ]
        self._environment = {
            'SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS': 'kafka:9092',
            'SCHEMA_REGISTRY_KAFKASTORE_LISTENERS': 'http://0.0.0.0:8081',
            'SCHEMA_REGISTRY_HOST_NAME': 'kafkastore'
        }
        self._port_bindings = [
            PortBinding(host_port=8081, container_port=8081, host_ip='127.0.0.1', protocol='tcp')
        ]
        self._depends_on = ['kafka']

    def cli_prepare(self, parser, subparsers):
        kafkastore_parser = subparsers.add_parser(name='kafkastore', help='KafkaStore Commands')
        kafkastore_subparser = kafkastore_parser.add_subparsers()
        kafkastore_create_parser = kafkastore_subparser.add_parser(name='create', help='Create a KafkaStore instance')
        kafkastore_create_parser.add_argument('-n', '--instance-name',
                                              dest='name',
                                              default='kafkastore',
                                              required=False,
                                              help='Instance name')
        kafkastore_create_parser.set_defaults(cmd=self.kafkastore_create)

        kafkastore_remove_parser = kafkastore_subparser.add_parser(name='remove', help='Remove a KafkaStore instance')
        kafkastore_remove_parser.add_argument('-n', '--instance-name',
                                              dest='name',
                                              required=True,
                                              help='Instance name')
        kafkastore_remove_parser.set_defaults(cmd=self.kafkastore_remove)

    def kafkastore_create(self, runtime: 'Runtime', args: argparse.Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=self.runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secreta
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:8081'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:8081'
        self.runtime.secreta = runtime_secrets

    def kafkastore_remove(self, runtime: 'Runtime', args: argparse.Namespace) -> int:
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
