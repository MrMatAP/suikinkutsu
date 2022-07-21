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

import yaml

from . import WaterDisplayable
from .output_base import WaterOutput


class YAMLWaterOutput(WaterOutput):
    name: str = 'yaml'

    def exception(self, ex: Exception):
        ex_dict = self._exception_dict(ex)
        print(yaml.safe_dump(ex_dict))

    def info(self, msg: str):
        print(yaml.safe_dump({'INFO': msg}))

    def warning(self, msg: str):
        print(yaml.safe_dump({'WARNING': msg}))

    def error(self, msg: str):
        print(yaml.safe_dump({'ERROR': msg}))

    def displayable(self, displayable: WaterDisplayable):
        print('YAML')

    def config(self, runtime):
        config_dict = self._config_dict(runtime)
        print(yaml.safe_dump(config_dict))

    def platform_list(self, runtime):
        platforms = self._platform_list(runtime)
        print(yaml.safe_dump(platforms))

    def cook_show(self, runtime):
        pass

    def blueprint_list(self, runtime):
        pass
