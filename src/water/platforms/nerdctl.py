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

from typing import List, Optional
import json
import shutil

from .docker import Docker
from water.blueprints import Blueprint, BlueprintInstance
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Nerdctl(Docker):
    """
    Nerdctl platform as a client for containerd, such as by Rancher Desktop
    """

    def __init__(self, runtime: 'Runtime'):
        super().__init__(runtime)
        self._name = 'nerdctl'
        self._description = 'nerdctl is a modern CLI for a containerd implementation, brought to you via ' \
                            'Rancher Desktop (for example).'
        self._executable_name = 'nerdctl'
        self._executable = shutil.which(self._executable_name)
        self._available = False

    def instance_list(self, blueprint: Optional[Blueprint] = None) -> List[BlueprintInstance]:
        if not self.available:
            return []
        result = self.execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            return []
        cmd = ['container', 'inspect', '--mode=native']
        cmd.extend(container_ids)
        result = self.execute(cmd)
        raw_instances = json.loads(result.stdout)
        instances: List[BlueprintInstance] = []
        for raw_instance in raw_instances:
            if not raw_instance.get('Labels', {}).get(LABEL_CREATED_BY):
                continue
            blueprint_label = raw_instance.get('Labels', {}).get(LABEL_BLUEPRINT)
            status_label = raw_instance.get('Process', {}).get('Status', {}).get('Status')

            instance = BlueprintInstance(name=raw_instance.get('Labels', {}).get('nerdctl/name', 'Unknown'),
                                         platform=self,
                                         blueprint=self.runtime.blueprints.get(blueprint_label))
            instance.id = raw_instance['ID']
            instance.running = False if status_label is None else status_label == 'running'
            instances.append(instance)
        return instances
