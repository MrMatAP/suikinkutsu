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

from . import OutputEntry
from .output import Output


class YAMLWaterOutput(Output):
    """
    YAML output
    """
    name = 'yaml'

    def __init__(self, config) -> None:
        super().__init__(config)
        self._description = 'Output in YAML'

    def print(self, entry: OutputEntry) -> None:
        if isinstance(entry.msg, str):
            print(yaml.safe_dump(entry.__dict__()))
            return

        # TODO: We must reorder this
        d = entry.__dict__()
        d['msg'] = dict(zip(entry.columns, entry.msg))
        del d['columns']
        print(yaml.safe_dump(d))

    def exception(self, ex: Exception):
        ex_dict = self._exception_dict(ex)
        print(yaml.safe_dump(ex_dict))

    def info(self, msg: str):
        print(yaml.safe_dump({'INFO': msg}))

    def warning(self, msg: str):
        print(yaml.safe_dump({'WARNING': msg}))

    def error(self, msg: str):
        print(yaml.safe_dump({'ERROR': msg}))
