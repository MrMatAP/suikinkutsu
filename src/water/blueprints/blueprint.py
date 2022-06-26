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

from argparse import Namespace
import abc
from typing import Optional

from water.schema import BlueprintSchema
from water.constants import LABEL_BLUEPRINT


class Blueprint(abc.ABC):
    kind: str = 'base'
    description: str = "An abstract base blueprint"
    _defaults: BlueprintSchema = BlueprintSchema(
        kind='base',
        name='base',
        image='',
        volumes={},
        environment={},
        ports={},
        labels={LABEL_BLUEPRINT: 'Blueprint'},
        depends_on=[]
    )

    def __init__(self, name: Optional[str] = None, schema: Optional[BlueprintSchema] = None):
        self._kind = 'base'
        self._schema = schema or self._defaults
        self._schema.name = name or self._defaults.name
        if schema:
            self._schema.merge_defaults(self._defaults)

    @property
    def name(self):
        return self._schema.name

    @property
    def platform(self):
        return self._schema.platform

    @property
    def image(self):
        return self._schema.image

    @property
    def labels(self):
        return self._schema.labels

    @property
    def volumes(self):
        return self._schema.volumes

    @property
    def environment(self):
        return self._schema.environment

    @property
    def ports(self):
        return self._schema.ports

    @property
    def depends_on(self):
        return self._schema.depends_on

    @classmethod
    def cli_prepare(cls, parser):
        pass

    @classmethod
    def cli_assess(cls, args: Namespace):
        pass
