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

from typing import Optional, List, Dict
from pydantic import BaseModel


class Blueprint(BaseModel):
    kind: str
    container: Optional[str]
    labels: Optional[Dict[str, str]]
    volumes: Optional[Dict[str, str]]
    environment: Optional[Dict[str, str]]
    ports: Optional[Dict[str, str]]

    def merge_defaults(self, defaults: 'Blueprint'):
        container = self.container or defaults.container
        labels = self.labels or defaults.labels
        volumes = self.volumes or defaults.labels
        environment = self.environment or defaults.environment
        ports = self.ports or defaults.ports


class Recipe(BaseModel):
    blueprints: Dict[str, Blueprint]
