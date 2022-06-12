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

import json
from .output import Output


class JSONOutput(Output):
    name: str = 'json'

    def exception(self, ex: Exception):
        ex_dict = {
            'Exception': str(ex),
            'Type': type(ex)
        }
        print(json.dumps(ex_dict))

    def config(self, runtime):
        config_dict = {
            'config-file': runtime.config_file,
            'config-file-source': runtime.config_file_source,
            'config-dir': runtime.config_dir,
            'config-dir-source': runtime.config_dir_source,
            'output': runtime.output.name,
            'output-source': runtime.output_source
        }
        print(json.dumps(config_dict))

    def info(self, msg: str):
        print(json.dumps({'INFO': msg}))

    def warning(self, msg: str):
        print(json.dumps({'WARNING': msg}))

    def error(self, msg: str):
        print(json.dumps({'ERROR': msg}))
