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
import configparser

from platforms import Platform
from water.blueprints import Blueprint


class PostgreSQL(Blueprint):

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

    @staticmethod
    def parser(subparsers):
        pg_parser = subparsers.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=PostgreSQL.create)
        pg_create_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=PostgreSQL.name,
                                      required=False,
                                      help='Instance name')
        pg_list_parser = pg_subparser.add_parser(name='list', help='List PostgreSQL instances')
        pg_list_parser.set_defaults(cmd=PostgreSQL.list)
        pg_remove_parser = pg_subparser.add_parser(name='remove', help='Remove PostgreSQL instances')
        pg_remove_parser.set_defaults(cmd=PostgreSQL.remove)
        pg_remove_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=PostgreSQL.name,
                                      required=False,
                                      help='Instance name')

    @staticmethod
    def create(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace):
        instance = PostgreSQL(name=args.name)
        platform.instance_create(blueprint=instance)
        return 0

    @staticmethod
    def list(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace):
        platform.volume_list()

    @staticmethod
    def remove(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace):
        instance = PostgreSQL(name=args.name)
        platform.volume_remove(instance.name)
        return 0
