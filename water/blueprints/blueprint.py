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
from typing import Dict, List
import configparser


class Blueprint(abc.ABC):
    name: str
    container: str
    volumes: Dict[str, str]
    environment: Dict[str, str]
    ports: Dict[str, str]
    labels: Dict[str, str]

    def __init__(self, name: str):
        self.name = name

    @classmethod
    @abc.abstractmethod
    def parser(cls, parser):
        pass

    @classmethod
    @abc.abstractmethod
    def create(cls,
               platform: 'water.platforms.Platform',
               config: configparser.ConfigParser,
               args: argparse.Namespace) -> 'water.models.Instance':
        pass

    @classmethod
    @abc.abstractmethod
    def list(cls,
             platform: 'water.platforms.Platform',
             config: configparser.ConfigParser,
             args: argparse.Namespace) -> List['water.models.Instance']:
        pass

    @classmethod
    @abc.abstractmethod
    def remove(cls,
               platform: 'water.platforms.Platform',
               config: configparser.ConfigParser,
               args: argparse.Namespace) -> 'water.models.Instance':
        pass
