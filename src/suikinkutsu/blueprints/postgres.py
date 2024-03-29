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
import secrets as generator
import psycopg2
from psycopg2 import sql

from suikinkutsu.models import PortBinding, VolumeBinding
from suikinkutsu.exceptions import MurkyWaterException
from .blueprint import Blueprint


class PostgreSQL(Blueprint):
    """
    PostgreSQL blueprint
    """

    name = 'pg'

    def __init__(self):
        super().__init__()
        self._description = 'PostgreSQL is a modern relational database'

        self._image = 'postgres'
        self._version = '14'
        self._volume_bindings = [
            VolumeBinding(name='pg_datavol', mount_point='/var/lib/postgresql/data')
        ]
        self._environment = {'POSTGRES_DB': 'localdb',
                             'POSTGRES_PASSWORD': generator.token_urlsafe(16),
                             'PGDATA': '/var/lib/postgresql/data/pgdata'}
        self._port_bindings = [
            PortBinding(container_port=5432, host_ip='127.0.0.1', host_port=5432, protocol='tcp')
        ]
        self._depends_on = []

    def cli_prepare(self, parser, subparsers):
        pg_parser = subparsers.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=self.pg_create)
        pg_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default='pg',
                                      required=False,
                                      help='Instance name')
        pg_remove_parser = pg_subparser.add_parser(name='remove', help='Remove PostgreSQL instances')
        pg_remove_parser.set_defaults(cmd=self.pg_remove)
        pg_remove_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      required=True,
                                      help='Instance name')
        pg_role_parser = pg_subparser.add_parser(name='role', help='PostgreSQL Role Commands')
        pg_role_subparser = pg_role_parser.add_subparsers()
        pg_role_create_parser = pg_role_subparser.add_parser(name='create', help='Create a role')
        pg_role_create_parser.add_argument('-n', '--instance-name',
                                           dest='name',
                                           required=True,
                                           help='Instance name')
        pg_role_create_parser.add_argument('-r', '--role-name',
                                           dest='role_name',
                                           required=True,
                                           help='Role name')
        pg_role_create_parser.add_argument('-p', '--role-password',
                                           dest='role_password',
                                           required=False,
                                           default=generator.token_urlsafe(16),
                                           help='Role password')
        pg_role_create_parser.add_argument('--create-schema',
                                           dest='create_schema',
                                           action='store_true',
                                           required=False,
                                           default=True,
                                           help='Create an associated schema for this role')
        pg_role_create_parser.set_defaults(cmd=self.pg_role_create)

        pg_role_remove_parser = pg_role_subparser.add_parser(name='remove', help='Remove a role')
        pg_role_remove_parser.add_argument('-n', '--instance_name',
                                           dest='name',
                                           required=True,
                                           help='Instance name')
        pg_role_remove_parser.add_argument('-r', '--role-name',
                                           dest='role_name',
                                           required=True,
                                           help='Role name')
        pg_role_remove_parser.add_argument('--remove-schema',
                                           dest='remove_schema',
                                           action='store_true',
                                           required=False,
                                           default=False,
                                           help='Remove the schema associated with this role')
        pg_role_remove_parser.set_defaults(cmd=self.pg_role_remove)

        pg_dumpall_parser = pg_subparser.add_parser(name='dumpall', help='PostgreSQL dumpall')
        pg_dumpall_parser.add_argument('-n', '--instance-name',
                                       dest='name',
                                       required=True,
                                       help='Instance name')
        pg_dumpall_parser.add_argument('-o', '--dumpfile',
                                       dest='dumpfile',
                                       required=True,
                                       help='File to dump output into')
        pg_dumpall_parser.set_defaults(cmd=self.pg_dumpall)

        pg_dump_parser = pg_subparser.add_parser(name='dump', help='PostgreSQL dump')
        pg_dump_parser.add_argument('-n', '--instance-name',
                                    dest='name',
                                    required=True,
                                    help='Instance name')
        pg_dump_parser.add_argument('-o', '--dumpfile',
                                    dest='dumpfile',
                                    required=True,
                                    help='File to dump output into')
        pg_dump_parser.add_argument('-d', '--database',
                                    dest='database',
                                    required=False,
                                    help='Database containing the schema')
        pg_dump_parser.add_argument('-s', '--schema',
                                    dest='schema',
                                    required=True,
                                    help='Schema to dump')
        pg_dump_parser.set_defaults(cmd=self.pg_dump)

        pg_restore_parser = pg_subparser.add_parser(name='restore', help='PostgreSQL restore')
        pg_restore_parser.add_argument('-n', '--instance-name',
                                       dest='name',
                                       required=True,
                                       help='Instance name')
        pg_restore_parser.add_argument('-o', '--dumpfile',
                                       dest='dumpfile',
                                       required=True,
                                       help='Dump file to restore from')
        pg_restore_parser.set_defaults(cmd=self.pg_restore)

    def pg_create(self, runtime: 'Runtime', args: argparse.Namespace):
        runtime.platform.apply(self)
        runtime.secreta.add(
            args.name,
            {
                'connection': f'postgresql://localhost:5432/{self.environment.get("POSTGRES_DB")}',
                'roles': {
                    'postgres': self.environment.get('POSTGRES_PASSWORD')
                }
            })

    def pg_remove(self, runtime: 'Runtime', args: argparse.Namespace):
        blueprint_instance = runtime.instance_get(name=args.name, blueprint=self)
        runtime.instance_remove(blueprint_instance)

    def pg_role_create(self, runtime: 'Runtime', args: argparse.Namespace):
        conn = self._pg_conn(runtime, args.name)
        cur = conn.cursor()
        query = sql.SQL('CREATE ROLE {} ENCRYPTED PASSWORD %s LOGIN').format(sql.Identifier(args.role_name))
        cur.execute(query, (args.role_password,))
        query = sql.SQL('CREATE SCHEMA AUTHORIZATION {}').format(sql.Identifier(args.role_name))
        cur.execute(query)
        query = sql.SQL('ALTER ROLE {} SET search_path TO {}').format(
            sql.Identifier(args.role_name),
            sql.Identifier(args.role_name)
        )
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        runtime.secreta.get(args.name, {}).get('roles', {})[args.role_name] = args.role_password
        runtime.save()

    def pg_role_remove(self, runtime: 'Runtime', args: argparse.Namespace):
        conn = self._pg_conn(runtime, args.name)
        cur = conn.cursor()
        if args.remove_schema:
            query = sql.SQL('DROP SCHEMA IF EXISTS {}').format(sql.Identifier(args.role_name))
            cur.execute(query)
        query = sql.SQL('DROP ROLE {}').format(sql.Identifier(args.role_name))
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
        if args.role_name in runtime.secreta.get(args.name, {}).get('roles'):
            del runtime.secreta[args.name]['roles'][args.role_name]
        runtime.save()

    def pg_dumpall(self, runtime: 'Runtime', args: argparse.Namespace):
        instance = runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            runtime.output.error(f'There is no instance called {args.name}')
            return
        result = instance.platform.execute(['exec', args.name,
                                            '/usr/local/bin/pg_dumpall', '-h', 'localhost', '-U', 'postgres'])
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)

    def pg_dump(self, runtime: 'Runtime', args: argparse.Namespace):
        instance = runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            runtime.output.error(f'There is no instance called {args.name}')
            return
        cmd = ['exec', args.name, '/usr/local/bin/pg_dump', '-h', 'localhost', '-U', 'postgres', '-n', args.schema]
        if hasattr(args, 'database'):
            cmd.extend(['-d', args.database])
        result = instance.platform.execute(cmd)
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)

    def pg_restore(self, runtime: 'Runtime', args: argparse.Namespace):
        instance = runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            runtime.output.error(f'There is no instance called {args.name}')
            return
        cmd = ['exec', args.name, '/usr/local/bin/pg_restore', '-h', 'localhost', '-U', 'postgres', '-n', args.schema]
        if hasattr(args, 'database'):
            cmd.extend(['-d', args.database])
        result = instance.platform.execute(cmd)
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)

    def _pg_conn(self, runtime: 'Runtime', instance_name: str):
        """
        Obtain an administrative connection to the PostgreSQL instance. You currently must close the connection
        yourself.

        Args:
            runtime: The runtime object
            instance_name: Name of the PostgreSQL instance to connect to

        Returns:
            A DBAPI Connection object
        """
        instance_secrets = runtime.secreta.get(instance_name, {})
        instance_connection = instance_secrets.get('connection')
        if instance_connection is None:
            raise MurkyWaterException(msg='Missing connection string for this instance in secrets')
        instance_password = instance_secrets.get('roles', {}).get('postgres')
        if instance_password is None:
            raise MurkyWaterException(msg='Missing postgres password for this instance in secrets')
        return psycopg2.connect(instance_connection,
                                user='postgres',
                                password=instance_password)
