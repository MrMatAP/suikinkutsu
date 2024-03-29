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

import dataclasses
import typing
import enum
import argparse

from suikinkutsu.behaviours import CommandLineAware


class OutputSeverity(enum.Enum):
    """
    Severity of the output to print
    """
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'

    def __str__(self):
        return self.value

    def __repr__(self):
        return f'OutputSeverity.{self.value}'


@dataclasses.dataclass
class OutputEntry:
    """
    A unit of output, allowing us to abstract away the method on how we output
    """
    msg: typing.Union[str, typing.List[typing.List[str]]]
    columns: typing.Optional[typing.List[str]] = dataclasses.field(default_factory=list)
    code: typing.Optional[int] = 200
    title: typing.Optional[str] = None
    severity: typing.Optional[OutputSeverity] = OutputSeverity.INFO

    def __dict__(self) -> typing.Dict:
        """
        Produce a dict from the content of this OutputEntry.

        This is a requirement for this class to be serializable as JSON and YAML. What is non-obvious is the generic
        method to make this work for classes. __dict__ itself is not one of the standard dunderscore methods in Python.
        There is mention of __iter__ and __next__ to implement standard JSON/YAML serialisability but I couldn't get
        that to work. It would be nice if we could, because it does look quite ugly to call __dict__() explicitly.
        Returns:
            a dictionary
        """
        d = {'msg': self.msg,
             'code': self.code,
             'severity': str(self.severity),
             'title': self.title,
             'columns': self.columns}
        return d


class Output(CommandLineAware):
    """
    Output base class
    """

    name = 'base'

    def __init__(self, config) -> None:
        self._config = config
        self._description = 'Abstract base for an output'

    def cli_prepare(self, parser, subparsers) -> None:
        output_parser = subparsers.add_parser(name='output', help='Output Commands')
        output_subparser = output_parser.add_subparsers()
        output_list_parser = output_subparser.add_parser('list', help='List Outputs')
        output_list_parser.set_defaults(cmd=self.output_list)

    # pylint: disable=unused-argument
    def output_list(self, runtime, args: argparse.Namespace) -> int:
        output = OutputEntry(title='Outputs',
                             columns=['Name', 'Description'],
                             msg=[[name, output.description] for name, output in runtime.outputs.items()])
        runtime.output.print(output)
        return 0

    @property
    def description(self) -> str:
        return self._description

    def print(self, entry: OutputEntry) -> None:
        """
        Display a log entry in the chosen output format
        Args:
            entry: An output entry
        """
        pass

    def exception(self, ex: Exception) -> None:
        """
        Display an exception
        Args:
            ex: The exception to display
        """
        pass

    def info(self, msg: str) -> None:
        """
        Display an informational message
        Args:
            msg: The informational message to display
        """
        pass

    def warning(self, msg: str) -> None:
        """
        Display a warning message
        Args:
            msg: The warning message to display
        """
        pass

    def error(self, msg: str) -> None:
        """
        Display an error message
        Args:
            msg: The error message to display
        """
        pass

    @staticmethod
    def _exception_dict(ex: Exception):
        return {
            'Exception': str(ex),
            'Type': type(ex)
        }

    @staticmethod
    def _config_dict(runtime):
        return {
            'config-file': str(runtime.config_file),
            'config-file-source': runtime.config_file_source.value,
            'config-dir': str(runtime.config_dir),
            'config-dir-source': runtime.config_dir_source.value,
            'output': runtime.output.name,
            'output-source': runtime.output_source.value,
            'platform': runtime.platform.name,
            'platform-source': runtime.platform_source.value,
            'recipe-file': str(runtime.recipe_file),
            'recipe-file-source': runtime.recipe_file_source.value
        }

    def __repr__(self):
        return 'Output()'

    def __str__(self):
        return 'Abstract base class for output'
