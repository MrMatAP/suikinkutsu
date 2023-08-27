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
from suikinkutsu.outputs import OutputEntry
from suikinkutsu.config import Configuration


class Project(object):
    """
    A project
    """

    def __init__(self, config: Configuration):
        self._config = config

    # pylint: disable=unused-argument
    def cli_prepare(self, parser, subparser):
        project_parser = subparser.add_parser(name='project', help='Project Commands')
        project_subparser = project_parser.add_subparsers()
        project_show_parser = project_subparser.add_parser(name='show', help='Show current project configuration')
        project_show_parser.set_defaults(cmd=self.project_show)

    def cli_assess(self, args: argparse.Namespace):
        pass

    # pylint: disable=unused-argument
    def project_show(self, runtime, args: argparse.Namespace) -> int:
        output = OutputEntry(title='Project',
                             columns=['Key', 'Value'],
                             msg=[
                                 ['recipe_file', self._config.recipe_file.value],
                                 ['secrets_file', self._config.secrets_file.value]
                             ])
        runtime.output.print(output)
        return 0
