from queryfuzz.datalog.base_fact import BaseFact
from queryfuzz.engines.ddlog.ddlog_subgoal import DDlogSubgoal
from queryfuzz.datalog.variable import Variable
import string

class DDlogFact(BaseFact):

    def generate_fact(self):
        self.arity = 1 # ATTENTION: arity in DDLOG rules is always 1. Maybe fix that later
        allowed_variable_types = self.params["ddlog_types"]
        self.name = self.randomness.get_upper_case_alpha_string(4)
        self.variables_types = [self.randomness.random_choice(allowed_variable_types) for i in range(self.arity)]
        # Generate rows
        for i in range(self.number_of_rows):
            table_entry = "insert " + self.name + "("
            raw_data_row = ""
            for j in range(self.arity):
                data_type = self.variables_types[j]
                data_item = self.generate_data_item(data_type)
                table_entry += str(data_item) + ", "
                raw_data_row += str(data_item) + "\t"
            table_entry = table_entry[:-2] + "),"
            self.raw_data_entries.append(raw_data_row)
            self.fact_data.append(table_entry)
        # Last entry should end with a semi colon
        self.fact_data[-1] = self.fact_data[-1][:-1] + ";"

    def get_fact_as_a_relation(self):
        fact_subgoal = DDlogSubgoal(randomness=self.randomness, arity=self.arity, params=self.params)
        fact_subgoal.generate_subgoal(name=self.name, 
                                        variables=[Variable(name=string.ascii_lowercase[i], vtype=self.variables_types[i]) for i in range(self.arity)], 
                                        variables_types=self.variables_types)
        return fact_subgoal

    def generate_decleration(self):
        self.declaration = "input relation " + self.name + "("
        for i in range(self.arity):
            self.declaration += string.ascii_lowercase[i] + ":" + self.variables_types[i] + ", "
        self.declaration = self.declaration[:-2] + ")"

    def generate_data_item(self, type):
        if type == "string":
            return '"' + self.randomness.get_random_alpha_numeric_string(1) + '"'