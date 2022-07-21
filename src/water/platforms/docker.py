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
from typing import List, Dict, Optional
import datetime
import json
from pydantic import BaseModel, Field

from water import MurkyWaterException
from water.platforms.platform import Platform
from water.schema import InstanceSchema


class Docker(Platform):

    name: str = 'docker'
    description: str = 'Docker is the classic containerisation platform'
    executable_name = 'docker'

    def __init__(self):
        super().__init__()
        try:
            self._execute(['ps', '-q'])
        except MurkyWaterException:
            self._available = False

    def blueprint_create(self, blueprint):
        pass

    def blueprint_list(self, blueprint):
        pass

    def blueprint_show(self, blueprint):
        pass

    def blueprint_remove(self, blueprint):
        pass

    def volume_create(self, name: str):
        self._execute(['volume', 'create',
                       '--label', 'org.mrmat.created-by=water',
                       name])
        info = self._execute(['volume', 'inspect', name])

        #console.print(f'Volume {name} successfully created')

    def volume_list(self):
        result = self._execute(['volume', 'ls', '--format', '{{ json . }}'])
        raw_volumes = [e for e in result.stdout.split('\n') if e.startswith('{')]
        result = []
        # for raw_volume in raw_volumes:
        #     json_volume = json.loads(raw_volume)
        #     result.append(water.schema.Volume(name=json_volume['Name'],
        #                                       scope=json_volume['Scope'],
        #                                       driver=json_volume['Driver'],
        #                                       labels=json_volume['Labels'],
        #                                       mountpoint=json_volume['Mountpoint']))
        return result

    def volume_show(self):
        pass

    def volume_remove(self, name: str):
        self._execute(['volume', 'rm', name])
        #console.print(f'Volume {name} successfully removed')

    def service_create(self, blueprint):
        cmd = ['container', 'run', '-d', '--name', blueprint.name]
        for label, value in blueprint.labels.items():
            cmd.extend(['--label', f'{label}={value}'])
        for key, value in blueprint.environment.items():
            cmd.extend(['-e', f'{key}={value}'])
        for src, dst in blueprint.volumes.items():
            # TODO: ro/rw
            cmd.extend(['--mount', f'type=volume,source={src},destination={dst}'])
        for host, container in blueprint.ports.items():
            cmd.extend(['-p', f'{host}:{container}'])
        cmd.append(blueprint.image)
        self._execute(cmd)

    def service_list(self, kind: Optional[str] = None) -> List[InstanceSchema]:
        result = self._execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            return []
        result = self._execute(['container', 'inspect', str.join(' ', container_ids)])
        raw_instances = json.loads(result.stdout)
        instances = []
        for raw_instance in raw_instances:
            instances.append(InstanceSchema(id=raw_instance['Id'], state=raw_instance['State']['Status']))
        return instances
        #instances = parse_raw_as(List[DockerInspectionSchema], result.stdout)
        pass

        # result = self._execute(['container', 'ls', '--format', '{{ json . }}'])
        # raw_instances = [json.loads(e) for e in result.stdout.split('\n') if e.startswith('{')]
        # for raw_instance in raw_instances:
        #     result = self._execute(['container', 'inspect', raw_instance['ID']])
        #     raw_instance['inspection'] = json.loads(result.stdout)
        #return [water.models.Instance(i) for i in raw_instances]

    def service_show(self, blueprint):
        result = self._execute(['container', 'inspect', blueprint.name])

    def service_remove(self, blueprint):
        self._execute(['container', 'stop', blueprint.name])
        self._execute(['container', 'rm', blueprint.name])
        [self._execute(['volume', 'rm', vol]) for vol in blueprint.volumes]
