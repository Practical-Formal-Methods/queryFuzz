from queryfuzz.datalog.base_predicate import BasePredicate

class Z3Predicate(BasePredicate):
    def generate_number_predicate(self):
        operations = ["=", "!=", "<", ">"]
        operand_1 = self.randomness.random_choice([self.randomness.random_choice([i.get_name() for i in self.variables]), str(self.randomness.get_random_integer(0,100))])
        operation = self.randomness.random_choice(operations)
        operand_2 = self.randomness.random_choice([i.get_name() for i in self.variables])
        self.string = operand_1 + " " + operation + " " + operand_2

    def generate_predicate(self):
        self.generate_number_predicate()