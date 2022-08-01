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
import secrets
import psycopg2
from psycopg2 import sql

from water.schema import BlueprintSchema
from water.exceptions import MurkyWaterException
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from .blueprint import Blueprint, BlueprintInstance


class PostgreSQL(Blueprint):
    """
    PostgreSQL blueprint
    """
    name: str = 'postgres'
    description: str = 'PostgreSQL is a modern relational database'
    _defaults: BlueprintSchema = BlueprintSchema(
        image='postgres:14.3-alpine',
        volumes={'pg_datavol': '/var/lib/postgresql/data'},
        environment={
            'POSTGRES_DB': 'localdb',
            'POSTGRES_PASSWORD': secrets.token_urlsafe(16),
            'PGDATA': '/var/lib/postgresql/data/pgdata'
        },
        ports={'5432': '5432'},
        labels={
            LABEL_BLUEPRINT: 'postgres',
            LABEL_CREATED_BY: 'water'
        },
        depends_on=[]
    )

    def cli_prepare(self, parser):
        pg_parser = parser.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=self.pg_create)
        pg_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default='pg',
                                      required=False,
                                      help='Instance name')
        pg_list_parser = pg_subparser.add_parser(name='list', help='List PostgreSQL instances')
        pg_list_parser.set_defaults(cmd=self.pg_list)
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
                                           default=secrets.token_urlsafe(16),
                                           help='Role password')
        pg_role_create_parser.add_argument('--create-schema',
                                           dest='create_schema',
                                           required=False,
                                           default=True,
                                           help='Create an associated schema for this role')
        pg_role_create_parser.set_defaults(cmd=self.pg_role_create)

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

    def pg_create(self, runtime, args: Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=runtime.platform,
                                               blueprint=self)
        runtime.instance_create(blueprint_instance)
        runtime_secrets = runtime.secrets
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': f'postgresql://localhost:5432/{self.environment.get("POSTGRES_DB")}',
                'roles': {
                    'postgres': self.environment.get('POSTGRES_PASSWORD')
                }
            }
        else:
            runtime_secrets[args.name][
                'connection'] = f'postgresql://localhost:5432/{self.environment.get("POSTGRES_DB")}'
            runtime_secrets_roles = runtime_secrets[args.name]['roles']
            runtime_secrets_roles['postgres'] = self.environment.get('POSTGRES_PASSWORD')
        runtime.secrets = runtime_secrets

    def pg_list(self, runtime: 'Runtime', args: Namespace):
        instances = runtime.instance_list(blueprint=self)
        runtime.output.displayable(instances)

    def pg_remove(self, runtime: 'Runtime', args: Namespace):
        blueprint_instance = runtime.instance_get(name=args.name, blueprint=self)
        runtime.instance_remove(blueprint_instance)

    def pg_role_create(self, runtime: 'Runtime', args: Namespace):
        instance_secrets = self.runtime.secrets.get(args.name)
        if instance_secrets is None:
            raise MurkyWaterException(msg='No secrets for this instance')
        conn = psycopg2.connect(instance_secrets.get('connection'),
                                user='postgres',
                                password=instance_secrets['roles'].get('postgres'))
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
        runtime_secrets = self.runtime.secrets
        runtime_secrets_roles = runtime_secrets[args.name]['roles']
        runtime_secrets_roles[args.role_name] = args.role_password
        self.runtime.secrets_save()

    def pg_dumpall(self, runtime: 'Runtime', args: Namespace):
        instance = self.runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            self.runtime.output.error(f'There is no instance called {args.name}')
            return
        result = instance.platform.execute(['exec', args.name,
                                            '/usr/local/bin/pg_dumpall', '-h', 'localhost', '-U', 'postgres'])
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)

    def pg_dump(self, runtime: 'Runtime', args: Namespace):
        instance = self.runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            self.runtime.output.error(f'There is no instance called {args.name}')
            return
        cmd = ['exec', args.name, '/usr/local/bin/pg_dump', '-h', 'localhost', '-U', 'postgres', '-n', args.schema]
        if hasattr(args, 'database'):
            cmd.extend(['-d', args.database])
        result = instance.platform.execute(cmd)
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)

    def pg_restore(self, runtime: 'Runtime', args: Namespace):
        instance = self.runtime.instance_get(name=args.name, blueprint=self)
        if not instance:
            self.runtime.output.error(f'There is no instance called {args.name}')
            return
        cmd = ['exec', args.name, '/usr/local/bin/pg_restore', '-h', 'localhost', '-U', 'postgres', '-n', args.schema]
        if hasattr(args, 'database'):
            cmd.extend(['-d', args.database])
        result = instance.platform.execute(cmd)
        with open(args.dumpfile, 'wt+', encoding='UTF-8') as d:
            d.write(result.stdout)
