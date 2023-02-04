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
#  FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from typing import Optional, Dict, List
from pydantic import BaseModel


class BlueprintSchema(BaseModel):
    """
    A blueprint schema
    """
    platform: Optional[str]
    image: Optional[str]
    labels: Optional[Dict[str, str]]
    volumes: Optional[Dict[str, str]]
    environment: Optional[Dict[str, str]]
    ports: Optional[Dict[str, str]]
    depends_on: Optional[List[str]]

    # TODO: This should be optimised
    def merge_defaults(self, defaults: 'BlueprintSchema'):
        self.platform = self.platform or defaults.platform
        self.image = self.image or defaults.image
        self.labels = self.labels or defaults.labels
        for k, v in defaults.labels.items():
            if k not in self.labels:
                self.labels[k] = v
        self.volumes = self.volumes or defaults.volumes
        for k, v in defaults.volumes.items():
            if k not in self.volumes:
                self.volumes[k] = v
        self.environment = self.environment or defaults.environment
        for k, v in defaults.environment.items():
            if k not in self.environment:
                self.environment[k] = v
        self.ports = self.ports or defaults.ports
        for k, v in defaults.ports.items():
            if k not in self.ports:
                self.ports[k] = v
        self.depends_on = self.depends_on or defaults.depends_on


class RecipeSchema(BaseModel):
    blueprints: Dict[str, BlueprintSchema]


