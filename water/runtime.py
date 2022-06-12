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

import os
import json
from typing import Dict, List, Tuple, Any
from argparse import ArgumentParser, Namespace
from pydantic import BaseModel, Field

from water import DEFAULT_CONFIG_FILE, DEFAULT_CONFIG_DIR, DEFAULT_OUTPUT
from water.exceptions import MurkyWaterException
from water.outputs import Output, DefaultOutput
from water.blueprints import Blueprint
from water.platforms import Platform
from water.recipe import Recipe


class WaterConfiguration(BaseModel):
    config_dir: str = Field(description='Directory into which water generates configuration files', default=None)
    output: str = Field(description='Default output style', default=None)


class Runtime:
    config_file: str = DEFAULT_CONFIG_FILE
    config_file_source: str = 'Default value'
    config_dir: str = None
    config_dir_source: str = None
    output: Output = DefaultOutput()
    output_source: str = None
    platform: Platform
    recipe: Recipe

    available_outputs: Dict[str, Output] = {clazz.name: clazz for clazz in Output.__subclasses__()}
    available_blueprints: Dict[str, Blueprint] = {clazz.name: clazz for clazz in Blueprint.__subclasses__()}
    available_platforms: List[Platform] = []

    def __init__(self):
        if os.getenv('WATER_CONFIG_FILE'):
            self.config_file = os.getenv('WATER_CONFIG_FILE')
            self.config_file_source = 'Environment'
        raw_config = self._config_load()

        self.config_dir, self.config_dir_source = Runtime._override_config(config=raw_config,
                                                                           env_key='WATER_CONFIG_DIR',
                                                                           config_key='config_dir',
                                                                           default=DEFAULT_CONFIG_DIR)
        configured_output, self.output_source = Runtime._override_config(config=raw_config,
                                                                         env_key='WATER_OUTPUT',
                                                                         config_key='output',
                                                                         default=DEFAULT_OUTPUT)
        if configured_output not in self.available_outputs:
            raise MurkyWaterException(msg=f'Configured output {configured_output} is not available. Pick one of '
                                          f'{str.join(",", self.available_outputs.keys())}')
        self.output = self.available_outputs.get(configured_output)()

        [platform(self) for platform in Platform.__subclasses__()]
        if len(self.available_platforms) == 0:
            raise MurkyWaterException(msg='No platforms are available')
        self.platform = self.available_platforms[0]

    @staticmethod
    def _override_config(config: WaterConfiguration, env_key: str, config_key: str, default: str) -> Tuple[str, str]:
        # Configuration override preference: ENV variable > config file > default
        env_value = os.getenv(env_key)
        if env_value:
            return os.getenv(env_key), f'Environment ({env_key})'
        config_value = config.__getattribute__(config_key)
        if config_value:
            return config_value, f'Configuration ({config_key})'
        return default, f'Default value'

    def cli_prepare(self, parser: ArgumentParser):
        parser.add_argument('-c',
                            dest='override_config_file',
                            required=False,
                            help='Override the water configuration file for this invocation')
        parser.add_argument('-d',
                            dest='override_config_dir',
                            required=False,
                            help='Override the directory into which configuration is generated for this invocation')
        parser.add_argument('-o', '--output',
                            dest='override_output',
                            choices=[name for name in self.available_outputs.keys()],
                            required=False,
                            help='Override the specific output style for this invocation')

    def cli_assess(self, args: Namespace):
        if args.override_config_dir and args.override_config_dir != DEFAULT_CONFIG_DIR:
            self.config_dir = args.override_config_dir
            self.config_dir_source = 'CLI'
        if args.override_output and args.override_output != DEFAULT_OUTPUT:
            if not self.available_outputs.get(args.override_output):
                raise MurkyWaterException(msg=f'Output {args.override_output} is not available. Pick one of '
                                              f'{str.join(",", self.available_outputs.keys())}')
            self.output = self.available_outputs.get(args.override_output)()
            self.output_source = 'CLI'

    def _config_load(self) -> WaterConfiguration:
        if os.path.exists(self.config_file):
            return WaterConfiguration.parse_file(self.config_file)
        return WaterConfiguration.construct()

    def _config_save(self):
        with open(self.config_file, 'w+', encoding='UTF-8') as c:
            c.write(json.dumps({
                'config_dir': self.config_dir,
                'output': self.output.name
            }, indent=2))
