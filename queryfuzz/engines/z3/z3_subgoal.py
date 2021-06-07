from queryfuzz.datalog.base_subgoal import BaseSubgoal

class Z3Subgoal(BaseSubgoal):
    def negate_subgoal(self):
        self.negated = True
        self.string = "!" + self.string