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

from .output_base import WaterOutput, WaterDisplayable
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.columns import Columns
from rich.box import ROUNDED

console = Console()


class HumanWaterOutput(WaterOutput):
    """Output for human users"""

    name: str = 'DefaultOutput'

    def exception(self, ex: Exception) -> None:
        console.print_exception()

    def info(self, msg: str) -> None:
        console.print(msg)

    def warning(self, msg: str) -> None:
        console.print(f'[bold yellow]Warning:[/bold yellow] {msg}')

    def error(self, msg: str) -> None:
        console.print(f'[bold red]Error:[/bold red] {msg}')

    def displayable(self, displayable: WaterDisplayable):
        data = displayable.display_dict()
        table = Table(title='Test', box=ROUNDED)
        [table.add_column(column) for column in data.keys()]
        [table.add_row(row) for row in data.values()]
        console.print(table)

    def config(self, runtime):
        table = Table(title='Configuration', box=ROUNDED)
        table.add_column('Key')
        table.add_column('Value')
        table.add_column('Source')
        table.add_row('config_file', str(runtime.config_file), runtime.config_file_source.value)
        table.add_row('config_dir', str(runtime.config_dir), runtime.config_dir_source.value)
        table.add_row('output', runtime.output.name, runtime.output_source.value)
        table.add_row('platform', runtime.platform.name, runtime.platform_source.value)
        table.add_row('recipe_file', str(runtime.recipe_file), runtime.recipe_file_source.value)
        table.add_row('secrets_file', str(runtime.secrets_file), runtime.secrets_file_source.value)
        console.print(table)

    def platform_list(self, runtime):
        table = Table(title='Available Platforms', box=ROUNDED)
        table.add_column('Platform')
        table.add_column('Available')
        table.add_column('Description')
        [table.add_row(name,
                       str(cls.available()),
                       cls.description)
         for name, cls in runtime.available_platforms.items()]
        console.print(table)

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
            [depends_on_node.add(Columns([f'[bold]Blueprint:[/bold]', v], width=80)) for v in blueprint.depends_on]
        console.print(tree)

    def blueprint_list(self, runtime):
        table = Table(title='Available Blueprints', box=ROUNDED)
        table.add_column('Blueprint')
        table.add_column('Description')
        [table.add_row(name, bp.description) for name, bp in runtime.available_blueprints.items()]
        console.print(table)

    def __repr__(self):
        return 'HumanOutput()'

    def __str__(self):
        return 'Output for human users'
