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
from queryfuzz.engines.souffle.souffle_subgoal import SouffleSubgoal
from queryfuzz.engines.souffle.souffle_predicate import SoufflePredicate 
import string 
from copy import deepcopy
from termcolor import colored


class SouffleRule(BaseRule):
    def generate_random_rule(self, ruleType, allowed_types, available_relations):
        """
            First we select the subgoals for the body from available_relations. 
            A head is then generated depending on the types
            that are in the body.

            Step 1: Choose subgoals for the body
            Step 2: Get all the types in the body
            Step 3: Create a head
            Step 4: Create joins by variable renamings and make this a valid clause
        """
        
        self.ruleType = ruleType
        # Step 1: Generate body by choosing relations in the base program
        for i in range(self.number_of_subgoals):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        # Step 2: Get the used types in the body
        self.get_types_in_body()
        # Step 3: Create basic head subgoal
        self.head_arity = self.randomness.get_random_integer(1, self.params["max_head_arity"])
        self.head = SouffleSubgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
        self.head.generate_random_subgoal(allowed_types=self.types_used)
        # Step 4: Make this a valid clause + create joins
        self.validate_rule()        
        # Done! Update string
        self.update_string()
        self.generate_decleration()

    def generate_disjunctive_rule(self, parent_rule, available_relations):
        """
            It takes the head as input and the list of all avaiable relations
            Will just generate 1 disjunctive rule
        """
        self.head = deepcopy(parent_rule.get_head())
        self.ruleType = parent_rule.get_rule_type()
        # For each variable type in the head, find a relation that conatins such a variable type and then insert it in the body
        for var in self.head.get_variables():
            # Search for a relations that contains a variable of this type
            while True:
                # This will ALWAYS break at some point
                rel = deepcopy(self.randomness.random_choice(available_relations))
                if var.get_type() in rel.get_types():
                    self.subgoals.append(rel)
                    break
        # Add the remaining number of subgoals
        for i in range(self.number_of_subgoals - len(self.subgoals)):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        self.get_types_in_body()
        self.validate_rule()
        self.update_string()

    def generate_decleration(self):
        self.decleration_string = ".decl " + self.head.get_name() + "("
        for i in range(self.head_arity):
            self.decleration_string += string.ascii_uppercase[i] + ":" + self.head.get_types()[i] + ", "
        self.decleration_string = self.decleration_string[:-2] + ")"
        if self.params["inline"] and self.ruleType == "simple": self.decleration_string += self.randomness.random_choice(["", " inline"])
        self.decleration_string += self.randomness.random_choice(["", " brie", " btree"])


    def add_negated_subgoals(self, available_relations):        
        for i in range(self.randomness.get_random_integer(0,self.params["max_number_of_negated_subgoals"])):
            success = True
            subgoal = deepcopy(self.randomness.random_choice(available_relations))
            # Now for each variable type in this new subgoal, we have to get a variable that is already in the rule
            # and put it here. If we cannot find such a variable then we are in trouble and we cannot safely negate it 
            for i, var in enumerate(subgoal.get_variables()):
                # pick a random variable from the following list of copied variables
                variables_of_this_type = self.get_body_variables_of_type(var.get_type())
                if len(variables_of_this_type) == 0:
                    success = False
                    break
                new_var = self.randomness.random_choice(variables_of_this_type)
                subgoal.update_variable_at_location(new_var, i)
            if not success: continue
            # Negate this subgoal
            subgoal.negate_subgoal()
            # Change it to an unsafe negation
            if self.params["unsafe_negations"]: subgoal.underline_a_variable()
            # Add this subgoal in the list of subgoals
            self.subgoals.append(subgoal)
            self.update_string()

    def generate_predicates(self):
        for i in range(self.number_of_predicates):
            predicate = SoufflePredicate(self.all_variables, self.randomness)
            if predicate.get_string() != "": self.predicates.append(predicate)
            self.update_string()

    def generate_heads(self, non_cyclic_relations):
        """ 
            Add multiple heads in the rule.
            Only updates the string of the rule. Nothing else is changed. Updating the rule will reset it to its original string.
        """
        valid_relations = list()
        for relation in non_cyclic_relations:
            flag = True
            for _type in relation.get_types():
                if _type not in self.types_used: 
                    flag = False
                    continue
            if flag: valid_relations.append(relation)
        
        # Do nothing if valid_relations is empty
        if len(valid_relations) == 0: return 1
        number_of_heads = self.randomness.get_random_integer(0, self.params["max_heads_in_mixed_rule"])
        new_head_string = ""
        # Now pick a realtion and rename the variables
        for i in range(number_of_heads):
            picked_relation = deepcopy(self.randomness.random_choice(valid_relations))
            for j, var in enumerate(picked_relation.get_variables()):
                picked_var = self.randomness.random_choice(self.get_body_variables_of_type(var.get_type()))
                picked_relation.update_variable_at_location(picked_var, j)
            new_head_string += ", " + picked_relation.get_string()
        self.string = self.head.get_string() + new_head_string + " " + self.string[self.string.find(":-"):]

    def insert_operations_in_head(self):
        """
            Insert operations in head
        """
        self.head.insert_operations(self.get_all_variables())
        self.update_string()

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