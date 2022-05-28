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

import sys
import os
import typing
import argparse
import inspect
import configparser
from typing import List, Dict, Any
from rich.table import Table
from rich.box import ROUNDED
from water import __version__, __default_configuration__, MurkyWaterException, console
from water.platforms import Platform, Nerdctl
from water.blueprints import PostgreSQL


def output_table(title: str, columns: List[str], rows: List[Any]):
    table = Table(title=title, box=ROUNDED)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(row)
    console.print(table)


def up(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    console.print('Starting environment')
    return 0


def down(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    console.print('Stopping environment')
    return 0


def instance_list(platform: Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    platform.instance_list()
    return 0


def main(args: typing.List) -> int:
    """
    Main entry point for the cook CLI
    Args:
        args: Command line arguments

    Returns:
        An exit code. 0 when successful, non-zero otherwise
    """
    parser = argparse.ArgumentParser(add_help=False, description=f'{__name__} - {__version__}')
    parser.add_argument('-c', '--config',
                        dest='config',
                        required=False,
                        default=os.path.join(os.path.expanduser('~/.water')),
                        help='Configuration file')
    parser.add_argument('-o', '--output',
                        dest='output',
                        choices=['table'],
                        default='table',
                        help='Output style')
    subparsers = parser.add_subparsers(dest='group')

    config_parser = subparsers.add_parser(name='config', help='Configuration Commands')
    config_subparser = config_parser.add_subparsers()
    config_show_parser = config_subparser.add_parser(name='show', help='Show current configuration')
    config_set_parser = config_subparser.add_parser(name='set', help='Set configuration')

    up_parser = subparsers.add_parser(name='up', help='Start cooking')
    up_parser.set_defaults(cmd=up)
    down_parser = subparsers.add_parser('down', help='Stop cooking')
    down_parser.set_defaults(cmd=down)
    list_parser = subparsers.add_parser(name='list', help='List')
    list_parser.set_defaults(cmd=instance_list)

    PostgreSQL.parser(subparsers)

    args = parser.parse_args(args)
    config = configparser.ConfigParser(strict=True)
    if args.config and os.path.exists(__default_configuration__):
        config.read(args.config)

    try:
        if hasattr(args, 'cmd'):
            platform = Nerdctl()
            # Do our thing
            return args.cmd(platform, config, args)() if inspect.isclass(args.cmd) else args.cmd(platform, config, args)
        else:
            parser.print_help()
        return 0
    except MurkyWaterException as mwe:
        console.print_exception()
        return mwe.code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
