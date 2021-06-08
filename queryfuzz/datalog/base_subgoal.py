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
from queryfuzz.datalog.variable import Variable
from copy import deepcopy
import string

class BaseSubgoal(object):
    def __init__(self, randomness, arity, params):
        self.string = ""
        self.name = ""
        self.arity = arity  
        self.variables = list()             # Type: Variable() list
        self.variables_types = list()       # Type: String list
        self.randomness = randomness
        self.negated = False
        self.params = params

    def generate_random_subgoal(self, allowed_types):
        """
            allowed_type: list of types that can be included in the attributes
        """
        # Generate subgoal name (Alpha-numeric of length 4)
        self.name = self.randomness.get_lower_case_alpha_string(4)
        # Pick types
        self.variables_types = [self.randomness.random_choice(allowed_types) for i in range(self.arity)]
        # generate variables
        for i in range(self.arity):
            self.variables.append(Variable(name=self.randomness.get_upper_case_alpha_string(4), vtype=self.variables_types[i]))       
        self.update_string()

    def generate_subgoal(self, name, variables, variables_types):
        self.name = name
        self.variables = variables
        self.variables_types = variables_types
        self.update_string()


    # >>> ENGINE SPECIFIC THINGS ---------------------------- 
    @abstractmethod
    def negate_subgoal(self):
        pass

    @abstractmethod
    def parse_subgoal_declaration(self, subgoal_decleration_string):
        pass

    @abstractmethod
    def insert_operations(self, all_rule_variables):
        pass
    
    def upper_case_name(self):
        self.name = self.name.upper()
        self.update_string()
    

    def lower_case_variables(self):
        for var in self.variables:
            var.set_name(var.get_name().lower())
        self.update_string()

    def update_string(self):
        self.string = self.name + "("
        for variable in self.variables:
            self.string += variable.get_name() + ", "
        self.string = self.string[:-2] + ")"
        if self.negated: self.negate_subgoal()

    def get_name(self):
        return self.name
    def get_string(self):
        return self.string
    def get_variables(self):
        return self.variables
    def get_types(self):
        return self.variables_types
    def get_arity(self):
        return self.arity
    def update_variable_at_location(self, new_var, location):
        """
            new_var     :   Type Variable()
        """
        self.variables[location] = new_var
        self.update_string()
    def is_negated(self):
        # Return true if it is a negated subgoal
        return self.negated

    def update_subgoal_name(self, new_name):
        self.name = new_name

    def underline_a_variable(self):
        """
            This is kinda buggy
        """
        var = self.randomness.random_choice(self.variables)
        temp_var = deepcopy(var)
        if self.randomness.flip_a_coin():
            var.set_name("_")
            self.update_string()
        var.set_name(temp_var.get_name())
