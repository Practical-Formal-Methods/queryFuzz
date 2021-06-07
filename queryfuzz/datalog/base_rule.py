from abc import ABC, abstractmethod
from queryfuzz.datalog.base_subgoal import BaseSubgoal
from queryfuzz.datalog.variable import Variable
from termcolor import colored
from copy import deepcopy
import string

class BaseRule(object):
    def __init__(self, verbose, randomness, params):
        """
            This is a conjunctive query. The most basic 
            rule definition we can have.
        """
        self.verbose = verbose          # Type: bool 
        self.params = params
        self.string = ""                # Type: string
        self.decleration_string = ""    # Type: string
        self.head = None                # Type: Subgoal()
        self.subgoals = list()          # Type: Subgoal() list
        self.predicates = list()        # Type: Predicate() list
        self.aggregate = None           # Type: String
        self.ruleType = None            # Type: string
        self.randomness = randomness    # Type: Randomenss()
        self.head_arity = 0             # Type: int
        self.all_variables = list()     # Type: Variable() list        

        # Parameters
        self.number_of_subgoals = self.randomness.get_random_integer(1, params["max_number_of_body_subgoals"])
        self.number_of_predicates = self.randomness.get_random_integer(0, params["max_number_of_predicates"])

        # Internal things
        self.types_used = list()

    # >>>> ENGINE SPECIFIC THINGS ---------------------------- 
    @abstractmethod
    def generate_random_rule(self, ruleType, allowed_types, available_relations):
        pass

    @abstractmethod
    def generate_disjunctive_rule(self, head, available_relations):
        pass

    @abstractmethod
    def add_functions_in_head(self):
        pass

    def add_operations_in_head(self):
        pass

    @abstractmethod
    def parse_rule(self, rule_string):
        pass

    @abstractmethod
    def generate_decleration(self):
        pass

    @abstractmethod
    def add_negated_subgoals(self, available_relations):
        pass

    @abstractmethod
    def generate_predicates(self):
        pass

    @abstractmethod 
    def insert_operations_in_head(self):
        pass

    @abstractmethod
    def generate_heads(self, non_cyclic_relations):
        pass

    @abstractmethod
    def update_string(self):
        pass

    # >>>> HELPER FUNCTIONS ---------------------------- 
    def get_types_in_body(self):
        """
            Get all the types used in the body as a set
        """
        for subgoal in self.subgoals:
            self.types_used = self.types_used + subgoal.get_types()
        self.types_used = list(set(self.types_used))
        self.types_used.sort()    # Because set() messes up the randomness


    def validate_rule(self):
        """
            Determine number of variable spots "s" of each type.
            Generate "n" variables
            where 1 <= n <= s
        """
        temporary_index = 0
        collection_of_variable = [i for i in string.ascii_uppercase] +  [i+i for i in string.ascii_uppercase] + [i+i+i for i in string.ascii_uppercase]
        for var_type in self.types_used:
            # see how many variable spots have these types in the subgoal
            spots = 0
            for subgoal in self.subgoals:
                spots += len([i for i in subgoal.get_types() if i == var_type])
            # Create variables of this type
            number_of_variables = 1 if spots < 3 else self.randomness.get_random_integer(2, spots-1)
            new_variables = [Variable(collection_of_variable[i + temporary_index], var_type) for i in range(number_of_variables)]
            temporary_index += number_of_variables
            # Now we rename variables
            for subgoal in self.subgoals:
                for i in range(len(subgoal.get_types())):
                    if subgoal.get_types()[i] == var_type:
                        new_var = deepcopy(self.randomness.random_choice(new_variables))
                        subgoal.update_variable_at_location(new_var, i)

        # Choose variables for the head
        for i in range(len(self.head.get_variables())):
            chosen_variable = self.randomness.random_choice(self.get_body_variables_of_type(self.head.get_variables()[i].get_type()))
            self.head.update_variable_at_location(chosen_variable, i)

    def lower_case_variables(self):
        self.head.lower_case_variables()
        for subgoal in self.subgoals:
            subgoal.lower_case_variables()


    def get_body_variables_of_type(self, var_type):
        """
            Return copies of variables, not the real things!
        """
        variables = list()
        for subgoal in self.subgoals:
            for var in subgoal.get_variables():
                if var.get_type() == var_type:
                    variables.append(deepcopy(var)) # Return copies
        return variables
    
    def get_string(self):
        return self.string
    def get_subgoals(self):
        """
            Pass by value
        """
        return deepcopy(self.subgoals)
    def get_real_subgoals(self):
        """
            Pass by reference
        """
        return self.subgoals    
    def get_head(self):
        return self.head
    def get_declaration(self):
        return self.decleration_string
    def get_rule_type(self):
        return self.ruleType
    def get_all_variables(self):
        return deepcopy(self.all_variables)
    def get_a_random_positive_subgoal(self):
        while True:
            # This must terminate at some point
            subgoal = self.randomness.random_choice(self.subgoals)
            if not subgoal.is_negated():
                return deepcopy(subgoal)
    
    def get_a_real_random_positive_subgoal(self):
        while True:
            # This must terminate at some point
            subgoal = self.randomness.random_choice(self.subgoals)
            if not subgoal.is_negated():
                return subgoal
    
    def get_body_string(self):
        body_string = ""
        for subgoal in self.subgoals: body_string += subgoal.get_string() + ", "
        for predicate in self.predicates: body_string += predicate.get_string() + ", "
        if self.aggregate is not None: body_string += self.aggregate
        if self.aggregate is None: body_string = body_string[:-2]
        return body_string

    def append_subgoal(self, subgoal):
        self.subgoals.append(subgoal)
        self.update_string()
    
    def update_rule_type(self, _type):
        self.ruleType = _type
        self.update_string()

    def get_variable_names_as_a_set(self):
        variable_set = list()
        for subgoal in self.subgoals:
            variable_set += [i.get_name() for i in subgoal.get_variables() if i.get_name() not in variable_set]
        return variable_set

    def add_aggregate(self, aggregate_string):
        self.aggregate = aggregate_string
        self.update_string()

    def set_string(self, string):
        self.string = string