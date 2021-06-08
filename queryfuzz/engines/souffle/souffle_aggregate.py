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
from queryfuzz.engines.souffle.souffle_subgoal import SouffleSubgoal
from queryfuzz.engines.souffle.souffle_rule import SouffleRule
from copy import deepcopy
from queryfuzz.datalog.variable import Variable

class SouffleAggregate(object):
    def __init__(self, parent_rule, verbose, randomness, params, allowed_types, available_relations):
        # This should get the original rule and should be able to generate a new rule
        self.parent_rule = parent_rule
        self.verbose = verbose
        self.randomness = randomness
        self.params = params
        self.allowed_types = allowed_types
        self.available_relations = available_relations
        self.string = ""
        self.chosen_aggregate = None
        self.aggregate_body = None
        self.external_variable = None
        self.internal_variable = None
        self.aggregate_equality = self.randomness.random_choice(["=", "!=", "<", ">", ">=", "<="])
        self.generate_aggregate()


    def generate_aggregate(self):
        """
            B(y) :- y = max z : A("A", z).
            B(z) :- z = min x+y : { A(x), A(y), C(y) }.
            B(s, c) :- W(s), c = count : { C(s, _) }.
            B(n, m) :- A(n, m), B(m, s), 2 * s = 2 * sum s : { A(n, s) } + 2.
            C(n) :- D(n), B(n, max p : { A(n, p) }).
            B(s, count : { C(s, _) }) :- W(s).
        """

        aggregate_body_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
        aggregate_body_rule.generate_random_rule(ruleType="simple", allowed_types=self.allowed_types, available_relations=self.available_relations)
        # Rename the variables in the aggregate internals. They cannot be the same as in parent rule. This can cause serious type errors.
        for subgoal in aggregate_body_rule.get_real_subgoals():
            for i,var in enumerate(subgoal.get_variables()):
                subgoal.update_variable_at_location(Variable(var.get_name() + var.get_name() + var.get_name(), var.get_type()), i)
        aggregate_body_rule.update_string()
        aggregate_body_rule.generate_predicates()
        self.aggregate_body = aggregate_body_rule.get_body_string()

        # Pick a variable of type "number" in the parent rule.
        number_variables = [i for i in self.parent_rule.get_all_variables() if i.get_type() == "number"]
        if len(number_variables) == 0: return 1
        self.external_variable = self.randomness.random_choice(number_variables)
        self.internal_variable = self.randomness.random_choice(aggregate_body_rule.get_all_variables())  
        if self.internal_variable.get_type() == "number": self.chosen_aggregate = self.randomness.random_choice(["min", "max", "sum", "count"])
        if self.internal_variable.get_type() == "symbol": self.chosen_aggregate = "count"

    def get_string(self):
        if self.external_variable is None or self.internal_variable is None or self.chosen_aggregate is None or self.aggregate_body is None:
            return "0 = 0"
        # No need to include the internal variable in case of count aggregate
        if self.chosen_aggregate == "count":
            self.string = self.external_variable.get_name() + " " + self.aggregate_equality + " " + self.chosen_aggregate + " : {" + self.aggregate_body + "}"
        else:
            self.string = self.external_variable.get_name() + " " + self.aggregate_equality + " " + self.chosen_aggregate + " " + self.internal_variable.get_name() + " : { " + self.aggregate_body + "}"
        return self.string

