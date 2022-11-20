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
import pathlib
import json

import water.constants
import water.runtime


def test_runtime_defaults() -> None:
    """
    Test the defaults
    """
    r = water.runtime.Runtime()
    assert r.config_file == pathlib.Path(water.constants.DEFAULT_CONFIG_FILE)
    assert r.config_file_source == water.runtime.Source.DEFAULT
    assert r.config_dir == pathlib.Path(water.constants.DEFAULT_CONFIG_DIR)
    assert r.config_dir_source == water.runtime.Source.DEFAULT
    assert r.output.__class__.__name__ == water.constants.DEFAULT_OUTPUT_CLASS
    assert r.output_source == water.runtime.Source.DEFAULT
    assert r.recipe_file == pathlib.Path(water.constants.DEFAULT_RECIPE_FILE)
    assert r.recipe_file_source == water.runtime.Source.DEFAULT
    assert len(r.available_blueprints) > 0
    assert len(r.available_platforms) > 0


def test_runtime_with_configfile(tmp_path) -> None:
    """
    Test whether we can override the configuration file with an environment variable
    Args:
        tmp_path: A temporary directory
    """
    config_dir = tmp_path / "etc"
    config_dir.mkdir()
    config_file = tmp_path / ".water"
    config_file.write_text(json.dumps({
        'config_dir': str(config_dir)
    }))
    os.environ[water.constants.ENV_CONFIG_FILE] = str(config_file)

    r = water.runtime.Runtime()
    assert r.config_file == config_file
    assert r.config_file_source == water.runtime.Source.ENVIRONMENT
    assert r.config_dir == pathlib.Path(config_dir)
    assert r.config_dir_source == water.runtime.Source.CONFIGURATION
    assert r.recipe_file == pathlib.Path(water.constants.DEFAULT_RECIPE_FILE)
    assert r.recipe_file_source == water.runtime.Source.DEFAULT
    assert len(r.available_blueprints) > 0
    assert len(r.available_platforms) > 0
    del(os.environ[water.constants.ENV_CONFIG_FILE])
