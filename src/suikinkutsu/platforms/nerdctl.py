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
from suikinkutsu.exceptions import MurkyWaterException
from suikinkutsu.blueprints import Blueprint, BlueprintInstance, BlueprintVolume
from suikinkutsu.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Nerdctl(Platform):
    """
    Nerdctl platform as a client for containerd, such as by Rancher Desktop
    """

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._name = 'nerdctl'
        self._description = 'nerdctl is a modern CLI for a containerd implementation, brought to you via ' \
                            'Rancher Desktop (for example).'

        self._executable_name = 'nerdctl'
        self._executable = shutil.which(self._executable_name)
        self._available = None

    def instances(self):
        result = self.execute(['container', 'ls', '-q'])
        return result

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
            self.execute(['container', 'ls', '-q'])
            self._available = True
        except MurkyWaterException:
            self._available = False
        return self._available

    #
    # nerdctl features a --mode=native which in some ways may be more detailed but for what we parse it's currently
    # easier to use the same method as Docker. Particularly the mounts are easier to parse.
    def instance_list(self, blueprint: typing.Optional[Blueprint] = None) -> typing.List[BlueprintInstance]:
        platform_instances: typing.List[BlueprintInstance] = []
        if not self.available:
            return platform_instances
        result = self.execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            return platform_instances
        cmd = ['container', 'inspect']
        cmd.extend(container_ids)
        result = self.execute(cmd)
        raw_instances = json.loads(result.stdout)
        for raw_instance in raw_instances:
            if not raw_instance.get('Config', {}).get('Labels', {}).get(LABEL_CREATED_BY):
                continue
            blueprint_label = raw_instance.get('Config', {}).get('Labels', {}).get(LABEL_BLUEPRINT)
            instance_name = raw_instance.get('Name', 'Unknown').strip('/')
            volumes = []
            for mount in raw_instance.get('Mounts', []):
                if mount['Type'] != 'volume':
                    continue
                volumes.append(BlueprintVolume(name=mount['Name'],
                                               destination=mount['Destination']))
            instance = BlueprintInstance(name=instance_name,
                                         platform=self,
                                         volumes=volumes,
                                         blueprint=self.runtime.blueprints.get(blueprint_label))
            instance.id = raw_instance['Id']
            instance.running = raw_instance.get('State', {}).get('Running')
            platform_instances.append(instance)
        return platform_instances

