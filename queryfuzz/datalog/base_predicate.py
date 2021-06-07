from abc import ABC, abstractmethod

class BasePredicate(object):
    def __init__(self, variables, randomness):
        self.randomness = randomness
        self.variables = variables      # Type: List of var() objects
        self.string = ""                # Type: string
        self.generate_predicate()               

    @abstractmethod
    def generate_predicate(self):
        pass

    def get_string(self):
        return self.string