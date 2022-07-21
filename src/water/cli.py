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
import argparse

from water import __version__, MurkyWaterException
from water.runtime import Runtime


def config_show(runtime: Runtime, args: argparse.Namespace) -> int:
    runtime.output.displayable(runtime.raw_config)
    return 0


def config_set(runtime: Runtime, args: argparse.Namespace) -> int:
    runtime.config_dir = args.set_config_dir
    runtime.config_output = args.set_config_output
    runtime.config_save()
    return 0


def platform_list(runtime: Runtime, args: argparse.Namespace) -> int:
    runtime.output.platform_list(runtime)
    return 0


def blueprint_list(runtime: Runtime, args: argparse.Namespace) -> int:
    runtime.output.blueprint_list(runtime)
    return 0


def instance_list(runtime: Runtime, args: argparse.Namespace) -> int:
    runtime.output.instance_list(runtime)
    return 0


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
        #console.print_exception()
        return 1


def cook_show(runtime: Runtime, args: argparse.Namespace) -> int:
    try:
        runtime.output.cook_show(runtime)
        return 0
    except Exception as e:
        #console.print_exception()
        return 1


def cook_down(runtime: Runtime, args: argparse.Namespace) -> int:
    try:
        [blueprint.remove(runtime, args) for blueprint in runtime.recipe.blueprints]
        return 0
    except Exception as e:
        #console.print_exception()
        return 1


def main() -> int:
    """
    Main entry point for the cook CLI

    Returns:
        An exit code. 0 when successful, non-zero otherwise
    """
    parser = argparse.ArgumentParser(add_help=False, description=f'{__name__} - {__version__}')
    subparsers = parser.add_subparsers(dest='group')

    config_parser = subparsers.add_parser(name='config', help='Configuration Commands')
    config_subparser = config_parser.add_subparsers()
    config_show_parser = config_subparser.add_parser(name='show', help='Show current configuration')
    config_show_parser.set_defaults(cmd=config_show)
    config_set_parser = config_subparser.add_parser(name='set', help='Set configuration')
    config_set_parser.add_argument('--config-dir',
                                   dest='set_config_dir',
                                   required=False,
                                   help='Persist the directory in which water will generate configuration')
    config_set_parser.add_argument('--output',
                                   dest='set_config_output',
                                   required=False,
                                   help='Persist the preferred output style in the water configuration file')
    config_set_parser.add_argument('--platform',
                                   dest='set_config_platform',
                                   required=False,
                                   help='Persist the preferred platform in the water configuration file')
    config_set_parser.set_defaults(cmd=config_set)

    pf_parser = subparsers.add_parser(name='platform', help='Platform Commands')
    pf_subparser = pf_parser.add_subparsers()
    pf_list_parser = pf_subparser.add_parser('list', help='List available platforms')
    pf_list_parser.set_defaults(cmd=platform_list)

    bp_parser = subparsers.add_parser(name='blueprint', help='Blueprint Commands')
    bp_subparser = bp_parser.add_subparsers()
    bp_list_parser = bp_subparser.add_parser('list', help='List available blueprints')
    bp_list_parser.set_defaults(cmd=blueprint_list)

    instance_parser = subparsers.add_parser(name='instance', help='Instance Commands')
    instance_subparser = instance_parser.add_subparsers()
    instance_list_parser = instance_subparser.add_parser('list', help='List instances')
    instance_list_parser.set_defaults(cmd=instance_list)

    cook_parser = subparsers.add_parser(name='cook', help='Cook environments')
    cook_parser.add_argument('-r', '--recipe',
                             dest='recipe',
                             required=False,
                             default=os.path.join(os.path.curdir, 'Recipe'),
                             help='The recipe to instantiate')
    cook_subparser = cook_parser.add_subparsers()
    cook_up_parser = cook_subparser.add_parser(name='up', help='Start an environment')
    cook_up_parser.set_defaults(cmd=cook_up)
    cook_show_parser = cook_subparser.add_parser(name='show', help='Show the environment')
    cook_show_parser.set_defaults(cmd=cook_show)
    cook_down_parser = cook_subparser.add_parser('down', help='Stop a running environment')
    cook_down_parser.set_defaults(cmd=cook_down)

    runtime = None
    try:
        runtime = Runtime()
        [blueprint.cli_prepare(subparsers) for blueprint in runtime.available_blueprints.values()]
        [platform.cli_prepare(subparsers) for platform in runtime.available_platforms.values()]
        runtime.cli_prepare(parser)
        args = parser.parse_args()
        runtime.cli_assess(args)
        [blueprint.cli_assess(args) for blueprint in runtime.available_blueprints.values()]
        [platform.cli_assess(args) for platform in runtime.available_platforms.values()]

        # Execute the desired command
        if hasattr(args, 'cmd'):
            return args.cmd(runtime, args)
        else:
            parser.print_help()
        return 0
    except MurkyWaterException as mwe:
        if runtime:
            runtime.output.exception(ex=mwe)
        else:
            print(f'An exception occurred during initialisation: {mwe}')
        return mwe.code


if __name__ == '__main__':
    sys.exit(main())
