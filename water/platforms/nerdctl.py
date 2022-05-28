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

from typing import List
import shutil
import json
from rich.table import Table

from water import MurkyWaterException, console, Volume, Instance
from water.platforms import Platform
from water.blueprints import Blueprint


class Nerdctl(Platform):
    executable_name = 'nerdctl'

    def __init__(self):
        self.executable = shutil.which(self.executable_name)

    def volume_create(self, name: str) -> Volume:
        self.execute(['volume', 'create',
                      '--label', 'org.mrmat.created-by=water',
                      name])
        console.print(f'Volume {name} successfully created')

    def volume_list(self) -> List[Volume]:
        result = self.execute(['volume', 'ls', '--format', '{{ json . }}'])
        raw_volumes = [e for e in result.stdout.split('\n') if e.startswith('{')]
        result = []
        for raw_volume in raw_volumes:
            json_volume = json.loads(raw_volume)
            result.append(Volume(name=json_volume['Name'],
                                 scope=json_volume['Scope'],
                                 driver=json_volume['Driver'],
                                 labels=json_volume['Labels'],
                                 mountpoint=json_volume['Mountpoint']))
        return result

    def volume_remove(self, name: str):
        self.execute(['volume', 'rm', name])
        console.print(f'Volume {name} successfully removed')

    def instance_create(self, blueprint: Blueprint) -> Instance:
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
        cmd.append(blueprint.container)
        self.execute(cmd)
        console.print(f'Instance {blueprint.name} successfully created')

    def instance_list(self) -> List[Instance]:
        result = self.execute(['container', 'ls', '--format', '{{ json . }}'])
        raw_instances = [json.loads(e) for e in result.stdout.split('\n') if e.startswith('{')]
        for raw_instance in raw_instances:
            result = self.execute(['container', 'inspect', raw_instance['ID']])
            raw_instance['inspection'] = json.loads(result.stdout)
        return [Instance(i) for i in raw_instances]

        #table = Table(title='Instances')
        # for column in ['Name', 'Scope', 'Driver', 'Labels', 'Mountpoint']:
        #     table.add_column(column)
        # for vol in volumes:
        #     row = json.loads(vol)
        #     table.add_row(row['Name'], row['Scope'], row['Driver'], row['Labels'], row['Mountpoint'])
        # console.print(table)

    def instance_remove(self, blueprint: Blueprint):
        result = self.execute(['container', 'stop', blueprint.name])
        result = self.execute(['container', 'rm', blueprint.name])
