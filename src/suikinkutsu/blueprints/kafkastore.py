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

from suikinkutsu.schema import BlueprintSchema
from suikinkutsu.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from .blueprint import Blueprint, BlueprintInstance


class KafkaStore(Blueprint):
    """
    Kafka blueprint
    """
    name: str = 'kafkastore'
    description: str = 'Schema Registry Store for Kafka'
    _defaults: BlueprintSchema = BlueprintSchema(
        image='confluentinc/cp-schema-registry:5.4.9',
        volumes={
            'kafkastore_etcvol': '/etc/schema-registry/secrets'
        },
        environment={
            'SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS': 'kafka:9092',
            'SCHEMA_REGISTRY_KAFKASTORE_LISTENERS': 'http://0.0.0.0:8081',
            'SCHEMA_REGISTRY_HOST_NAME': 'kafkastore'
        },
        ports={'8081': '8081'},
        labels={
            LABEL_BLUEPRINT: 'kafkastore',
            LABEL_CREATED_BY: 'suikinkutsu'
        },
        depends_on=['kafka']
    )

    def cli_prepare(self, parser):
        kafkastore_parser = parser.add_parser(name='kafkastore', help='KafkaStore Commands')
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

    def kafkastore_create(self, runtime, args: Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=self.runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secrets
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:8081'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:8081'
        self.runtime.secrets = runtime_secrets

    def kafkastore_remove(self, runtime, args: Namespace):
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
