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
import os

import pytest
import suikinkutsu.constants

config_overrides = [(suikinkutsu.constants.ENV_CONFIG_FILE, suikinkutsu.constants.CLI_CONFIG_FILE, 'config_file'),
                    (suikinkutsu.constants.ENV_CONFIG_DIR, suikinkutsu.constants.CLI_CONFIG_DIR, 'config_dir'),
                    (suikinkutsu.constants.ENV_RECIPE_FILE, suikinkutsu.constants.CLI_RECIPE_FILE, 'recipe_file'),
                    (suikinkutsu.constants.ENV_SECRETS_FILE, suikinkutsu.constants.CLI_SECRETS_FILE, 'secrets_file'),
                    (suikinkutsu.constants.ENV_OUTPUT, suikinkutsu.constants.CLI_OUTPUT, 'output'),
                    (suikinkutsu.constants.ENV_PLATFORM, suikinkutsu.constants.CLI_PLATFORM, 'platform')]
config_override_ids = [f'override-{entry[2]}' for entry in config_overrides]


@pytest.fixture
def cli_arg_namespace() -> argparse.Namespace:
    cli_args = {arg[1]: None for arg in config_overrides}
    return argparse.Namespace(**cli_args)


@pytest.fixture
def config_env(tmp_path):
    env_vars = [entry[0] for entry in config_overrides]
    for env_var in env_vars:
        if env_var in os.environ:
            del os.environ[env_var]
    yield tmp_path
    for env_var in env_vars:
        if env_var in os.environ:
            del os.environ[env_var]
