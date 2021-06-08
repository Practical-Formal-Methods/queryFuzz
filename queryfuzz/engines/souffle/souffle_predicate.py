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
from termcolor import colored


class SoufflePredicate(BasePredicate):
    def generate_number_predicate(self):
        """
            Comparison:
                A(a,c) :- a > c.
                B(a,c) :- a < c.
                C(a,c) :- a = c.
                D(a,c) :- a != c.
                E(a,c) :- a <= c.
                F(a,c) :- a >= c.
            strlen:
                ord(A) > strlen("IbM3cHsXpfPzyChuOZ")
            to_number:
                to_number("-8") != A
        """ 
        number_predicate_type = self.randomness.random_choice(["comparison", "to_number"]) # "strlen"
        operations = ["=", "!=", "<", ">", "<=", ">="]
        if number_predicate_type == "comparison":
            operand_1 = self.randomness.random_choice([self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "number"]), str(self.randomness.get_random_integer(-10,10))])
            operation = self.randomness.random_choice(operations)
            operand_2 = self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "number"])
            self.string = operand_1 + " " + operation + " " + operand_2
        """
        if number_predicate_type == "strlen":
            variable = self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "number"])
            operation = self.randomness.random_choice(operations)
            string = self.randomness.get_random_alpha_numeric_string(self.randomness.get_random_integer(1,20))
            self.string = 'ord(' + variable + ') '  + operation + ' strlen("' + string + '")'
        """
        if number_predicate_type == "to_number":
            variable = self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "number"])
            operation = self.randomness.random_choice(operations)
            number_string = str(self.randomness.get_random_integer(-10,10))
            self.string = 'to_number("' + number_string + '") '  + operation + ' ' + variable


    def generate_float_predicate(self):
        float_predicate_type = self.randomness.random_choice(["comparison"]) # "to_number", "strlen" TODO
        operations = ["=", "!=", "<", ">", "<=", ">="]
        if float_predicate_type == "comparison":
            operand_1 = self.randomness.random_choice([self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "float"]), str(self.randomness.get_random_float(-10,10)), "-0.0", "0.0"])
            operation = self.randomness.random_choice(operations)
            operand_2 = self.randomness.random_choice([i.get_name() for i in self.variables if i.get_type() == "float"])
            self.string = operand_1 + " " + operation + " " + operand_2


    def generate_string_predicate(self):
        string_predicate_type = self.randomness.random_choice(["contains", "match", "substr"]) # "ord", "strlen"
        operations = ["=", "!=", "<", ">", "<=", ">="]
        symbol_variables = [i.get_name() for i in self.variables if i.get_type() == "symbol"]
        """
        if string_predicate_type == "ord":
            operand_1 = self.randomness.random_choice(symbol_variables)
            operand_2 = self.randomness.random_choice([self.randomness.random_choice(symbol_variables), '"' + self.randomness.get_random_alpha_numeric_string(self.randomness.get_random_integer(1,20)) + '"'])
            operation = self.randomness.random_choice(operations)
            self.string = 'ord(' + operand_1 + ') '  + operation + ' ord(' + operand_2 + ') '
        """
        if string_predicate_type == "contains":
            argument_1 = self.randomness.random_choice( symbol_variables + ['"' + self.randomness.get_random_alpha_string(1) + '"' for i in range(len(symbol_variables))])
            argument_2 = self.randomness.random_choice( symbol_variables + ['"' + self.randomness.get_random_alpha_string(1) + '"' for i in range(len(symbol_variables))])
            self.string = 'contains(' + argument_1 + "," + argument_2 + ")"
        if string_predicate_type == "match":
            self.string = 'match("' + self.randomness.get_random_alpha_string(1) + '.*",' + self.randomness.random_choice(symbol_variables) + ')'
        if string_predicate_type == "substr":
            rand_var = self.randomness.get_random_alpha_string(3)
            self.string =  rand_var + '="'+ self.randomness.get_random_alpha_string(3) +'", ' + self.randomness.random_choice(symbol_variables) + '=substr('+ rand_var +',0,1)'            
        """
        if string_predicate_type == "strlen":
            variable = self.randomness.random_choice(symbol_variables)
            operation = self.randomness.random_choice(operations)
            string = self.randomness.get_random_alpha_numeric_string(self.randomness.get_random_integer(1,20))
            self.string = 'ord(' + variable + ') '  + operation + ' strlen("' + string + '")'
        """

    def generate_mixed_predicate(self):
        """
            ord(A) > strlen(B)    where A is of type string and B is of type string
        """
        self.string = "1 = 1"


    def generate_predicate(self):
        # Pick a predicate type by randomly picking a variable
        predicate_type = self.randomness.random_choice([i.get_type() for i in self.variables])
        if "symbol" in [i.get_type() for i in self.variables] and "number" in [i.get_type() for i in self.variables]:
            predicate_type = self.randomness.random_choice([predicate_type, "mixed"])

        if predicate_type == "number":
            self.generate_number_predicate()
        
        if predicate_type == "symbol":
            self.generate_string_predicate()
        
        if predicate_type == "float":
            self.generate_float_predicate()

        if predicate_type == "mixed":
            self.generate_mixed_predicate()
