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

from suikinkutsu.config import Configuration
from suikinkutsu.models import VolumeBinding, PortBinding
from .blueprint import Blueprint, BlueprintInstance


class Kafka(Blueprint):
    """
    Kafka blueprint
    """

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._config = config
        self._name = 'kafka'
        self._description = 'Apache Kafka'
        self._image = 'confluentinc/cp-kafka'
        self._version = '7.3.1'
        self._volume_bindings = [
            VolumeBinding(name='kafka_etcvol', mount_point='/etc/kafka/secrets'),
            VolumeBinding(name='kafka_datavol', mount_point='/var/lib/kafka/data')
        ]
        self._environment = {
            'KAFKA_ZOOKEEPER_CONNECT': 'zk:32181',
            'KAFKA_LISTENER_SECURITY_PROTOCOL_MAP': 'PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT',
            'KAFKA_ADVERTISED_LISTENERS': 'PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092',
            'KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR': 1,
            'KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS': 0,
            'KAFKA_TRANSACTION_STATE_LOG_MIN_ISR': 1,
            'KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR': 1
        }
        self._port_bindings = [
            PortBinding(container_port=29092, host_ip='127.0.0.1', host_port=29092, protocol='tcp')
        ]
        self._depends_on = ['zk']

    def cli_prepare(self, parser, subparsers):
        kafka_parser = subparsers.add_parser(name='kafka', help='Kafka Commands')
        kafka_subparser = kafka_parser.add_subparsers()
        kafka_create_parser = kafka_subparser.add_parser(name='create', help='Create a Kafka instance')
        kafka_create_parser.add_argument('-n', '--instance-name',
                                         dest='name',
                                         default='kafka',
                                         required=False,
                                         help='Instance name')
        kafka_create_parser.set_defaults(cmd=self.kafka_create)

        kafka_remove_parser = kafka_subparser.add_parser(name='remove', help='Remove a Kafka instance')
        kafka_remove_parser.add_argument('-n', '--instance-name',
                                         dest='name',
                                         required=True,
                                         help='Instance name')
        kafka_remove_parser.set_defaults(cmd=self.kafka_remove)

    def kafka_create(self, runtime, args: argparse.Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=self.runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secrets
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:29092'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:29092'
        self.runtime.secrets = runtime_secrets

    def kafka_remove(self, runtime, args: argparse.Namespace):
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
