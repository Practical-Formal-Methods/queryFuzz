from abc import ABC, abstractmethod
from queryfuzz.datalog.base_subgoal import BaseSubgoal
from queryfuzz.datalog.variable import Variable
import string

class BaseFact(object):
    def __init__(self, randomness, params):
        self.name = ""
        self.randomness = randomness
        self.params = params
        self.declaration = ""
        self.fact_data = list()         # Fact rows
        self.variables_types = list()    
        self.raw_data_entries = list()  # Raw data entries for the facts file

        # Parameters
        self.arity = self.randomness.get_random_integer(1, params["max_fact_arity"])
        self.number_of_rows = self.randomness.get_random_integer(1, params["max_number_of_fact_rows"])

        # Generate engine specific fact
        self.generate_fact()
        self.generate_decleration()


    @abstractmethod
    def generate_fact(self):
        pass

    @abstractmethod
    def generate_decleration(self):
        pass

    @abstractmethod
    def get_fact_input_string(self):
        pass

    @abstractmethod
    def get_fact_as_a_relation(self):
        pass

    @abstractmethod
    def generate_fact_file(self, export_location):
        pass

    def get_decleration(self):
        return self.declaration

    def get_fact_data(self):
        return self.fact_data