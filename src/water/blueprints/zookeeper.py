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

from water.schema import BlueprintSchema
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY
from .blueprint import Blueprint


class Zookeeper(Blueprint):
    name: str = 'zookeeper'
    description: str = 'Zookeeper'
    _defaults: BlueprintSchema = BlueprintSchema(
        image='confluentinc/cp-zookeeper:7.2.1',
        volumes={},
        environment={
            'ZOOKEEPER_CLIENT_PORT': 32181,
            'ZOOKEEPER_TICK_TIME': 2000,
            'ZOOKEEPER_SYNC_LIMIT': 2,
            'ZOOKEEPER_SERVER_ID': 1
        },
        ports={'32181': '32181'},
        labels={
            LABEL_BLUEPRINT: 'zookeeper',
            LABEL_CREATED_BY: 'water'
        },
        depends_on=[]
    )

    def cli_prepare(self, parser):
        zk_parser = parser.add_parser(name='zookeeper', help='Zookeeper Commands')
        zk_subparser = zk_parser.add_subparsers()
        zk_create_parser = zk_subparser.add_parser(name='create', help='Create a Zookeeper instance')
        zk_create_parser.set_defaults(cmd=self.zookeeper_create)
        zk_create_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      default='zookeeper',
                                      required=False,
                                      help='Instance name')
        zk_list_parser = zk_subparser.add_parser(name='list', help='List Zookeeper instances')
        zk_list_parser.set_defaults(cmd=self.zookeeper_list)
        zk_remove_parser = zk_subparser.add_parser(name='remove', help='Remove Zookeeper instances')
        zk_remove_parser.set_defaults(cmd=self.zookeeper_remove)
        zk_remove_parser.add_argument('-n', '--instance-name',
                                      dest='name',
                                      required=True,
                                      help='Instance name')

    def zookeeper_create(self, runtime, args: Namespace):
        runtime.platform.service_create(self)

    def zookeeper_list(self, runtime, args: Namespace):
        runtime.platform.service_list(self.name)

    def zookeeper_remove(self, runtime, args: Namespace):
        runtime.platform.service_remove(self)
