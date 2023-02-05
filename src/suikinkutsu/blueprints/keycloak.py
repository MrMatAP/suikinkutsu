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
import secrets

from suikinkutsu.config import Configuration
from suikinkutsu.models import VolumeBinding, PortBinding
from suikinkutsu.blueprints.blueprint import Blueprint, BlueprintInstance


class Keycloak(Blueprint):
    """
    Keycloak Blueprint
    """

    name = 'keycloak'

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._config = config
        self._description = 'Keycloak is an Identity Provider implementing OAuth 2 and ' \
                            'SAML authentication/authorisation'
        self._image = 'jboss/keycloak'
        self._version = '16.1.1'
        self._environment = {
            # 'DB_VENDOR': 'postgres',
            # 'DB_ADDR': 'pg',
            # 'DB_DATABASE': 'localdb',
            # 'DB_USER': 'keycloak',
            # 'DB_PASSWORD': 'keycloak',
            # 'DB_SCHEMA': 'keycloak',
            'KEYCLOAK_USER': 'admin',
            'KEYCLOAK_PASSWORD': secrets.token_urlsafe(16)
        }
        self._volume_bindings = [
            VolumeBinding(name='kc_importvol', mount_point='/import')
        ]
        self._port_bindings = [
            PortBinding(container_port=8080, host_ip='127.0.0.1', host_port=8080, protocol='tcp')
        ]
        self._depends_on = []

    def cli_prepare(self, parser, subparsers):
        kc_parser = subparsers.add_parser(name='kc', help='Keycloak Commands')
        kc_subparser = kc_parser.add_subparsers()
        kc_create_parser = kc_subparser.add_parser(name='create', help='Create a Keycloak instance')
        kc_create_parser.set_defaults(cmd=self.kc_create)
        kc_create_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default='kc',
                                      required=False,
                                      help='Instance name')
        kc_remove_parser = kc_subparser.add_parser(name='remove', help='Remove Keycloak instances')
        kc_remove_parser.set_defaults(cmd=self.kc_remove)
        kc_remove_parser.add_argument('-n', '--name',
                                      dest='name',
                                      default=self.name,
                                      required=False,
                                      help='Instance name')

    def kc_create(self, runtime, args: argparse.Namespace):
        blueprint_instance = BlueprintInstance(name=args.name,
                                               platform=self.runtime.platform,
                                               blueprint=self)
        self.runtime.instance_create(blueprint_instance)
        runtime_secrets = self.runtime.secreta
        if args.name not in runtime_secrets:
            runtime_secrets[args.name] = {
                'connection': 'http://localhost:8080',
                'accounts': {
                    'admin': self.environment.get('KEYCLOAK_PASSWORD')
                }
            }
        else:
            runtime_secrets[args.name]['connection'] = 'http://localhost:8080'
            runtime_secrets[args.name]['admin'] = self.environment.get('KEYCLOAK_PASSWORD')
        self.runtime.secreta = runtime_secrets

    def kc_remove(self, runtime, args: argparse.Namespace):
        blueprint_instance = self.runtime.instance_get(name=args.name, blueprint=self)
        self.runtime.instance_remove(blueprint_instance)
