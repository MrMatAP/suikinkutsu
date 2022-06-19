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
import abc
from typing import Dict, Optional
from pydantic import BaseModel
from rich.table import Table
from rich.box import ROUNDED
from water import console, LABEL_BLUEPRINT


class BlueprintSchema(BaseModel):
    kind: str
    image: Optional[str]
    labels: Optional[Dict[str, str]]
    volumes: Optional[Dict[str, str]]
    environment: Optional[Dict[str, str]]
    ports: Optional[Dict[str, str]]


class Blueprint(abc.ABC):

    name: str = "base"
    kind: str = 'base'
    description: str = "An abstract base blueprint"
    image: str = ""
    volumes: Dict[str, str] = {}
    environment: Dict[str, str] = {}
    ports: Dict[str, str] = {}
    labels: Dict[str, str] = {}

    def __init__(self):
        self.labels[LABEL_BLUEPRINT] = self.__class__.name
        self.labels['org.mrmat.test'] = 'foo'

    @classmethod
    def cli(cls, parser):
        pass

    @classmethod
    def from_schema(cls, runtime, name, schema):
        instance = cls()
        instance.name = name
        instance.image = schema.image or instance.image
        return instance

    @classmethod
    def blueprint_list(cls, runtime, args: argparse.Namespace):
        table = Table(title='Available Blueprints', box=ROUNDED)
        table.add_column('Blueprint')
        table.add_column('Description')
        [table.add_row(name, bp.description) for name, bp in runtime.available_blueprints.items()]
        console.print(table)

    def create(self, runtime, args: argparse.Namespace):
        service = runtime.platform.service_create(blueprint=self)
        console.print(f'Service {self.name} of kind {self.kind} created')
        return service

    def list(self, runtime, args: argparse.Namespace):
        console.print(f'Listing services of kind {self.kind}')

    def remove(self, runtime, args: argparse.Namespace):
        runtime.platform.service_remove(blueprint=self)
        console.print(f'Service {self.name} of kind {self.kind} removed')
