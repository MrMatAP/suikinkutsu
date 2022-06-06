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
import yaml
from water import __version__, __default_configuration__, MurkyWaterException, console
import water.blueprints
import water.platforms


def output_table(title: str, columns: List[str], rows: List[Any]):
    table = Table(title=title, box=ROUNDED)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(row)
    console.print(table)


def up(platform: water.platforms.Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    if not os.path.exists(args.recipe):
        console.print(f'There is no recipe at {args.recipe}')
        return 1
    try:
        with open(args.recipe, 'r', encoding='UTF-8') as r:
            raw_recipe = yaml.safe_load(r)
        parsed_recipe = water.models.Recipe.parse_obj(raw_recipe)
        console.print(parsed_recipe)
    except Exception as e:
        console.print_exception()


def down(platform: water.platforms.Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    console.print('Stopping environment')
    return 0


def instance_list(platform: water.platforms.Platform, config: configparser.ConfigParser, args: argparse.Namespace) -> int:
    platform.service_list()
    return 0


def main(argv: typing.List) -> int:
    """
    Main entry point for the cook CLI
    Args:
        argv: Command line arguments

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

    pf_parser = subparsers.add_parser(name='platform', help='Platform Commands')
    pf_subparser = pf_parser.add_subparsers()
    pf_list_parser = pf_subparser.add_parser('list', help='List platforms')
    pf_list_parser.set_defaults(cmd=water.platforms.Platform.list)

    up_parser = subparsers.add_parser(name='up', help='Start cooking')
    up_parser.add_argument('-r', '--recipe',
                           dest='recipe',
                           required=False,
                           default=os.path.join(os.path.curdir, 'Recipe'),
                           help='The recipe to instantiate')
    up_parser.set_defaults(cmd=up)
    down_parser = subparsers.add_parser('down', help='Stop cooking')
    down_parser.set_defaults(cmd=down)
    list_parser = subparsers.add_parser(name='list', help='List')
    list_parser.set_defaults(cmd=instance_list)

    for blueprint_class in water.blueprints.Blueprint.__subclasses__():
        blueprint_class.parser(subparsers)

    args = parser.parse_args(argv)
    config = configparser.ConfigParser(strict=True)
    if args.config and os.path.exists(__default_configuration__):
        config.read(args.config)

    try:
        if hasattr(args, 'cmd'):
            # TODO: hardcoded default
            platform = water.platforms.nerdctl.Nerdctl()
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
