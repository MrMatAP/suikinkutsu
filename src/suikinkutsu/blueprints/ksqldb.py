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
from suikinkutsu.schema import BlueprintSchema
from suikinkutsu.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from .blueprint import Blueprint, BlueprintInstance


class KSQLDB(Blueprint):
    """
    Kafka blueprint
    """
    _defaults: BlueprintSchema = BlueprintSchema(
        image='confluentinc/ksqldb-server:0.27.2',
        volumes={},
        environment={
            'KSQL_LISTENERS': 'http://0.0.0.0:8088',
            'KSQL_BOOTSTRAP_SERVERS': 'kafka:9092',
            'KSQL_KSQL_LOGGING_PROCESSING_STREAM_AUTO_CREATE': 'true',
            'KSQL_KSQL_LOGGING_PROCESSING_TOPIC_AUTO_CREATE': 'true'
        },
        ports={'8088': '8088'},
        labels={
            LABEL_BLUEPRINT: 'ksqldb',
            LABEL_CREATED_BY: 'suikinkutsu'
        },
        depends_on=['kafka']
    )

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._config = config
        self._name = 'ksqldb'
        self._description = 'KSQLDB on top of Kafka'

    def cli_prepare(self, parser, subparsers):
        ksqldb_parser = subparsers.add_parser(name='ksqldb', help='KSQLDB Commands')
        ksqldb_subparser = ksqldb_parser.add_subparsers()
        ksqldb_create_parser = ksqldb_subparser.add_parser(name='create', help='Create a KSQLDB instance')
        ksqldb_create_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          default='ksqldb',
                                          required=False,
                                          help='Instance name')
        ksqldb_create_parser.set_defaults(cmd=self.ksqldb_create)

        ksqldb_remove_parser = ksqldb_subparser.add_parser(name='remove', help='Remove a KSQLDB instance')
        ksqldb_remove_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          required=True,
                                          help='Instance name')
        ksqldb_remove_parser.set_defaults(cmd=self.ksqldb_remove)

    def ksqldb_create(self, runtime, args: argparse.Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=self.runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secrets
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:8088'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:8088'
        self.runtime.secrets = runtime_secrets

    def ksqldb_remove(self, runtime, args: argparse.Namespace):
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
