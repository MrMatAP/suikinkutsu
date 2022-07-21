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
import secrets

from water.schema import BlueprintSchema
from water.blueprints.blueprint import Blueprint
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Keycloak(Blueprint):

    kind: str = 'keycloak'
    description: str = 'Keycloak is an Identity Provider implementing OAuth 2 and SAML authentication/authorisation'
    _defaults: BlueprintSchema = BlueprintSchema(
        kind='keycloak',
        name='kc',
        image='jboss/keycloak:16.1.1',
        volumes={'import': '/import'},
        environment={
            # 'DB_VENDOR': 'postgres',
            # 'DB_ADDR': 'pg',
            # 'DB_DATABASE': 'localdb',
            # 'DB_USER': 'keycloak',
            # 'DB_PASSWORD': 'keycloak',
            # 'DB_SCHEMA': 'keycloak',
            'KEYCLOAK_USER': 'admin',
            'KEYCLOAK_PASSWORD': secrets.token_urlsafe(16)
        },
        ports={'127.0.0.1:8080': '8080'},
        labels={
            LABEL_BLUEPRINT: 'keycloak',
            LABEL_CREATED_BY: 'water'
        },
        depends_on=[]
    )

    @classmethod
    def cli_prepare(cls, parser):
        kc_parser = parser.add_parser(name='kc', help='Keycloak Commands')
        kc_subparser = kc_parser.add_subparsers()
        kc_create_parser = kc_subparser.add_parser(name='create', help='Create a Keycloak instance')
        kc_create_parser.set_defaults(cmd=cls.kc_create)
        kc_create_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=cls._defaults.name,
                                      required=False,
                                      help='Instance name')
        kc_list_parser = kc_subparser.add_parser(name='list', help='List all keycloak instances')
        kc_list_parser.set_defaults(cmd=cls.kc_list)
        kc_remove_parser = kc_subparser.add_parser(name='remove', help='Remove Keycloak instances')
        kc_remove_parser.set_defaults(cmd=cls.kc_remove)
        kc_remove_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=cls.name,
                                      required=False,
                                      help='Instance name')

    @classmethod
    def cli_assess(cls, args: Namespace):
        super().cli_assess(args)

    @classmethod
    def kc_create(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_create(instance)

    @classmethod
    def kc_list(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_list(instance)

    @classmethod
    def kc_remove(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_remove(instance)
