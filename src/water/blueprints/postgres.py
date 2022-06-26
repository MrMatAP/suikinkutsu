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
import psycopg2
from psycopg2 import sql

from schema import BlueprintSchema
from water import MurkyWaterException
from water.blueprints.blueprint import Blueprint
from constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class PostgreSQL(Blueprint):
    kind: str = 'postgres'
    description: str = 'PostgreSQL is a modern relational database'
    _defaults: BlueprintSchema = BlueprintSchema(
        kind='postgres',
        name='pg',
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

    @classmethod
    def cli_prepare(cls, parser):
        pg_parser = parser.add_parser(name='pg', help='PostgreSQL Commands')
        pg_subparser = pg_parser.add_subparsers()
        pg_create_parser = pg_subparser.add_parser(name='create', help='Create a PostgreSQL instance')
        pg_create_parser.set_defaults(cmd=cls.pg_create)
        pg_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default=cls._defaults.name,
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
        pg_account_create_parser = pg_account_subparser.add_parser(name='create', help='Create an account')
        pg_account_create_parser.add_argument('-n', '--instance-name',
                                              dest='name',
                                              required=True,
                                              help='Instance name')
        pg_account_create_parser.add_argument('-a', '--account-name',
                                              dest='account_name',
                                              required=True,
                                              help='Account name')
        pg_account_create_parser.add_argument('-p', '--account-password',
                                              dest='account_password',
                                              required=False,
                                              default=secrets.token_urlsafe(16),
                                              help='Account password')
        pg_account_create_parser.set_defaults(cmd=cls.pg_account_create)

        pg_backup_parser = pg_subparser.add_parser(name='backup', help='PostgreSQL backup')
        pg_backup_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      required=True,
                                      help='Instance name')
        pg_backup_parser.add_argument('-o', '--output-dir',
                                      dest='output_dir',
                                      required=True,
                                      help='Output directory')
        pg_backup_parser.set_defaults(cmd=cls.pg_backup)

    @classmethod
    def cli_assess(cls, args: Namespace):
        super().cli_assess(args)

    @classmethod
    def pg_create(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_create(instance)
        runtime_secrets = runtime.secrets
        if instance.name not in runtime_secrets:
            runtime_secrets[instance.name] = {
                'connection': f'postgresql://localhost:5432/{instance.environment.get("POSTGRES_DB")}',
                'accounts': {
                    'postgres': instance.environment.get('POSTGRES_PASSWORD')
                }
            }
        else:
            runtime_secrets[instance.name]['connection'] = f'postgresql://localhost:5432/{instance.environment.get("POSTGRES_DB")}'
            runtime_secrets_accounts = runtime_secrets[instance.name]['accounts']
            runtime_secrets_accounts['postgres'] = instance.environment.get('POSTGRES_PASSWORD')
        runtime.secrets_save()

    @classmethod
    def pg_list(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_create(instance)

    @classmethod
    def pg_remove(cls, runtime, args: Namespace):
        instance = cls(name=args.name)
        runtime.platform.service_remove(instance)

    @classmethod
    def pg_account_create(cls, runtime, args):
        instance_secrets = runtime.secrets.get(args.name)
        if instance_secrets is None:
            raise MurkyWaterException(msg='No secrets for this instance')
        conn = psycopg2.connect(instance_secrets.get('connection'),
                                user='postgres',
                                password=instance_secrets['accounts'].get('postgres'))
        cur = conn.cursor()
        query = sql.SQL('CREATE ROLE {} ENCRYPTED PASSWORD %s LOGIN').format(sql.Identifier(args.account_name))
        cur.execute(query, (args.account_password,))
        conn.commit()
        cur.close()
        conn.close()
        runtime_secrets = runtime.secrets
        runtime_secrets_accounts = runtime_secrets[args.name]['accounts']
        runtime_secrets_accounts[args.account_name] = args.account_password
        runtime.secrets_save()

    @classmethod
    def pg_backup(cls, runtime, args):
        instance_secrets = runtime.secrets.get(args.name)
        if instance_secrets is None:
            raise MurkyWaterException(msg='No secrets for this instance')
        # TODO:
        # nerdctl exec -it pg pg_dumpall -h localhost -U postgres -l localdb

