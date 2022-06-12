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

import os
import yaml
from argparse import Namespace
from typing import List
from water import console
from water.exceptions import MurkyWaterException
from water.blueprints import Blueprint, RecipeSchema


class Recipe:
    blueprints: List[Blueprint] = []

    def __init__(self, runtime, args: Namespace):
        if not hasattr(args, 'recipe'):
            return
        if not os.path.exists(args.recipe):
            raise MurkyWaterException(msg=f'There is no recipe at {args.recipe}')
        try:
            with open(args.recipe, 'r', encoding='UTF-8') as r:
                raw_recipe = yaml.safe_load(r)
            parsed_recipe = RecipeSchema.parse_obj(raw_recipe)
            for name, bp_schema in parsed_recipe.blueprints.items():
                if bp_schema.kind not in runtime.available_blueprints:
                    raise MurkyWaterException(msg=f'Blueprint {bp_schema.kind} for instance {name} is not known')
                blueprint = runtime.available_blueprints[bp_schema.kind].from_schema(runtime, name, bp_schema)
                self.blueprints.append(blueprint)
        except Exception as e:
            console.print_exception()
