#  MIT License
#
#  Copyright (c) 2023 Mathieu Imfeld
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

import typing
import argparse
import pathlib
import json

from suikinkutsu.config import Configuration
from suikinkutsu.outputs import OutputEntry


class Secreta:
    """
    Secrets Manager
    """

    def __init__(self, config: Configuration):
        self._config = config
        self._secrets_file = pathlib.Path(config.secrets_file.value)
        self._secrets = {}
        if self._secrets_file.exists():
            self._secrets = json.loads(self._secrets_file.read_text(encoding='UTF-8'))

    def cli_prepare(self, parser, subparsers):
        secrets_parser = subparsers.add_parser(name='secrets', help='Secrets Commands')
        secrets_subparser = secrets_parser.add_subparsers()
        secrets_list_parser = secrets_subparser.add_parser('list', help='List secrets')
        secrets_list_parser.set_defaults(cmd=self.secrets_list)

    def cli_assess(self, args: argparse.Namespace):
        pass

    def secrets_list(self, runtime, args: argparse.Namespace):
        # output = OutputEntry(title='Secrets',
        #                      columns=['Name', 'Secrets'],
        #                      msg=[[name, ]])
        output = OutputEntry(title='Secrets',
                             columns=['Instance Name', 'Secret'],
                             msg=[[key, str(value)] for key, value in self._secrets.items()])
        runtime.output.print(output)
        pass

    def add(self, key: str, value: typing.Dict):
        self._secrets[key] = value
        self._save()

    def _save(self):
        self._secrets_file.parent.mkdir(parents=True, exist_ok=True)
        self._secrets_file.write_text(json.dumps(self._secrets, indent=2))
