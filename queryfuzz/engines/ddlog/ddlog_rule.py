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

from queryfuzz.datalog.base_rule import BaseRule
from queryfuzz.engines.ddlog.ddlog_subgoal import DDlogSubgoal
from copy import deepcopy
import string

class DDlogRule(BaseRule):

    def generate_random_rule(self, ruleType, allowed_types, available_relations):
        self.ruleType = ruleType
        for i in range(self.number_of_subgoals):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        self.get_types_in_body()
        self.head_arity = 1
        self.head = DDlogSubgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
        self.head.generate_random_subgoal(allowed_types=self.types_used)
        self.validate_rule() 
        self.head.upper_case_name()
        self.lower_case_variables()
        self.update_string()
        self.generate_decleration()
        


    def generate_decleration(self):
        self.decleration_string = "relation " + self.head.get_name() + "("
        for i in range(self.head_arity):
            self.decleration_string += string.ascii_lowercase[i] + ":" + self.head.get_types()[i] + ", "
        self.decleration_string = self.decleration_string[:-2] + ")"


    
    def update_string(self):
        # update the list of variables in the body as well
        self.all_variables = list()
        for subgoal in self.subgoals:
            self.all_variables = self.all_variables + subgoal.get_variables()
        # update string
        self.string = self.head.get_string()
        self.string += " :- "
        # body
        
        # Subgoal
        for subgoal in self.subgoals:
            self.string += subgoal.get_string() + ", "
        
        # Predicates
        for predicate in self.predicates:
            self.string += predicate.get_string() + ", "
        
        # Aggregate
        if self.aggregate is not None: self.string += self.aggregate
        if self.aggregate is None: self.string = self.string[:-2]

        self.string += "."
        self.string += "     //" + self.ruleType + " rule"