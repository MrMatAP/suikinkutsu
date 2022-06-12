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
import typing
from typing import List, Dict, Optional
import datetime
import shutil
import json
from pydantic import BaseModel, Field, parse_raw_as

from water import console
from water.platforms.platform import Platform
import water.schema


class DockerInspectionStateSchema(BaseModel):
    status: str = Field(alias='Status')
    running: bool = Field(alias='Running')
    paused: bool = Field(alias='Paused')
    restarting: bool = Field(alias='Restarting')
    oom_killed: bool = Field(alias='OOMKilled')
    dead: bool = Field(alias='Dead')
    pid: int = Field(alias='Pid')
    exit_code: int = Field(alias='ExitCode')
    error: str = Field(alias='Error')
    started_at: datetime.datetime = Field(alias='StartedAt')
    finished_at: datetime.datetime = Field(alias='FinishedAt')


class DockerInspectionMountsSchema(BaseModel):
    type: str = Field(alias='Type')
    name: str = Field(alias='Name')
    source: str = Field(alias='Source')
    destination: str = Field(alias='Destination')
    driver: str = Field(alias='Driver')
    mode: str = Field(alias='Mode')
    read_write: bool = Field(alias='RW')
    propagation: str = Field(alias='Propagation')


class DockerInspectionConfigSchema(BaseModel):
    host_name: str = Field(alias='Hostname')
    domain_name: str = Field(alias='Domainname')
    user: str = Field(alias='User')
    attach_stdin: bool = Field(alias='AttachStdin')
    attach_stdout: bool = Field(alias='AttachStdout')
    attach_stderr: bool = Field(alias='AttachStderr')
    exposed_ports: Dict[str, typing.Any] = Field(alias='ExposedPorts')
    env: List[str] = Field(alias='Env')
    image: str = Field(alias='Image')
    volumes: Dict[str, typing.Any] = Field(alias='Volumes')
    labels: Dict[str, str] = Field(alias='Labels')


class DockerInspectionSchema(BaseModel):
    id: str = Field(alias='Id')
    created: datetime.datetime = Field(alias='Created')
    path: str = Field(alias='Path')
    args: List[str] = Field(alias='Args')
    state: DockerInspectionStateSchema = Field(alias='State')
    mounts: List[DockerInspectionMountsSchema] = Field(alias='Mounts')
    config: DockerInspectionConfigSchema = Field(alias='Config')

class Docker(Platform):
    name: str = 'docker'
    description: str = 'Docker is the classic containerisation platform'
    executable_name = 'docker'

    def available(self) -> bool:
        self.executable = shutil.which(self.executable_name)
        return True if self.executable else False

    def volume_create(self, name: str) -> water.schema.Volume:
        self._execute(['volume', 'create',
                       '--label', 'org.mrmat.created-by=water',
                       name])
        info = self._execute(['volume', 'inspect', name])

        console.print(f'Volume {name} successfully created')

    def volume_list(self) -> List['water.schema.volume.Volume']:
        result = self._execute(['volume', 'ls', '--format', '{{ json . }}'])
        raw_volumes = [e for e in result.stdout.split('\n') if e.startswith('{')]
        result = []
        for raw_volume in raw_volumes:
            json_volume = json.loads(raw_volume)
            result.append(water.schema.Volume(name=json_volume['Name'],
                                              scope=json_volume['Scope'],
                                              driver=json_volume['Driver'],
                                              labels=json_volume['Labels'],
                                              mountpoint=json_volume['Mountpoint']))
        return result

    def volume_remove(self, name: str):
        self._execute(['volume', 'rm', name])
        console.print(f'Volume {name} successfully removed')

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

    def service_list(self, name: Optional[str] = None) -> List['water.schema.Instance']:
        result = self._execute(['container', 'ls', '--all', '--quiet'])
        container_ids = [container_id for container_id in result.stdout.split('\n') if container_id != '']
        if len(container_ids) == 0:
            console.print('There are no containers defined on this platform')
            return None
        result = self._execute(['container', 'inspect', str.join(' ', container_ids)])
        instances = parse_raw_as(List[DockerInspectionSchema], result.stdout)
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
