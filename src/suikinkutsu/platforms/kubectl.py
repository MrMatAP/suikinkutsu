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

import typing
import json
import shutil

from .platform import Platform
from suikinkutsu.config import Configuration
from suikinkutsu import MurkyWaterException
from suikinkutsu.blueprints import BlueprintInstance, Blueprint


class Kubectl(Platform):
    """
    Kubernetes platform
    """

    def __init__(self, config: Configuration, name: typing.Optional[str] = 'kubernetes'):
        super().__init__(config)
        self._name = name
        self._description = 'Kubernetes Context'
        self._executable_name = 'kubectl'
        self._executable = shutil.which(self._executable_name)
        self._available = None

    @classmethod
    def factory(cls, config: Configuration) -> typing.Dict[str, 'Platform']:
        self = cls(config)
        if not self._executable:
            #self.runtime.output.info(f'{self._name} executable not found. Platform is not available')
            self._available = False
            return {}
        try:
            kubeconfig = self.execute(['config', 'view', '-o', 'json'])
            config_json = json.loads(kubeconfig.stdout)
            contexts = config_json.get('contexts', [])
            kube_contexts = {}
            for context in contexts:
                context_name = context.get('name')
                kube_contexts[context_name] = cls(config, context_name)
            return kube_contexts
        except MurkyWaterException:
            #self.runtime.output.warning(f'{self._name} executable was found but is not available: {mwe.msg}')
            self._available = False

    def apply(self, blueprint: Blueprint):
        pass

    @property
    def executable_name(self) -> str:
        return self._executable_name

    @property
    def executable(self):
        return self._executable

    @property
    def available(self):
        if self._available is not None:
            return self._available
        if not self._executable:
            self._available = False
            return False
        try:
            self.execute(['version'])
            self._available = True
        except MurkyWaterException:
            self._available = False
        return self._available

    def instance_create(self, blueprint_instance: BlueprintInstance):
        pass

    def instance_list(self, blueprint: typing.Optional[Blueprint] = None) -> typing.List[BlueprintInstance]:
        # TODO
        return []

    def instance_show(self, name: str, blueprint: typing.Optional[Blueprint] = None):
        pass

    def instance_remove(self, name: str, blueprint: typing.Optional[Blueprint] = None):
        pass

