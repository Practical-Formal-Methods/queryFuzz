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

from termcolor import colored
import string
import copy


class negTransformer(object):
    def __init__(self, randomness, verbose, params, rule, transformed_program):
        self.randomness = randomness
        self.verbose = verbose
        self.params = params
        self.rule = rule
        self.transformed_program = transformed_program
        self.chosen_subgoal = None
        self.negated_rule_string = ""
        self.negated_decl_string = ""


    def apply_transformation(self):
        """
            Choose a positive subgoal from rule. The rule should be simple
            If the variables in chosen subgoal are found somewhere else in the rule then this is a good choice.
        """
        if self.rule.get_rule_type() != "simple":
            return 1
        self.chosen_subgoal = self.rule.get_a_real_random_positive_subgoal()
        if not self.variables_grounded():
            return 1
        # It is not allowed for the chosen subgoal to be inlined!
        for decl in self.transformed_program.declarations:
            if decl.find(self.chosen_subgoal.get_name()) != -1 and decl.find("inline") != -1:
                return 1
        self.generate_negation_rule()
        self.transformed_program.declarations.append(self.negated_decl_string)
        self.chosen_subgoal.update_subgoal_name("negate")
        self.chosen_subgoal.negate_subgoal()
        self.chosen_subgoal.update_string()
        self.rule.update_string()
        self.rule.update_rule_type("transformed")
        self.rule.string = self.negated_rule_string + "\t\t//transformed rule" + "\n" + self.rule.string
        

    def generate_negation_rule(self):
        # Generate decleration string 
        # We can just copy the decleration of the subgoal we want to negate
        self.negated_decl_string = ".decl negate("
        for i in range(self.chosen_subgoal.get_arity()):
            self.negated_decl_string += string.ascii_uppercase[i] + ":" + self.chosen_subgoal.get_variables()[i].get_type() + ", "
        self.negated_decl_string = self.negated_decl_string[:-2] + ")"
        head_string = copy.deepcopy(self.chosen_subgoal.get_string()).replace(self.chosen_subgoal.get_name() + "(", "negate(")
        body_string = ""
        for body_elem in [i for i in self.rule.get_subgoals() if i.get_string() != self.chosen_subgoal.get_string()]:
            body_string += body_elem.get_string() + ", "
        body_string = body_string[:-2]
        if body_string != "":
            self.negated_rule_string = head_string + " :- " + body_string + ", !" + self.chosen_subgoal.get_string() + "."
        else:
            self.negated_rule_string = "// Cannot negate. Sorry"


    def variables_grounded(self):
            # check if all the variables of the chosen sub-goal are also found somewhere else or are ungrounded.
            # Returns true if variables are grounded
            chosen_variables = self.chosen_subgoal.get_variables()
            remaining_body = [i for i in self.rule.get_subgoals() if i.get_name() != self.chosen_subgoal.get_name()]
            for var in chosen_variables:
                found = False
                for sub_goal in remaining_body:
                    if var.get_name() in [i.get_name() for i in sub_goal.get_variables()]:
                        found = True
                        break
                if not found:
                    return False
            return True