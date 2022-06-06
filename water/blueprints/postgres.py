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
from typing import Dict, List
import configparser

from water.blueprints.blueprint import Blueprint


class PostgreSQL(Blueprint):

    blueprint: 'water.models.Blueprint'
    defaults: 'water.models.Blueprint'

    name: str = 'pg'
    container: str = 'postgres:14.3-alpine'
    volumes: Dict[str, str] = {
        'pgdata': '/var/lib/postgresql/data/pgdata'
    }
    environment: Dict[str, str] = {
        'POSTGRES_DB': 'localdb',
        'POSTGRES_PASSWORD': 'foobar',
        'PGDATA': '/var/lib/postgresql/data/pgdata'
        #'PGDATA': '/var/lib/postgresql/local'
    }
    ports: Dict[str, str] = {
        '127.0.0.1:5432': '5432'
    }
    labels: Dict[str, str] = {
        'org.mrmat.water.blueprint': 'PostgreSQL'
    }

    @classmethod
    def parser(cls, parser):
        pg_parser = parser.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=PostgreSQL.create)
        pg_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default=PostgreSQL.name,
                                      required=False,
                                      help='Instance name')
        pg_list_parser = pg_subparser.add_parser(name='list', help='List PostgreSQL instances')
        pg_list_parser.set_defaults(cmd=PostgreSQL.list)
        pg_remove_parser = pg_subparser.add_parser(name='remove', help='Remove PostgreSQL instances')
        pg_remove_parser.set_defaults(cmd=PostgreSQL.remove)
        pg_remove_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      required=True,
                                      help='Instance name')
        pg_account_parser = pg_subparser.add_parser(name='account', help='PostgreSQL Account Commands')
        pg_account_subparser = pg_account_parser.add_subparsers()
        pg_account_add_parser = pg_account_subparser.add_parser(name='add', help='Add an account')
        pg_account_add_parser.add_argument('-n', '--instance-name',
                                           dest='name',
                                           required=True,
                                           help='Instance name')
        pg_account_add_parser.add_argument('-a', '--account-name',
                                           dest='account_name',
                                           required=True,
                                           help='Account name')
        pg_account_add_parser.set_defaults(cmd=PostgreSQL.account_add)

    @classmethod
    def account_add(cls,
               platform: 'water.platforms.Platform',
               config: configparser.ConfigParser,
               args: argparse.Namespace) -> 'water.models.service.Instance':
        pass

    @classmethod
    def create(cls,
               platform: 'water.platforms.Platform',
               config: configparser.ConfigParser,
               args: argparse.Namespace) -> 'water.models.service.Instance':
        blueprint = PostgreSQL(name=args.name)
        return platform.service_create(blueprint=blueprint)

    @classmethod
    def list(cls,
             platform: 'water.platforms.Platform',
             config: configparser.ConfigParser,
             args: argparse.Namespace) -> List['water.models.Instance']:
        pass

    @classmethod
    def remove(cls,
               platform: 'water.platforms.Platform',
               config: configparser.ConfigParser,
               args: argparse.Namespace):
        blueprint = PostgreSQL(name=args.name)
        platform.service_remove(blueprint=blueprint)
