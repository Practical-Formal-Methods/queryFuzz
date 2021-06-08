"""
Copyright 2021 MPI-SWS
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from abc import ABC, abstractmethod

class BasePredicate(object):
    def __init__(self, variables, randomness):
        self.randomness = randomness
        self.variables = variables      # Type: List of var() objects
        self.string = ""                # Type: string
        self.generate_predicate()               

    @abstractmethod
    def generate_predicate(self):
        pass

    def get_string(self):
        return self.string