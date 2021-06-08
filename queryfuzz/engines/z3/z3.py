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

from queryfuzz.datalog.base_program import BaseProgram
from queryfuzz.engines.z3.z3_rule import Z3Rule
from queryfuzz.engines.z3.z3_fact import Z3Fact
from copy import deepcopy
from termcolor import colored
import os
from queryfuzz.utils.file_operations import create_file

class Z3Program(BaseProgram):

    def get_allowed_types(self):
        self.allowed_types = deepcopy(self.params["z3_types"])

    def generate_mixed_rules(self):
        for i in range(self.number_of_mixed_rules):
            mixed_rule = Z3Rule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            mixed_rule.generate_random_rule(ruleType="mixed", allowed_types=self.allowed_types, available_relations=self.all_relations)
            mixed_rule.generate_predicates()
            if self.params["max_number_of_negated_subgoals"] > 0: mixed_rule.add_negated_subgoals(available_relations=self.all_relations)
            self.declarations.append(mixed_rule.get_declaration())
            self.all_relations.append(deepcopy(mixed_rule.get_head()))
            self.all_rules.append(mixed_rule)


    def generate_simple_rules(self):
        """
            Simplest rules possible
        """
        # Generate simple rules
        for i in range(self.number_of_simple_rules):
            rule = Z3Rule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            rule.generate_random_rule(ruleType="simple", allowed_types=self.allowed_types, available_relations=self.all_relations)
            self.declarations.append(rule.get_declaration())
            self.all_relations.append(deepcopy(rule.get_head()))
            self.all_rules.append(rule)
        # Pop the last decleration 
        self.declarations.pop()

    def generate_facts(self):
        self.type_declarations.append("Z 64")
        for i in range(self.number_of_facts):
            fact_table = Z3Fact(randomness=self.randomness, params=self.params)
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())

    def pretty_print_program(self):
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")        
        for decl in self.declarations: print(colored(decl, "red", attrs=["bold"]))
        print(colored( self.output_rule.get_declaration() + " printtuples" , "green", attrs=["bold"]))   
        print("\n")
        for fact in self.facts:
            for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())
            # Mixed rule
            if rule_string.find("mixed rule") != -1:
                rule_string = rule_string.replace("##mixed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("##mixed rule", "magenta", attrs=["bold"]))
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("##simple rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("##simple rule", "green", attrs=["bold"]))
            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))


    def create_program_string(self):
        """
            Z3 program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        # type declaration
        for type_decl in self.type_declarations:
            self.program_string += type_decl + "\n"
        self.program_string += "\n"
        # declarations
        for decl in self.declarations:
            self.program_string += decl + "\n"
        self.program_string += self.output_rule.get_declaration() + " printtuples"        
        self.program_string += "\n\n"
        # facts (only when in_file_facts is true)
        self.program_string += "\n\n"
        for fact in self.facts:
            for row in fact.get_fact_data():
                self.program_string += row + "\n"
        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"

    def add_transformation_information(self, oracle):
        self.program_string = ""

    def export_program_string(self, core_path):
        """
            Export original program string
        """
        self.program_path = os.path.join(core_path, "program_" + str(self.program_number))
        self.program_file_path = os.path.join(self.program_path, "orig_rules.datalog")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        

    def export_transformed_program_string(self, transformation_number):
        """
            Export transformed program string
        """
        self.program_file_path = os.path.join(self.program_path, "transformed_rules_" + str(transformation_number) + ".datalog")
        self.logs.set_log_file_name("transformed_rules_" + str(transformation_number) + ".log")
        create_file(self.program_string, self.program_file_path)
