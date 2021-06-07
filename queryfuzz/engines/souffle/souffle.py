from queryfuzz.datalog.base_program import BaseProgram
from queryfuzz.engines.souffle.souffle_rule import SouffleRule
from queryfuzz.engines.souffle.souffle_fact import SouffleFact
from queryfuzz.engines.souffle.souffle_aggregate import SouffleAggregate
from queryfuzz.engines.souffle.souffle_subgoal import SouffleSubgoal
from queryfuzz.utils.file_operations import create_file
from copy import deepcopy
from termcolor import colored
import os

class SouffleProgram(BaseProgram):
    def get_allowed_types(self):
        self.allowed_types = deepcopy(self.params["souffle_types"])

    def parse_program(self):
        """
            Parse a program
        """
        # Read the file.
        self.add_log_text("\tReading seed file: " + self.seed_program_file)
        with open(self.seed_program_file, 'r') as f:
            lines = f.read().splitlines()
            for line in lines:
                # Type definition ?
                if line.find(".type") != -1:
                    self.type_declarations.append(line + "  //Parsed entity") 
                    continue
                # Decleration ?
                if line.find(".decl") != -1:
                    self.declarations.append(line + "  //Parsed entity")
                    # We have to create a subgoal
                    parsed_subgoal = SouffleSubgoal(randomness=self.randomness, arity=0, params=self.params)
                    parsed_subgoal.parse_subgoal_declaration(line)
                    self.add_log_text("\tParsing subgoal: " + line + "   Arity: " + str(parsed_subgoal.get_arity()))
                    # Add parsed subgoal in the list of all available relations
                    # Add the new type used in the subgoal(if any)
                    if parsed_subgoal.get_arity() != 0:
                        self.all_relations.append(parsed_subgoal)
                        # ADD types used in the subgoal to allowed types    
                        for _type in parsed_subgoal.get_types():
                            if _type not in self.allowed_types: self.allowed_types.append(_type)
                    continue
                # Input ?
                if line.find(".input") != -1:
                    self.inputs.append(line + "  //Parsed entity")
                    continue
                # Rule definition ?       
                if line.find(":-") != -1:
                    parsed_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
                    parsed_rule.set_string(line + "     //parsed rule")
                    self.all_rules.append(parsed_rule)  
                    continue
                # Comment OR empty line OR outout
                if line[0:2] == "//" or line == "" or line.find(".output") != -1:
                    continue
                # Otherwise it is probably a fact. #TODO: make sure this is the case
                self.other_things.append(line + " //Parsed entity")


    def generate_cycle_breaker_rules(self):
        """
            Cycle breakers have only facts in their bodies. 
            They are only used in heads of mixed rules.
            They can contain predicates / aggregates / negations etc
        """
        if self.number_of_mixed_rules == 0: return 0 # No need for cycle breakers in this case
        for i in range(self.number_of_cycle_breaker_rules):
            # Generate a normal rule
            cycle_breaker_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            cycle_breaker_rule.generate_random_rule(ruleType="cycle breaker", allowed_types=self.allowed_types, available_relations=self.all_relations)
            #cycle_breaker_rule.add_negated_subgoals(available_relations=self.all_relations)
            #cycle_breaker_rule.generate_predicates()
            # Add the rule in the program. We will not add in all_relations for the moment.
            self.declarations.append(cycle_breaker_rule.get_declaration())
            self.all_rules.append(cycle_breaker_rule)
            self.cycle_breakers.append(cycle_breaker_rule.get_head())

    def generate_mixed_rules(self):
        """
            negations
            operations in the subgoals
            multiple heads
            arithematic operations in the body (predicates)
            Aggregates
        """
        # Generate a normal rule and add negations, predicates, aggregates, multi-heads
        for i in range(self.number_of_mixed_rules):
            # Generate a normal rule
            mixed_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            mixed_rule.generate_random_rule(ruleType="mixed", allowed_types=self.allowed_types, available_relations=self.all_relations)
            mixed_rule.add_negated_subgoals(available_relations=self.all_relations)
            mixed_rule.generate_predicates()
            mixed_rule.insert_operations_in_head()
            aggregate = SouffleAggregate(parent_rule=mixed_rule, 
                                            verbose=self.verbose, 
                                            randomness=self.randomness, 
                                            params=self.params,
                                            allowed_types=self.params["souffle_types"],
                                            available_relations=self.all_relations)
            if self.params["aggregate"]: mixed_rule.add_aggregate(aggregate.get_string())
            mixed_rule.generate_heads(non_cyclic_relations=self.cycle_breakers)
            # Generate a couple of disjunctive rules
            disjunctive_rules = list()
            for j in range(self.randomness.get_random_integer(0, self.params["max_number_of_disjunctions"])):
                dis_mixed_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
                dis_mixed_rule.generate_disjunctive_rule(parent_rule=mixed_rule, available_relations=self.all_relations)
                dis_mixed_rule.add_negated_subgoals(available_relations=self.all_relations)
                dis_mixed_rule.generate_predicates()
                dis_mixed_rule.insert_operations_in_head()
                aggregate = SouffleAggregate(parent_rule=dis_mixed_rule, 
                                                verbose=self.verbose, 
                                                randomness=self.randomness, 
                                                params=self.params,
                                                allowed_types=self.params["souffle_types"],
                                                available_relations=self.all_relations)
                if self.params["aggregate"]: dis_mixed_rule.add_aggregate(aggregate.get_string())
                disjunctive_rules.append(dis_mixed_rule)
            # Add information about this rule in the program
            self.declarations.append(mixed_rule.get_declaration())
            self.all_relations.append(deepcopy(mixed_rule.get_head()))
            self.all_rules.append(mixed_rule)
            self.all_rules = self.all_rules + disjunctive_rules
        # Cycle breaker relations are now available to be used in the body of rules.
        self.all_relations = self.all_relations + self.cycle_breakers

    def generate_complex_rules(self):
        """
            negations
        """
        # Generate a normal rule and add some negations. 
        # It should be a safe negation. With all the grounded variables etc
        for i in range(self.number_of_complex_rules):
            # Generate a normal rule
            complex_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            complex_rule.generate_random_rule(ruleType="complex", allowed_types=self.allowed_types, available_relations=self.all_relations)
            # Add negated subgoals in the complex rule
            # we pick a subgoal from the available relations and then we negate them 
            complex_rule.add_negated_subgoals(available_relations=self.all_relations)
            # Generate a couple of disjunctive rules
            disjunctive_rules = list()
            for j in range(self.randomness.get_random_integer(0, self.params["max_number_of_disjunctions"])):
                dis_complex_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
                dis_complex_rule.generate_disjunctive_rule(parent_rule=complex_rule, available_relations=self.all_relations)
                dis_complex_rule.add_negated_subgoals(available_relations=self.all_relations)
                disjunctive_rules.append(dis_complex_rule)
            # Add information about this rule in the program
            self.declarations.append(complex_rule.get_declaration())
            self.all_relations.append(deepcopy(complex_rule.get_head()))
            self.all_rules.append(complex_rule)
            # Add disjuntive rules in the set of all rules 
            self.all_rules = self.all_rules + disjunctive_rules


    def generate_simple_rules(self):
        """
            Simplest possible rules
        """
        # Generate simple rules
        for i in range(self.number_of_simple_rules):
            rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
            rule.generate_random_rule(ruleType="simple", allowed_types=self.allowed_types, available_relations=self.all_relations)
            # Generate a couple of disjunctive rules
            disjunctive_rules = list()
            for j in range(self.randomness.get_random_integer(0, self.params["max_number_of_disjunctions"])):
                dis_simple_rule = SouffleRule(verbose=self.verbose, randomness=self.randomness, params=self.params)
                dis_simple_rule.generate_disjunctive_rule(parent_rule=rule, available_relations=self.all_relations)
                disjunctive_rules.append(dis_simple_rule)
            # Add information about this rule in the program
            self.declarations.append(rule.get_declaration())
            self.all_relations.append(deepcopy(rule.get_head()))
            self.all_rules.append(rule)
            # Add disjuntive rules in the set of all rules 
            self.all_rules = self.all_rules + disjunctive_rules


    def generate_facts(self):
        # Generate fact tables
        for i in range(self.number_of_facts):
            fact_table = SouffleFact(randomness=self.randomness, params=self.params)
            # Add information about this fact table in the program
            self.declarations.append(fact_table.get_decleration())
            self.facts.append(fact_table)
            self.all_relations.append(fact_table.get_fact_as_a_relation())
            if self.params["in_file_facts"] is False: self.inputs.append(fact_table.get_fact_input_string())


    def pretty_print_program(self):
       
        for decl in self.type_declarations: print(colored(decl, "green", attrs=["bold"]))
        print("\n\n")
        
        for decl in self.declarations: print(colored(decl, "red", attrs=["bold"]))
        print("")
        
        for _input in self.inputs: print(colored(_input, "green", attrs=["bold"]))
        print("")

        print(colored( ".output " + self.output_rule.get_head().get_name(), "green", attrs=["bold"]))   
        
        print("\n\n")
        if self.params["in_file_facts"]:
            for fact in self.facts:
                for row in fact.get_fact_data(): print(colored(row, "yellow", attrs=["bold"]))
            print("")
        
        for thing in self.other_things:
            print(colored(thing, "yellow", attrs=["bold"]))
        
        print("")
        for rule in self.all_rules:
            rule_string = deepcopy(rule.get_string())

            # Parsed rule
            if rule_string.find("parsed rule") != -1:
                rule_string = rule_string.replace("//parsed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//parsed rule", "green", attrs=["bold"]))

            # Cycle breaker rule
            if rule_string.find("cycle breaker rule") != -1:
                rule_string = rule_string.replace("//cycle breaker rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//cycle breaker rule", "red", attrs=["bold"]))

            # Mixed rule
            if rule_string.find("mixed rule") != -1:
                rule_string = rule_string.replace("//mixed rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//mixed rule", "magenta", attrs=["bold"]))

            # Complex rule
            if rule_string.find("complex rule") != -1:
                rule_string = rule_string.replace("//complex rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//complex rule", "red", attrs=["bold"]))

            # Simple rule
            if rule_string.find("simple rule") != -1:
                rule_string = rule_string.replace("//simple rule", "")
                print(colored(rule_string, "blue", attrs=["bold"]), end="")
                print(colored("//simple rule", "green", attrs=["bold"]))

            # Transformed rule
            if rule_string.find("transformed rule") != -1:
                print(colored(rule_string, "yellow", attrs=["bold"]))


    def create_program_string(self):
        """
            Souffle program structure:
                declarations
                facts
                rule definitions  
                output declaration  
        """
        # type declaration
        for type_decl in self.type_declarations:
            self.program_string += type_decl + "\n"

        # declarations
        for decl in self.declarations:
            self.program_string += decl + "\n"
        
        self.program_string += "\n\n"
        # Inputs
        for _input in self.inputs:
            self.program_string += _input + "\n"

        # facts (only when in_file_facts is true)
        if self.params["in_file_facts"]:
            self.program_string += "\n\n"
            for fact in self.facts:
                for row in fact.get_fact_data():
                    self.program_string += row + "\n"

        # other things that are kinda hard to parse
        for thing in self.other_things:
            self.program_string += thing + "\n"

        # rule definitions
        self.program_string += "\n\n"
        for rule in self.all_rules:
            self.program_string += rule.get_string() + "\n"
        # output
        self.program_string += "\n" + ".output " + self.output_rule.get_head().get_name() + "\n"

    def add_transformation_information(self, oracle):
        self.program_string = "// TRANSFORMED PROGRAM\n"
        self.program_string += "// Oracle: " + oracle + " \n\n"

    def export_program_string(self, core_path):
        """
            Export original program string
        """
        
        self.program_path = os.path.join(core_path, "program_" + str(self.program_number))
        self.program_file_path = os.path.join(self.program_path, "orig_rules.dl")
        self.logs.set_log_file_name("orig.log")
        self.logs.set_log_file_path(self.program_path)
        os.mkdir(self.program_path)
        create_file(self.program_string, self.program_file_path)
        
        # Create .facts file here as well
        if self.params["in_file_facts"] is False:
            for fact in self.facts: 
                fact.generate_fact_file(self.program_path)


    def export_transformed_program_string(self, transformation_number):
        """
            Export transformed program string
        """
        self.program_file_path = os.path.join(self.program_path, "transformed_rules_" + str(transformation_number) + ".dl")
        self.logs.set_log_file_name("transformed_rules_" + str(transformation_number) + ".log")
        create_file(self.program_string, self.program_file_path)