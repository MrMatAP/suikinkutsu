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

from argparse import Namespace
import secrets

from water.schema import BlueprintSchema
from water.exceptions import MurkyWaterException
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from .blueprint import Blueprint


class Kafka(Blueprint):
    name: str = 'kafka'
    description: str = 'Kafka'
    _defaults: BlueprintSchema = BlueprintSchema(
        image='confluentinc/cp-kafka:7.2.1',
        volumes={},
        environment={
            'KAFKA_ZOOKEEPER_CONNECT': 'zookeeper:32181',
            'KAFKA_ADVERTISED_LISTENERS': 'PLAINTEXT://localhost:29092',
            'KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR': 1
        },
        ports={'29092': '29092'},
        labels={
            LABEL_BLUEPRINT: 'kafka',
            LABEL_CREATED_BY: 'water'
        },
        depends_on=['zookeeper']
    )

    def cli_prepare(self, parser):
        kafka_parser = parser.add_parser(name='kafka', help='Kafka Commands')
        kafka_subparser = kafka_parser.add_subparsers()
        kafka_create_parser = kafka_subparser.add_parser(name='create', help='Create a Kafka instance')
        kafka_create_parser.set_defaults(cmd=self.kafka_create)
        kafka_create_parser.add_argument('-n', '--instance-name',
                                         dest='name',
                                         default='kafka',
                                         required=False,
                                         help='Instance name')
        kafka_list_parser = kafka_subparser.add_parser(name='list', help='List Kafka instances')
        kafka_list_parser.set_defaults(cmd=self.kafka_list)
        kafka_remove_parser = kafka_subparser.add_parser(name='remove', help='Remove Kafka instances')
        kafka_remove_parser.set_defaults(cmd=self.kafka_remove)
        kafka_remove_parser.add_argument('-n', '--instance-name',
                                         dest='name',
                                         required=True,
                                         help='Instance name')

    def cli_assess(self, args: Namespace):
        super().cli_assess(args)

    def kafka_create(self, runtime, args: Namespace):
        runtime.platform.service_create(self)

    def kafka_list(self, runtime, args: Namespace):
        runtime.platform.service_list(self.name)

    def kafka_remove(self, runtime, args: Namespace):
        runtime.platform.service_remove(self)
