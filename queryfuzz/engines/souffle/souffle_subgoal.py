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


from queryfuzz.datalog.base_subgoal import BaseSubgoal
from queryfuzz.datalog.variable import Variable
from termcolor import colored
import copy

class SouffleSubgoal(BaseSubgoal):

    def parse_subgoal_declaration(self, subgoal_decleration_string):
        temp_string = copy.deepcopy(subgoal_decleration_string)
        temp_string = temp_string.replace(".decl ", "")
        self.name = temp_string[0:temp_string.find("(")]
        variables_with_types = temp_string[temp_string.find("(") + 1 : temp_string.find(")")].replace(" ", "").split(",")
        if variables_with_types[0] == "":
            # No variables were declared in this subgoal
            self.arity = 0
        else:
            # Found atleast one variable declaration
            self.arity = len(variables_with_types)
            for variable in variables_with_types:
                var_name = variable[:variable.find(":")]
                var_type = variable[variable.find(":") + 1:]
                self.variables.append(Variable(var_name, var_type))
                self.variables_types.append(var_type)        
            self.update_string()


    def negate_subgoal(self):
        self.negated = True
        self.string = "!" + self.string

    def insert_operations(self, all_rule_variables):
        """
            Number data type:
                Binary operations:
                    +, -, *, /, ^, %, min, max
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j) :- A(i), B(j), i!=j, i = 2.1.
                    C(i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

                Unaray operations 
                    Negation:
                    C(-i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.
                    
                    Double negation:
                        C(--i*2,j/i) :- A(i), B(j), i!=j, i = 2.1, j < 5.

            String data type:
                Binary operations:
                    cat(A, "x")
                    cat(A, B)
        """
        operations_dictionary = {
                                    "number" : {
                                                    "binary"    :   ["+", "-", "*", "/"],
                                                    "unary"     :   ["-", "--"],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "unsigned" : {
                                                    "binary"    :   ["+", "-", "*"],
                                                    "unary"     :   [""],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "float" : {
                                                    "binary"    :   ["+", "-", "*", "/", "^"],
                                                    "unary"     :   ["-", "--"],
                                                    "func"      :   ["min", "max"]
                                    },
                                    "symbol" : {    
                                                    "binary"    :   [""],
                                                    "unary"     :   [""],
                                                    "func"      :   ["cat"]
                                    }
        }         
        max_expression_adding_operations = self.randomness.get_random_integer(0, self.params["max_expression_adding_operations"])
        for i in range(max_expression_adding_operations):
            variable = self.randomness.random_choice(self.variables)
            variable_type = variable.get_type()
            if variable_type not in self.params["souffle_types"]: continue
            new_variable_string = ""
            operation_type = self.randomness.random_choice(["binary", "binary", "unary", "unary", "func"])
            if variable_type == "symbol": operation_type = "func"
            operation = self.randomness.random_choice(operations_dictionary[variable_type][operation_type])
            random_constant = ""
            random_variable = self.randomness.random_choice([i.get_name() for i in all_rule_variables if i.get_type() == variable_type])
            if variable_type == "symbol": random_constant = '"' + self.randomness.get_random_alpha_string(1) + '"'
            if variable_type == "number": random_constant = str(self.randomness.get_random_integer(-10,10))   
            if variable_type == "unsigned": random_constant = str(self.randomness.get_random_integer(0,20))   
            if variable_type == "float" : random_constant = str(self.randomness.get_random_float(-10, 10))   
            if operation_type == "func": new_variable_string = operation + '(' + variable.get_name() + ',' + self.randomness.random_choice([random_constant, random_variable]) + ')'
            if operation_type == "binary": new_variable_string = variable.get_name() + operation + self.randomness.random_choice([random_constant, random_variable])
            if operation_type == "unary": new_variable_string = operation + variable.get_name()
            variable.set_name(new_variable_string)
        self.update_string()
