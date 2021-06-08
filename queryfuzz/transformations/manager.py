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
from copy import deepcopy
from queryfuzz.transformations.cqt import cqtTransformer
from queryfuzz.transformations.neg import negTransformer

class TransformationManager(object):
    def __init__(self, randomness, program, params, verbose, engine):
        """
            Multi rule transformations
        """
        self.randomness = randomness
        self.params = params
        self.original_program = program
        self.verbose = verbose
        self.transformed_program = deepcopy(program)
        self.engine = engine
        # Update logs for this new file
        self.transformed_program.refresh_log_text()
        self.transformation_types = ["EQU", "EXP", "CON"]
        self.EXPAND = ["ADD_EQU", "MOD_EQU", "REM_EQU", "MOD_EXP", "REM_EXP"]
        self.CONTRACT = ["ADD_EQU", "MOD_EQU", "REM_EQU", "ADD_CON", "MOD_CON"]
        self.EQUIVALENT = ["ADD_EQU", "MOD_EQU", "REM_EQU"]
        self.chosen_transformation_type = self.randomness.random_choice(self.transformation_types)  # Oracle.
        self.number_of_rules_transformed = self.randomness.get_random_integer(1, self.params["max_rule_transformations"])
        self.transformed_program.add_log_text("Oracle: " + self.chosen_transformation_type)


    def generate_transformation_sequence(self):
        sequence_length = self.randomness.get_random_integer(1, self.params["max_transformation_sequence"])
        if self.chosen_transformation_type == "EXP":
            return [self.randomness.random_choice(self.EQUIVALENT + self.EXPAND) for i in range(sequence_length)] 
        if self.chosen_transformation_type == "EQU":
            # This can either return a sequence of EQU transformations or "NEG"
            if self.engine == "souffle": return self.randomness.random_choice([[self.randomness.random_choice(self.EQUIVALENT) for i in range(sequence_length)], "NEG"])
            else: return self.randomness.random_choice([[self.randomness.random_choice(self.EQUIVALENT) for i in range(sequence_length)]])
        if self.chosen_transformation_type == "CON":
            return [self.randomness.random_choice(self.EQUIVALENT + self.CONTRACT) for i in range(sequence_length)] 


    def generate_transformation(self):
        """
            This can generate transformations for multiple rules in the file.
        """
        for i in range(self.number_of_rules_transformed):
            # Generate a transformation sequence
            transformation_sequence = self.generate_transformation_sequence()
            self.transformed_program.add_log_text("Transformation Sequence: " + str(transformation_sequence))
            # Pick a rule that can be fuzzed
            rule_to_be_transformed = self.transformed_program.get_a_rule_for_transformation(oracle=self.chosen_transformation_type)
            self.transformed_program.add_log_text("\n\tORIG RULE:  " + rule_to_be_transformed.get_string())
            # Apply the transformation
            self.apply_transformations_on_a_rule(transformation_sequence, rule_to_be_transformed)
            self.transformed_program.add_log_text("\n\t\t\t  |  ")
            self.transformed_program.add_log_text("\t\t\t  V  \n")
            self.transformed_program.add_log_text("\tTRANS RULE:  " + rule_to_be_transformed.get_string())
        return self.transformed_program


    def apply_transformations_on_a_rule(self, transformation_sequence, rule):
        if transformation_sequence == "NEG":
            print(colored(" [NEG]", "blue"))
            neg_transformer = negTransformer(self.randomness, self.verbose, self.params, rule, self.transformed_program)
            neg_transformer.apply_transformation()
        else:
            cqt_transformer = cqtTransformer(self.randomness, self.verbose, self.params, rule, self.transformed_program)
            cqt_transformer.apply_transformation_sequence(transformation_sequence)
            print("")
            if self.engine == "ddlog": 
                rule.lower_case_variables()
            rule.update_rule_type("transformed")
        
        if self.verbose: self.transformed_program.pretty_print_program()

    def get_chosen_transformation_type(self):
        return self.chosen_transformation_type