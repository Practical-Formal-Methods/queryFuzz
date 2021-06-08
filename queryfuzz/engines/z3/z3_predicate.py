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

from queryfuzz.datalog.base_predicate import BasePredicate

class Z3Predicate(BasePredicate):
    def generate_number_predicate(self):
        operations = ["=", "!=", "<", ">"]
        operand_1 = self.randomness.random_choice([self.randomness.random_choice([i.get_name() for i in self.variables]), str(self.randomness.get_random_integer(0,100))])
        operation = self.randomness.random_choice(operations)
        operand_2 = self.randomness.random_choice([i.get_name() for i in self.variables])
        self.string = operand_1 + " " + operation + " " + operand_2

    def generate_predicate(self):
        self.generate_number_predicate()