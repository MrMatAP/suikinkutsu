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

from typing import List
import json

from .docker import Docker
from water.instances import Instance


class Nerdctl(Docker):
    name: str = 'nerdctl'
    description: str = 'nerdctl is a modern CLI for a containerd implementation, brought to you ' \
                       'via Rancher Desktop (for example).'
    executable_name = 'nerdctl'

    def instance_list(self) -> List[Instance]:
        result = self._execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            return []
        result = self._execute(['container', 'inspect', '--mode=native', str.join(' ', container_ids)])
        raw_instances = json.loads(result.stdout)
        instances: List[Instance] = []
        for raw_instance in raw_instances:
            if 'Labels' not in raw_instance or 'org.mrmat.created-by' not in raw_instance['Labels']:
                continue
            instance = Instance(id=raw_instance['ID'],
                                name=raw_instance['Labels']['nerdctl/name'],
                                platform=self,
                                blueprint=raw_instance['Labels']['org.mrmat.water.blueprint'],
                                running=raw_instance['Process']['Status']['Status'] == 'running')
            instances.append(instance)
        return instances
