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

import os
import json
import argparse
import pytest

import conftest
import suikinkutsu.constants
from suikinkutsu.config import WaterConfig, Source, ConfigurableItem


def assert_configurable_item(item: ConfigurableItem, value: str, source: Source):
    assert value == item.value
    assert source == item.source


def test_default_config(config_env):
    config = suikinkutsu.config.WaterConfig()
    assert_configurable_item(config.config_file, suikinkutsu.constants.DEFAULT_CONFIG_FILE, Source.DEFAULT)
    assert_configurable_item(config.config_dir, suikinkutsu.constants.DEFAULT_CONFIG_DIR, Source.DEFAULT)
    assert_configurable_item(config.recipe_file, suikinkutsu.constants.DEFAULT_RECIPE_FILE, Source.DEFAULT)


@pytest.mark.parametrize('env_override,cli_override,config_item',
                         conftest.config_overrides,
                         ids=conftest.config_override_ids)
def test_env_overrides_default(config_env, env_override: str, cli_override: str, config_item: str):
    os.environ[env_override] = 'override'
    config = suikinkutsu.config.WaterConfig()
    assert_configurable_item(getattr(config, config_item), 'override', Source.ENVIRONMENT)


@pytest.mark.parametrize('env_override,cli_override,config_item',
                         conftest.config_overrides,
                         ids=conftest.config_override_ids)
def test_cli_overrides_default(config_env, env_override: str, cli_override: str, config_item: str, cli_arg_namespace: argparse.Namespace):
    setattr(cli_arg_namespace, cli_override, 'override')
    config = suikinkutsu.config.WaterConfig()
    config.cli_assess(cli_arg_namespace)
    assert_configurable_item(getattr(config, config_item), 'override', Source.CLI)


def test_cli_overrides_env(config_env, cli_arg_namespace: argparse.Namespace):
    os.environ[suikinkutsu.constants.ENV_CONFIG_DIR] = 'env_override'
    setattr(cli_arg_namespace, suikinkutsu.constants.CLI_CONFIG_DIR, 'cli_override')
    config = suikinkutsu.config.WaterConfig()
    config.cli_assess(cli_arg_namespace)
    assert_configurable_item(config.config_dir, 'cli_override', Source.CLI)


def test_config_file_overrides_default(config_env, tmp_path, cli_arg_namespace: argparse.Namespace):
    config_file = tmp_path / 'custom-config.json'
    config_file.write_text(json.dumps({
        'config_dir': 'file-override'
    }))
    os.environ[suikinkutsu.constants.ENV_CONFIG_FILE] = str(config_file)
    config = suikinkutsu.config.WaterConfig()
    config.cli_assess(cli_arg_namespace)
    assert_configurable_item(config.config_file, str(config_file), Source.ENVIRONMENT)
    assert_configurable_item(config.config_dir, 'file-override', Source.CONFIGURATION)
    assert config.recipe_file.source == Source.DEFAULT
    assert config.secrets_file.source == Source.DEFAULT
