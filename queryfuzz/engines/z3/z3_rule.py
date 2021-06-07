from queryfuzz.datalog.base_rule import BaseRule
from queryfuzz.engines.z3.z3_subgoal import Z3Subgoal
from queryfuzz.engines.z3.z3_predicate import Z3Predicate
from copy import deepcopy
import string

class Z3Rule(BaseRule):

    def generate_random_rule(self, ruleType, allowed_types, available_relations):
        self.ruleType = ruleType
        for i in range(self.number_of_subgoals):
            self.subgoals.append(deepcopy(self.randomness.random_choice(available_relations)))
        self.get_types_in_body()
        self.head_arity = self.randomness.get_random_integer(1, self.params["max_head_arity"])
        self.head = Z3Subgoal(randomness=self.randomness, arity=self.head_arity, params=self.params)
        self.head.generate_random_subgoal(allowed_types=self.types_used)
        self.validate_rule() 
        self.update_string()
        self.generate_decleration()


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

    def generate_decleration(self):
        self.decleration_string = self.head.get_name() + "("
        for i in range(self.head_arity):
            self.decleration_string += string.ascii_uppercase[i] + ":" + self.head.get_types()[i] + ", "
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
        self.string += "     ##" + self.ruleType + " rule"


    def generate_predicates(self):
        for i in range(self.number_of_predicates):
            predicate = Z3Predicate(self.all_variables, self.randomness)
            if predicate.get_string() != "": self.predicates.append(predicate)
            self.update_string()