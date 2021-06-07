from queryfuzz.datalog.base_program import BaseProgram
from queryfuzz.engines.ddlog.ddlog_rule import DDlogRule
from queryfuzz.engines.ddlog.ddlog_fact import DDlogFact
from copy import deepcopy
from termcolor import colored
import os
from queryfuzz.utils.file_operations import create_file

class DDlogProgram(BaseProgram):
    def get_allowed_types(self):
        self.allowed_types = deepcopy(self.params["ddlog_types"])
    
    def generate_simple_rules(self):
        for i in range(self.number_of_simple_rules):
            rule = DDlogRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            rule.generate_random_rule(ruleType="simple", allowed_types=self.allowed_types, available_relations=self.all_relations)
            self.declarations.append(rule.get_declaration())
            self.all_relations.append(deepcopy(rule.get_head()))
            self.all_rules.append(rule)
            

    def generate_facts(self):
        for i in range(self.number_of_facts):
            fact_table = DDlogFact(randomness=self.randomness, params=self.params)
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())


    def pretty_print_program(self):
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")        
        for decl in self.declarations[:-1]: print(colored(decl, "red", attrs=["bold"]))
        print(colored("output " + self.output_rule.get_declaration(), "green", attrs=["bold"]))

        # facts (only when in_file_facts is true)
        if self.params["in_file_facts"]:
            for fact in self.facts:
                for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
            print("")

        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("//simple rule", "")
                print(colored(rule_string, "white", attrs=["bold"]), end="")
                print(colored("//simple rule", "green", attrs=["bold"]))
            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))
        print("")



    def create_program_string(self):
        # declarations
        for decl in self.declarations[:-1]:
            self.program_string += decl + "\n"
        self.program_string += "output " + self.output_rule.get_declaration() 
        self.program_string += "\n\n"
        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        


    def export_program_string(self, core_path):
        def export_facts():
            fact_file_string = "start;\n\n"
            for fact in self.facts:
                for row in fact.get_fact_data():
                    fact_file_string += row + "\n"
            fact_file_string += "commit;\ndump " + self.output_rule.get_head().get_name() + ";\n" 
            create_file(fact_file_string, os.path.join(self.program_path, "facts.dat"))


        self.program_path = os.path.join(core_path, "program_" + str(self.program_number))
        self.program_file_path = os.path.join(self.program_path, "orig_rules.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        export_facts()

    def add_transformation_information(self, oracle):
        self.program_string = ""


    def export_transformed_program_string(self, transformation_number):
        
        self.program_file_path = os.path.join(self.program_path, "transformed_rules_" + str(transformation_number) + ".dl")
        self.logs.set_log_file_name("transformed_rules_" + str(transformation_number) + ".log")
        create_file(self.program_string, self.program_file_path)