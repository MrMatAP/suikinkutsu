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
from typing import List, Dict, Any
from rich.table import Table
from rich.box import ROUNDED
import yaml
from water import __version__, __configuration__, MurkyWaterException, console
import water.blueprints
import water.platforms


def output_table(title: str, columns: List[str], rows: List[Any]):
    table = Table(title=title, box=ROUNDED)
    for column in columns:
        table.add_column(column)
    for row in rows:
        table.add_row(row)
    console.print(table)


class Recipe:
    blueprints: List[water.blueprints.Blueprint] = []

    def __init__(self, runtime, args: argparse.Namespace):
        if not hasattr(args, 'recipe'):
            return
        if not os.path.exists(args.recipe):
            raise MurkyWaterException(msg=f'There is no recipe at {args.recipe}')
        try:
            with open(args.recipe, 'r', encoding='UTF-8') as r:
                raw_recipe = yaml.safe_load(r)
            parsed_recipe = water.blueprints.RecipeSchema.parse_obj(raw_recipe)
            for name, bp_schema in parsed_recipe.blueprints.items():
                if bp_schema.kind not in runtime.available_blueprints:
                    raise MurkyWaterException(msg=f'Blueprint {bp_schema.kind} for instance {name} is not known')
                blueprint = runtime.available_blueprints[bp_schema.kind].from_schema(runtime, name, bp_schema)
                self.blueprints.append(blueprint)
        except Exception as e:
            console.print_exception()


class Runtime:
    config_dir: str = os.path.expanduser(os.path.join('~', 'etc'))
    available_blueprints: Dict[str, water.blueprints.Blueprint] = {
        clazz.name: clazz for clazz in water.blueprints.Blueprint.__subclasses__()
    }
    available_platforms: List[water.platforms.Platform] = []
    default_platform: water.platforms.Platform
    recipe: Recipe

    def __init__(self, config_file: str):
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='UTF-8') as c:
                raw_config = yaml.safe_load(c)
            if 'config_dir' in raw_config:
                self.config_dir = raw_config['config_dir']

        [platform(self) for platform in water.platforms.Platform.__subclasses__()]
        if len(self.available_platforms) == 0:
            raise MurkyWaterException(msg='No platforms are available')
        self.default_platform = self.available_platforms[0]


def cook_up(runtime: Runtime, args: argparse.Namespace) -> int:
    try:
        [blueprint.create(runtime, args) for blueprint in runtime.recipe.blueprints]
        return 0
        # with open(args.recipe, 'r', encoding='UTF-8') as r:
        #     raw_recipe = yaml.safe_load(r)
        # parsed_recipe = water.models.RecipeSchema.parse_obj(raw_recipe)
        # console.print(parsed_recipe)
        # for name, blueprint_model in parsed_recipe.blueprints.items():
        #     if blueprint_model.kind == 'postgres':
        #         blueprint_model.merge_defaults(water.blueprints.postgres.PostgreSQL.defaults)
        # console.print(parsed_recipe)
    except Exception as e:
        console.print_exception()
        return 1


def cook_down(runtime: Runtime, args: argparse.Namespace) -> int:
    try:
        [blueprint.remove(runtime, args) for blueprint in runtime.recipe.blueprints]
        return 0
    except Exception as e:
        console.print_exception()
        return 1


def cook_list(runtime: Runtime, args: argparse.Namespace) -> int:
    try:
        [blueprint.list(runtime, args) for blueprint in runtime.recipe.blueprints]
        return 0
    except Exception as e:
        console.print_exception()
        return 1


def main(argv: typing.List) -> int:
    """
    Main entry point for the cook CLI
    Args:
        argv: Command line arguments

    Returns:
        An exit code. 0 when successful, non-zero otherwise
    """
    parser = argparse.ArgumentParser(add_help=False, description=f'{__name__} - {__version__}')
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
    pf_list_parser = pf_subparser.add_parser('list', help='List available platforms')
    pf_list_parser.set_defaults(cmd=water.platforms.Platform.platform_list)

    bp_parser = subparsers.add_parser(name='blueprint', help='Blueprint Commands')
    bp_subparser = bp_parser.add_subparsers()
    bp_list_parser = bp_subparser.add_parser('list', help='List available blueprints')
    bp_list_parser.set_defaults(cmd=water.blueprints.Blueprint.blueprint_list)

    cook_parser = subparsers.add_parser(name='cook', help='Cook environments')
    cook_parser.add_argument('-r', '--recipe',
                             dest='recipe',
                             required=False,
                             default=os.path.join(os.path.curdir, 'Recipe'),
                             help='The recipe to instantiate')
    cook_subparser = cook_parser.add_subparsers()
    cook_up_parser = cook_subparser.add_parser(name='up', help='Start an environment')
    cook_up_parser.set_defaults(cmd=cook_up)
    cook_list_parser = cook_subparser.add_parser(name='list', help='List environments')
    cook_list_parser.set_defaults(cmd=cook_list)
    cook_down_parser = cook_subparser.add_parser('down', help='Stop a running environment')
    cook_down_parser.set_defaults(cmd=cook_down)

    try:
        runtime = Runtime(config_file=__configuration__)
        [blueprint.cli(subparsers) for blueprint in runtime.available_blueprints.values()]
        [platform.cli(subparsers) for platform in runtime.available_platforms]
        args = parser.parse_args(argv)

        runtime.recipe = Recipe(runtime, args)

        if hasattr(args, 'cmd'):
            return args.cmd(runtime, args)
        else:
            parser.print_help()
        return 0
    except MurkyWaterException as mwe:
        console.print_exception()
        return mwe.code


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
