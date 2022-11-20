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

from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.columns import Columns
from rich.box import ROUNDED

from .output import Output, OutputEntry, OutputSeverity


class HumanWaterOutput(Output):
    """
    Output for humans
    """

    name = 'human'

    def __init__(self, runtime = None):
        super().__init__()
        self._console = Console()

    def print(self, entry: OutputEntry):
        if type(entry.msg) == str:
            self._console.print(HumanWaterOutput._severity(entry.severity, f'* [{entry.code}] {entry.msg}'))
            return

        table = Table(title=f'[{entry.code}] {entry.title}' or None,
                      box=ROUNDED)
        for col in (entry.columns or []):
            table.add_column(col)
        for row in (entry.msg or []):
            table.add_row(*row)
        self._console.print(table)

    @staticmethod
    def _severity(severity: OutputSeverity, msg: str):
        match severity:
            case None: return msg
            case OutputSeverity.DEBUG: return f'[bold yellow]{msg}[/bold yellow]'
            case OutputSeverity.WARNING: return f'[bold orange]{msg}[/bold orange]'
            case OutputSeverity.ERROR: return f'[bold red]{msg}[/bold red]'
        return msg

    def exception(self, ex: Exception) -> None:
        self._console.print_exception()

    def info(self, msg: str) -> None:
        self._console.print(msg)

    def warning(self, msg: str) -> None:
        self._console.print(f'[bold yellow]Warning:[/bold yellow] {msg}')

    def error(self, msg: str) -> None:
        self._console.print(f'[bold red]Error:[/bold red] {msg}')

    def cook_show(self, runtime):
        tree = Tree('Recipe')
        for blueprint in runtime.recipe.blueprints.values():
            node = tree.add(blueprint.name)
            node.add(Columns(['[bold]Kind:[/bold]', blueprint.kind], width=80))
            # node.add(Columns(['[bold]Platform:[/bold]'], blueprint.platform))
            node.add(Columns(['[bold]Image:[/bold]', blueprint.image], width=80))

            labels_node = node.add('[bold]Labels:[/bold]')
            [labels_node.add(Columns([f'[bold]{k}:[/bold]', v], width=80)) for k, v in blueprint.labels.items()]

            volumes_node = node.add('[bold]Volumes:[/bold]')
            [volumes_node.add(Columns([f'[bold]{k}:[/bold]', v], width=80)) for k, v in blueprint.volumes.items()]

            env_node = node.add('[bold]Environment:[/bold]')
            [env_node.add(Columns([f'[bold]{k}:[/bold]', v], width=80)) for k, v in blueprint.environment.items()]

            ports_node = node.add('[bold]Ports:[/bold]')
            [ports_node.add(Columns([f'[bold]{k}:[/bold]', v], width=80)) for k, v in blueprint.ports.items()]

            depends_on_node = node.add('[bold]Depends on:[/bold]')
            [depends_on_node.add(Columns(['[bold]Blueprint:[/bold]', v], width=80)) for v in blueprint.depends_on]
        self._console.print(tree)

    def __repr__(self):
        return 'HumanOutput()'

    def __str__(self):
        return 'Output for human users'
