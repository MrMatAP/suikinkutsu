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

DEFAULT_CONFIG_FILE = os.path.expanduser(os.path.join('~', '.suikinkutsu'))
ENV_CONFIG_FILE = 'WATER_CONFIG_FILE'
CLI_CONFIG_FILE = 'override_config_file'

DEFAULT_CONFIG_DIR = os.path.expanduser(os.path.join('~', 'etc'))
ENV_CONFIG_DIR = 'WATER_CONFIG_DIR'
CLI_CONFIG_DIR = 'override_config_dir'

DEFAULT_OUTPUT = 'human'
ENV_OUTPUT = 'WATER_OUTPUT'
CLI_OUTPUT = 'override_output'

DEFAULT_PLATFORM = 'docker'
ENV_PLATFORM = 'WATER_PLATFORM'
CLI_PLATFORM = 'override_platform'

DEFAULT_RECIPE_FILE = os.path.join(os.path.abspath(os.path.curdir), 'Recipe')
ENV_RECIPE_FILE = 'WATER_RECIPE'
CLI_RECIPE_FILE = 'override_recipe_file'

ENV_SECRETS_FILE = 'WATER_SECRETS_FILE'
CLI_SECRETS_FILE = 'override_secrets_file'

LABEL_BLUEPRINT: str = 'org.mrmat.suikinkutsu.blueprint'
LABEL_CREATED_BY: str = 'org.mrmat.created-by'
