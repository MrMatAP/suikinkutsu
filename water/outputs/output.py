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

import abc


class Output(abc.ABC):
    name: str = 'BasePlatform'

    @abc.abstractmethod
    def exception(self, ex: Exception):
        pass

    @abc.abstractmethod
    def info(self, msg: str):
        pass

    @abc.abstractmethod
    def warning(self, msg: str):
        pass

    @abc.abstractmethod
    def error(self, msg: str):
        pass

    @abc.abstractmethod
    def config(self, runtime):
        pass

    @abc.abstractmethod
    def platform_list(self, runtime):
        pass

    @abc.abstractmethod
    def cook_show(self, runtime):
        pass

    @staticmethod
    def _exception_dict(ex: Exception):
        return {
            'Exception': str(ex),
            'Type': type(ex)
        }

    @staticmethod
    def _config_dict(runtime):
        return {
            'config-file': str(runtime.config_file),
            'config-file-source': runtime.config_file_source.value,
            'config-dir': str(runtime.config_dir),
            'config-dir-source': runtime.config_dir_source.value,
            'output': runtime.output.name,
            'output-source': runtime.output_source.value,
            'platform': runtime.platform.name,
            'platform-source': runtime.platform_source.value,
            'recipe-file': str(runtime.recipe_file),
            'recipe-file-source': runtime.recipe_file_source.value
        }

    @staticmethod
    def _platform_list(runtime):
        return [
            {
                'name': platform.name,
                'available': platform.available(),
                'description': platform.description
            }
            for platform in runtime.available_platforms]
