from queryfuzz.utils.file_operations import create_file
from abc import ABC, abstractmethod
from termcolor import colored
import copy
import os
from queryfuzz.utils.logging import Logging
import shutil

class BaseProgram(object):

    def __init__(self, params, verbose, randomness, program_number, seed_program):
        self.params = params
        self.verbose = verbose
        self.randomness = randomness
        self.string = ""
        self.seed_program = seed_program
        self.seed_program_file = None
        self.logs = Logging()
        # Program things
        self.allowed_types = list()         # Type: string
        self.facts = list()                 # A list of fact objects
        self.other_things = list()          # Type: string
        self.type_declarations = list()     # Type : string
        self.declarations = list()
        self.inputs = list()                # Type: string
        self.other_rules = list()
        self.all_rules = list()
        self.all_relations = list()         # Type: Subgoal() list
        self.output_rule = None             # Type: rule
        self.program_string = ""
        self.output_result_path = ""        # Path
        self.cycle_breakers = list()        # Type: Subgoal() list
        # Parameters
        self.number_of_simple_rules = self.randomness.get_random_integer(1, params["max_number_of_simple_rules"])
        self.number_of_complex_rules = self.randomness.get_random_integer(0, params["max_number_of_complex_rules"])
        self.number_of_facts = self.randomness.get_random_integer(1, params["max_number_of_fact_tables"])
        self.number_of_cycle_breaker_rules = self.randomness.get_random_integer(1, params["max_number_of_cycle_breaker_rules"])
        self.number_of_mixed_rules = self.randomness.get_random_integer(0, params["max_number_of_mixed_rules"])
        
        # other stuff
        self.program_path = None
        self.program_number = program_number
        self.program_file_path = None

        # Get allowed types
        self.get_allowed_types()

        # Some initial logs
        self.logs.add_log_text("\tSEED:" + str(self.randomness.get_initial_random_seed()))

        # parse the seed program
        if self.seed_program is not None:
            for r,d,f in os.walk(self.seed_program):
                for file in f:
                    if file.find(".dl") != -1:
                        self.seed_program_file = os.path.join(self.seed_program, file)
            self.logs.add_log_text(" ================= ")
            self.logs.add_log_text("  Seed Parsing ")
            self.logs.add_log_text(" ================= ")
            self.parse_program()

        self.logs.add_log_text("\n ================= ")
        self.logs.add_log_text("  File Generation ")
        self.logs.add_log_text(" ================= ")


    def enrich_program(self):
        # Step 2 : Generate facts
        self.logs.add_log_text("\tGenerating facts...")
        self.generate_facts()
        # Step 3 : Generate some more complex program elements.
        # Generate non-cyclic rules. These are the rules that are not used in the body of complex rules
        self.logs.add_log_text("\tGenerating some more complex program elements...")
        self.generate_cycle_breaker_rules()
        self.generate_mixed_rules()
        self.generate_complex_rules()
        # Generate Simple rules
        # Both the gen mode and nogen mode, both have program generation phase
        self.logs.add_log_text("\tGenerating simple rules...")
        self.generate_simple_rules()
        # Step 4 : Select an output rule
        self.output_rule = copy.deepcopy(self.all_rules[-1])
        self.logs.add_log_text("\tOutput rule: " + self.output_rule.get_head().get_string())
        # Output rule cannot be inlined. 
        for i, decl_string in enumerate(self.declarations):
            if decl_string.find(self.output_rule.get_head().get_name()) != -1:
                self.declarations[i] = decl_string.replace(" inline", "")

    @abstractmethod
    def get_allowed_types(self):
        pass

    @abstractmethod
    def parse_program(self):
        pass

    @abstractmethod
    def generate_cycle_breaker_rules(self):
        pass

    @abstractmethod
    def generate_mixed_rules(self):
        pass

    @abstractmethod
    def generate_complex_rules(self):
        pass

    @abstractmethod
    def generate_simple_rules(self):
        pass

    @abstractmethod
    def generate_facts(self):
        pass

    @abstractmethod
    def create_program_string(self):
        pass

    @abstractmethod
    def pretty_print_program(self):
        pass

    @abstractmethod
    def add_transformation_information(self, oracle):
        pass
    
    @abstractmethod
    def export_program_string(self, core_path):
        pass

    @abstractmethod
    def export_transformed_program_string(self, transformation_number):
        pass

    def set_output_result_path(self, path):
        self.output_result_path = path
    def get_string(self):
        return self.string
    def get_program_path(self):
        return self.program_path + "/"
    def get_program_file_path(self):
        return self.program_file_path
    def get_output_relation_name(self):
        return self.output_rule.get_head().get_name()
    def get_a_rule_for_transformation(self, oracle):
        # For an EQU transformation, we can pick any rule
        # For a CON or EXP transformation, we only can use a simple rule
        while True:
            rule = self.randomness.random_choice(self.all_rules)
            if oracle == "EQU":
                if rule.get_string().find("simple rule") != -1 or\
                    rule.get_string().find("complex rule") != -1:
                    # Pass by reference 
                    return rule
            if oracle == "CON" or oracle == "EXP":
                if rule.get_string().find("simple rule") != -1:
                    # Pass by reference 
                    return rule
    def get_output_result_file_path(self):
        return self.output_result_path
    def get_output_relation(self):
        # Return : output (Subgoal)
        return self.output_rule.get_head()
    def get_all_relations(self):
        # Return : list of relations in the program.
        return copy.deepcopy(self.all_relations)

    def add_log_text(self, text):
        self.logs.add_log_text(text)

    def dump_program_log_file(self):
        self.logs.dump_log_file()

    def refresh_log_text(self):
        self.logs.refresh_log_text()

    def get_log_file_path(self):
        return self.logs.get_log_file_path()

    def copy_fact_file_for_seed_program(self):
        for r,d,f in os.walk(self.seed_program):
            for file in f:
                if file.find(".facts") != -1:
                    shutil.copyfile(os.path.join(self.seed_program, file), os.path.join(self.program_path,file))

    def get_type_declarations(self):
        return self.type_declarations