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

from typing import Optional, List
import json
import shutil

from water import MurkyWaterException
from .platform import WaterPlatform
from water.blueprints import Blueprint, BlueprintInstance, BlueprintVolume
from water.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Docker(WaterPlatform):
    """
    Docker platform
    """

    def __init__(self, runtime: 'Runtime'):
        super().__init__(runtime)
        self._name = 'docker'
        self._description = 'Docker is the classic containerisation platform'
        self._executable_name = 'docker'
        self._executable = shutil.which(self._executable_name)
        self._available = None

    @property
    def available(self):
        if self._available is not None:
            return self._available
        if not self._executable:
            self._available = False
            return False
        try:
            self.execute(['container', 'ps', '-q'])
            self._available = True
        except MurkyWaterException:
            self._available = False
        return self._available

    def instance_create(self, blueprint_instance: BlueprintInstance):
        cmd = ['container', 'run', '-d', '--name', blueprint_instance.name]
        for label, value in blueprint_instance.blueprint.labels.items():
            cmd.extend(['--label', f'{label}={value}'])
        for key, value in blueprint_instance.blueprint.environment.items():
            cmd.extend(['-e', f'{key}={value}'])
        for src, dst in blueprint_instance.blueprint.volumes.items():
            # TODO: ro/rw
            cmd.extend(['--mount', f'type=volume,source={src},destination={dst}'])
        for host, container in blueprint_instance.blueprint.ports.items():
            cmd.extend(['-p', f'{host}:{container}'])
        cmd.extend(['--hostname', blueprint_instance.name])
        if len(blueprint_instance.blueprint.depends_on) > 0:
            cmd.extend(['--link', ','.join(blueprint_instance.blueprint.depends_on)])
        cmd.append(blueprint_instance.blueprint.image)
        result = self.execute(cmd)
        blueprint_instance.id = result.stdout.strip()
        blueprint_instance.running = True

    def instance_list(self, blueprint: Optional[Blueprint] = None) -> List[BlueprintInstance]:
        platform_instances: List[BlueprintInstance] = []
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

    def instance_show(self, name: str, blueprint: Optional[Blueprint] = None):
        # result = self.execute(['container', 'inspect', blueprint.name])
        pass

    def instance_remove(self, blueprint_instance: BlueprintInstance):
        self.execute(['container', 'stop', blueprint_instance.name])
        self.execute(['container', 'rm', blueprint_instance.name])
        [self.execute(['volume', 'rm', vol.name]) for vol in blueprint_instance.volumes]
