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
from typing import Dict

from water import console
from water.blueprints.blueprint import Blueprint


class Keycloak(Blueprint):

    name: str = 'keycloak'
    kind: str = 'keycloak'
    description: str = 'Keycloak is an Identity Provider implementing OAuth 2 and SAML authentication/authorisation'
    image: str = 'jboss/keycloak:16.1.1'
    volumes: Dict[str, str] = {
        'import': '/import'
    }
    environment: Dict[str, str] = {
        'DB_VENDOR': 'postgres',
        'DB_ADDR': 'pg',
        'DB_DATABASE': 'localdb',
        'DB_USER': 'keycloak',
        'DB_PASSWORD': 'keycloak',
        'DB_SCHEMA': 'keycloak',
        'KEYCLOAK_USER': 'admin',
        'KEYCLOAK_PASSWORD': 'foobar'
    }
    ports: Dict[str, str] = {
        '127.0.0.1:8080': '8080'
    }
    labels: Dict[str, str] = {
        'org.mrmat.water.blueprint': 'KeyCloak'
    }

    @classmethod
    def cli(cls, parser):
        kc_parser = parser.add_parser(name='keycloak', help='Keycloak Commands')
        kc_subparser = kc_parser.add_subparsers()
        kc_create_parser = kc_subparser.add_parser(name='create', help='Create a Keycloak instance')
        kc_create_parser.set_defaults(cmd=cls.kc_create)
        kc_create_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=cls.name,
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
    def kc_create(cls, runtime, args):
        instance = cls()
        instance.name = args.name
        instance.create(runtime, args)

    @classmethod
    def kc_list(cls, runtime, args):
        instance = cls()
        instance.name = args.name
        instance.list(runtime, args)

    @classmethod
    def kc_remove(cls, runtime, args):
        instance = cls()
        instance.name = args.name
        instance.remove(runtime, args)

    def create(self, runtime, args: argparse.Namespace):
        pass

    def list(self, runtime, args: argparse.Namespace):
        pass

    def remove(self, runtime, args: argparse.Namespace):
        pass
