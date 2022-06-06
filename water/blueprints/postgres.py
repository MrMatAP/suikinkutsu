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
import secrets

from water import console
from water.blueprints.blueprint import Blueprint, BlueprintSchema


class PostgreSQL(Blueprint):

    name: str = 'postgres'
    kind: str = 'postgres'
    description: str = 'PostgreSQL is a modern relational database'

    image: str = 'postgres:14.3-alpine'
    volumes: Dict[str, str] = {
        'pg_datavol': '/var/lib/postgresql/data',
    }
    environment: Dict[str, str] = {
        'POSTGRES_DB': 'localdb',
        'POSTGRES_PASSWORD': secrets.token_urlsafe(16),
        'PGDATA': '/var/lib/postgresql/data/pgdata'
    }
    ports: Dict[str, str] = {'127.0.0.1:5432': '5432'}

    @classmethod
    def cli(cls, parser):
        pg_parser = parser.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=cls.pg_create)
        pg_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default=cls.name,
                                      required=False,
                                      help='Instance name')
        pg_list_parser = pg_subparser.add_parser(name='list', help='List PostgreSQL instances')
        pg_list_parser.set_defaults(cmd=cls.pg_list)
        pg_remove_parser = pg_subparser.add_parser(name='remove', help='Remove PostgreSQL instances')
        pg_remove_parser.set_defaults(cmd=cls.pg_remove)
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
        pg_account_add_parser.set_defaults(cmd=cls.pg_account_add)

    @classmethod
    def pg_account_add(cls, runtime, args):
        pass

    @classmethod
    def pg_create(cls, runtime, args: argparse.Namespace):
        instance = cls()
        instance.name = args.name
        instance.create(runtime, args)

    @classmethod
    def pg_list(cls, runtime, args: argparse.Namespace):
        instance = cls()
        instance.name = args.name
        instance.list(runtime, args)

    @classmethod
    def pg_remove(cls, runtime, args: argparse.Namespace):
        instance = cls()
        instance.name = args.name
        instance.remove(runtime, args)

