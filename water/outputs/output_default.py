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

from water import console
from water.outputs.output import Output
from rich.tree import Tree
from rich.table import Table
from rich.box import ROUNDED


class DefaultOutput(Output):

    name: str = 'default'

    def exception(self, ex: Exception):
        console.print_exception()

    def config(self, runtime):
        table = Table(title='Configuration', box=ROUNDED)
        table.add_column('Key')
        table.add_column('Value')
        table.add_column('Source')
        table.add_row('config_file', runtime.config_file, runtime.config_file_source)
        table.add_row('config_dir', runtime.config_dir, runtime.config_dir_source)
        table.add_row('output', runtime.output.name, runtime.output_source)
        console.print(table)

    def info(self, msg: str):
        console.print(msg)

    def warning(self, msg: str):
        console.print(f'[bold yellow]Warning:[/bold yellow] {msg}')

    def error(self, msg: str):
        console.print(f'[bold red]Error:[/bold red] {msg}')


