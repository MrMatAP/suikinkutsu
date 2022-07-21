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

from argparse import Namespace
from water.schema import BlueprintSchema
from water.blueprints.blueprint import Blueprint
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Jaeger(Blueprint):
    kind: str = 'jaeger'
    description: str = 'Jaeger Tracing'
    _defaults: BlueprintSchema = BlueprintSchema(
        kind='jaeger',
        name='jaeger',
        image='jaegertracing/all-in-one:1.35',
        volumes={},
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
            LABEL_CREATED_BY: 'water'
        },
        depends_on=[]
    )

    @classmethod
    def cli_prepare(cls, parser):
        jaeger_parser = parser.add_parser(name='jaeger', help='Jaeger Commands')
        jaeger_subparser = jaeger_parser.add_subparsers()
        jaeger_create_parser = jaeger_subparser.add_parser(name='create', help='Create a Jaeger instance')
        jaeger_create_parser.set_defaults(cmd=cls.jaeger_create)
        jaeger_create_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          default=cls._defaults.name,
                                          required=False,
                                          help='Instance name')
        jaeger_remove_parser = jaeger_subparser.add_parser(name='remove', help='Remove a Jaeger instance')
        jaeger_remove_parser.set_defaults(cmd=cls.jaeger_remove)
        jaeger_remove_parser.add_argument('-n', '--instance-name',
                                          dest='name',
                                          required=True,
                                          help='Instance name')

    @classmethod
    def cli_assess(cls, args: Namespace):
        super().cli_assess(args)

    @classmethod
    def jaeger_create(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_create(instance)
        runtime_secrets = runtime.secrets
        if instance.name not in runtime_secrets:
            runtime_secrets[instance.name] = {}
        runtime.secrets_save()

    @classmethod
    def jaeger_remove(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_remove(instance)

