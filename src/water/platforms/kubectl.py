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
import json
import shutil

from water import MurkyWaterException
from .platform import WaterPlatform
from water.blueprints import BlueprintInstance, Blueprint


class Kubectl(WaterPlatform):
    """
    Kubernetes platform
    """

    def __init__(self, runtime: 'Runtime', context: Optional[str] = None):
        super().__init__(runtime)
        self._name = context or 'kubectl'
        self._description = 'Kubernetes Context'
        self._executable_name = 'kubectl'
        self._executable = shutil.which(self._executable_name)
        self._available = None

    @classmethod
    def factory(cls, runtime: 'Runtime') -> Dict[str, 'WaterPlatform']:
        self = cls(runtime)
        if not self._executable:
            self.runtime.output.info(f'{self._name} executable not found. Platform is not available')
            self._available = False
            return {}
        try:
            config = self.execute(['config', 'view', '-o', 'json'])
            config_json = json.loads(config.stdout)
            contexts = config_json.get('contexts', [])
            kube_contexts = {}
            for context in contexts:
                context_name = context.get('name')
                kube_contexts[context_name] = cls(runtime, context_name)
            return kube_contexts
        except MurkyWaterException as mwe:
            self.runtime.output.warning(f'{self._name} executable was found but is not available: {mwe.msg}')
            self._available = False

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

    def instance_list(self, blueprint: Optional[Blueprint] = None) -> List[BlueprintInstance]:
        # TODO
        return []

    def instance_show(self, name: str, blueprint: Optional[Blueprint] = None):
        pass

    def instance_remove(self, name: str, blueprint: Optional[Blueprint] = None):
        pass

