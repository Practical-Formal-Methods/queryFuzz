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

from queryfuzz.datalog.base_fact import BaseFact
from queryfuzz.engines.z3.z3_subgoal import Z3Subgoal
from queryfuzz.datalog.variable import Variable
import string
from copy import deepcopy

class Z3Fact(BaseFact):
    def generate_fact(self):
        allowed_variable_types = self.params["z3_types"]
        self.name = self.randomness.get_lower_case_alpha_string(4)
        self.variables_types = [self.randomness.random_choice(allowed_variable_types) for i in range(self.arity)]
        # Generate rows
        for i in range(self.number_of_rows):
            table_entry = self.name + "("
            raw_data_row = ""
            for j in range(self.arity):
                data_type = self.variables_types[j]
                data_item = self.generate_data_item(data_type)
                table_entry += str(data_item) + ", "
                raw_data_row += str(data_item) + "\t"
            table_entry = table_entry[:-2] + ")."
            self.raw_data_entries.append(raw_data_row)
            self.fact_data.append(table_entry)


    def get_fact_as_a_relation(self):
        fact_subgoal = Z3Subgoal(randomness=self.randomness, arity=self.arity, params=self.params)
        fact_subgoal.generate_subgoal(name=self.name, 
                                        variables=[Variable(name=string.ascii_uppercase[i], vtype=self.variables_types[i]) for i in range(self.arity)], 
                                        variables_types=self.variables_types)
        return fact_subgoal

    def generate_decleration(self):
        self.declaration = self.name + "("
        for i in range(self.arity):
            self.declaration += string.ascii_uppercase[i] + ":" + self.variables_types[i] + ", "
        self.declaration = self.declaration[:-2] + ") input"
 
    def generate_data_item(self, type):
        if type == "Z":
            return self.randomness.get_random_integer(0,50)
