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

from suikinkutsu.config import Configuration
from suikinkutsu.schema import BlueprintSchema
from suikinkutsu.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from suikinkutsu.blueprints.blueprint import Blueprint, BlueprintInstance


class Jaeger(Blueprint):
    """
    Jaeger blueprint
    """
    _defaults: BlueprintSchema = BlueprintSchema(
        image='jaegertracing/all-in-one:1.35',
        volumes={
            'jaeger_tmpvol': '/tmp'
        },
        environment={
            'COLLECTOR_ZIPKIN_HOST_PORT': ':9411',
            'COLLECTOR_OLTP_ENABLED': 'true'
        },
        ports={
            '6831': '6831/udp',
            '6832': '8632/udp',
            '5778': '5778',
            '16686': '16686',
            '4317': '4317',
            '4318': '4318',
            '14250': '14250',
            '14268': '14268',
            '14269': '14269',
            '9411': '9411'
        },
        labels={
            LABEL_BLUEPRINT: 'jaeger',
            LABEL_CREATED_BY: 'suikinkutsu'
        },
        depends_on=[]
    )

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._config = config
        self._name = 'jaeger'
        self._description = 'Jaeger Tracing'

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

    def jaeger_create(self, runtime, args: argparse.Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secrets
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'{args.name}:16686'
            }
        else:
            runtime_secrets[args.name]['connection'] = f'{args.name}:16686'
        self.runtime.secrets = runtime_secrets

    def jaeger_remove(self, runtime, args: argparse.Namespace):
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
