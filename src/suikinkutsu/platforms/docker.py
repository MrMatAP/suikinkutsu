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

import sys
import typing
import json
import shutil

from suikinkutsu.exceptions import MurkyWaterException, UnparseableInstanceException
from .platform import Platform
from suikinkutsu.models import Instance, PortBinding, VolumeBinding
from suikinkutsu.config import Configuration
from suikinkutsu.blueprints import Blueprint
from suikinkutsu.constants import LABEL_BLUEPRINT, LABEL_CREATED_BY


class Docker(Platform):
    """
    Docker platform
    """

    def __init__(self, config: Configuration):
        super().__init__(config)
        self._name = 'docker'
        self._description = 'Docker is the classic containerisation platform'

        self._executable_name = 'docker'
        self._executable = shutil.which(self._executable_name)
        self._available = None

    def apply(self, blueprint: Blueprint) -> Instance:
        cmd = ['container', 'run', '-d', '--name', blueprint.name]
        cmd.extend(['--label', f'{LABEL_CREATED_BY}=suikinkutsu'])
        cmd.extend(['--label', f'{LABEL_BLUEPRINT}={blueprint.__class__.__name__}'])
        for key, value in blueprint.environment.items():
            cmd.extend(['-e', f'{key}={value}'])
        for vol in blueprint.volume_bindings:
            # TODO: ro/rw
            cmd.extend(['--mount', f'type=volume,source={vol.name},destination={vol.mount_point}'])
        for port_binding in blueprint.port_bindings:
            cmd.extend(['-p', port_binding.to_mapping()])
        cmd.extend(['--hostname', blueprint.name])
        if len(blueprint.depends_on) > 0:
            cmd.extend(['--link', ','.join(blueprint.depends_on)])
        cmd.append(f'{blueprint.image}:{blueprint.version}')
        result = self.execute(cmd)
        instance = Instance(instance_id=result.stdout.strip('\n'),
                            name=blueprint.name,
                            running=True)
        instance.blueprint = blueprint
        instance.port_bindings = blueprint.port_bindings
        instance.volume_bindings = blueprint.volume_bindings
        return instance

    def instances(self) -> typing.List[Instance]:
        if not self.available:
            return []
        result = self.execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            return []
        cmd = ['container', 'inspect']
        cmd.extend(container_ids)
        result = self.execute(cmd)
        raw_instances = json.loads(result.stdout)
        filtered_instances = [i for i in raw_instances if i.get('Config', {}).get('Labels', {}).get(LABEL_CREATED_BY)]
        instances = []
        for i in filtered_instances:
            instance = Instance(instance_id=i['Id'],
                                name=i.get('Name', 'Unknown').strip('/'),
                                running=i.get('State', {}).get('Running'))
            instance_blueprint = i.get('Config', {}).get('Labels', {}).get(LABEL_BLUEPRINT, 'Unknown')
            try:
                blueprint_clz = getattr(sys.modules['suikinkutsu.blueprints'], instance_blueprint)
                instance.blueprint = blueprint_clz()
            except AttributeError as ae:
                raise UnparseableInstanceException(code=500, msg=f'Unable to find corresponding blueprint for '
                                                                 f'"{instance_blueprint}') from ae
            instance.port_bindings = [PortBinding.from_mapping(c, h) for c, h in
                                      i.get('NetworkSettings', {}).get('Ports', {}).items()]
            instance.volume_bindings = [VolumeBinding(mount['Name'], mount['Destination']) for mount in
                                        i.get('Mounts', [])]
            instances.append(instance)
        return instances

    def instance_show(self, name: str, blueprint: typing.Optional[Blueprint] = None):
        # result = self.execute(['container', 'inspect', blueprint.name])
        pass

    def instance_remove(self, instance: Instance):
        self.execute(['container', 'stop', instance.name])
        self.execute(['container', 'rm', instance.name])
        for vol in instance.volume_bindings:
            self.execute(['volume', 'rm', vol.name])

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
            self.execute(['container', 'ps', '-q'])
            self._available = True
        except MurkyWaterException:
            self._available = False
        return self._available
