from termcolor import colored
import string
from queryfuzz.datalog.variable import Variable
from copy import deepcopy
import re

class cqtTransformer(object):
    def __init__(self, randomness, verbose, params, rule, transformed_program):
        self.randomness = randomness
        self.verbose = verbose
        self.params = params
        self.rule = rule
        self.transformed_program = transformed_program
    
    def apply_transformation_sequence(self, transformation_sequence):
        for transformation in transformation_sequence:
            if transformation == "ADD_EQU":
                print(colored(" [ADD_EQU]", "blue"), end="")
                self.ADD_EQU()
            if transformation == "ADD_CON":
                print(colored(" [ADD_CON]", "blue"), end="")
                self.ADD_CON()
            if transformation == "MOD_EXP":
                print(colored(" [MOD_EXP]", "blue"), end="")
                self.MOD_EXP()
            if transformation == "MOD_CON":
                print(colored(" [MOD_CON]", "blue"), end="")
                self.MOD_CON()
            if transformation == "MOD_EQU":
                print(colored(" [MOD_EQU]", "blue"), end="")
                self.MOD_EQU()
            if transformation == "REM_EXP":
                print(colored(" [REM_EXP]", "blue"), end="")
                self.REM_EXP()
            if transformation == "REM_EQU":
                print(colored(" [REM_EQU]", "blue"), end="")
                self.REM_EQU()

            self.transformed_program.add_log_text("\n\t\t\t  |  ")
            self.transformed_program.add_log_text("\t\t\t  |  [" + transformation + "]")
            self.transformed_program.add_log_text("\t\t\t  V  \n")
            self.transformed_program.add_log_text("\tTRANS RULE:  " + self.rule.get_string())

    # Helper functions -------------------------------------

    def generate_fresh_var(self, present_vars):
        """
            Returns a variable var name, which is not in present_vars.
        """
        collection_of_variables = [i for i in string.ascii_uppercase] + [i+i for i in string.ascii_uppercase] + [i+i+i for i in string.ascii_uppercase]
        for var in collection_of_variables:
            if var not in [i.get_name() for i in present_vars]:
                return var


    def check_rule_validity(self, rule):
        """
            Returns False if: 
                all head variables are not conatined in atleast one postive subgoal
                all variables in all negative subgoals are not contained in atleast one postive subgoal
        """
        positive_subgoal_indexes = [i for i,j in enumerate(rule.get_real_subgoals()) if not j.is_negated()]
        negative_subgoal_indexes = [i for i,j in enumerate(rule.get_real_subgoals()) if j.is_negated()]
        #print(colored("\t\tNegative subgoal indexes ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(negative_subgoal_indexes, "cyan", attrs=["bold"]))
        positive_body_variables = list()
        for i in positive_subgoal_indexes:
            positive_body_variables += [j.get_name() for j in rule.get_real_subgoals()[i].get_variables()]
        negative_body_variables = list()
        for i in negative_subgoal_indexes:
            negative_body_variables += [j.get_name() for j in rule.get_real_subgoals()[i].get_variables()]
        for var in negative_body_variables:
            if var not in positive_body_variables:
                #print(colored("\t\tERROR: NEGATIVE VARIABLE " + head_var.get_name() + " is not in any postive subgoal!", "white", "on_red", attrs=["bold"]) )
                return False
        for head_var in rule.get_head().get_variables():
            if head_var.get_name() not in positive_body_variables:
                #print(colored("\t\tERROR: Variable " + head_var.get_name() + " is not in any postive subgoal!", "red", attrs=["bold"]) )
                return False
        return True


    # Helper functions end -------------------------------------
    def ADD_EQU(self):
        """
            Preserves the results of the original query while adding a new sub-goal
            The key idea behind this transformation is the following:
            When we add a new sub_goal (new_sub) to Q_orig, we make sure that there is
            a containment map from Q_trans to Q_orig. We know that in case of ADD, a
            containment map always exist from Q_orig to Q_trans. So just constructing
            a containment map from Q_trans to Q_orig will make the two queries equivalent.
        """
        #if self.verbose: print(colored("\n\t\toriginal rule ->  ", "blue", attrs=["bold"]), end="")
        #if self.verbose: print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        # Pick a positive random subgoal from the rule
        new_sub = self.rule.get_a_random_positive_subgoal()
        #if self.verbose: print(colored("\t\tpicked subgoal ->  ", "blue", attrs=["bold"]), end="")
        #if self.verbose: print(colored(new_sub.get_string(), "cyan", attrs=["bold"]))
        present_vars = self.rule.get_all_variables()
        for i, var in enumerate(new_sub.get_variables()):
            if self.randomness.flip_a_coin():
                fresh_var_name = self.generate_fresh_var(present_vars)
                fresh_var_type = var.get_type()
                fresh_var = Variable(fresh_var_name, fresh_var_type)
                new_sub.update_variable_at_location(fresh_var, i)
                self.rule.update_string()
                present_vars.append(fresh_var)
        #if self.verbose: print(colored("\t\tNew subgoal ->  ", "blue", attrs=["bold"]), end="")
        #if self.verbose: print(colored(new_sub.get_string(), "cyan", attrs=["bold"]))
        self.rule.append_subgoal(new_sub)
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))

    def ADD_CON(self):
        """
            Contracts the results of the original query by adding a new sub-goal.
            When we add a new subgoal, we make sure that there is a containment map from Q_orig to 
            Q_trans. Intuitively, ADD_CON adds a new subgoal to Q_orig which introduces new joins.
        """
        #print(colored("\n\t\toriginal rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        # Pick a positive random subgoal from the set of all relations
        new_sub = self.randomness.random_choice(self.transformed_program.get_all_relations())
        #print(colored("\t\tpicked subgoal ->  ", "blue", attrs=["bold"]), end="")
        #print(colored(new_sub.get_string(), "cyan", attrs=["bold"]))
        newly_added_variables = list()
        for i,var in enumerate(new_sub.get_variables()):
            var_type = var.get_type()
            variable_options = self.rule.get_body_variables_of_type(var_type)
            new_var = None
            if len(variable_options) == 0:
                # Create a new variable
                fresh_var_name = self.generate_fresh_var(self.rule.get_all_variables() + newly_added_variables)
                new_var = Variable(fresh_var_name, var_type)
                newly_added_variables.append(new_var)
            else:
                new_var = self.randomness.random_choice(variable_options)
            new_sub.update_variable_at_location(new_var, i)
        #print(colored("\t\tNEW subgoal ->  ", "blue", attrs=["bold"]), end="")
        #print(colored(new_sub.get_string(), "cyan", attrs=["bold"]))
        if self.rule.get_string().find(new_sub.get_string()) != -1:
            #print(colored("\t\tThis subgoal is already present! Not adding in the rule", "red", attrs=["bold"]))
            a=0
        else:
            #print(colored("\t\tSTRING NOT FOUND! Adding in the rule", "green", attrs=["bold"]))
            self.rule.append_subgoal(new_sub)
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))


    def MOD_EXP(self):
        """
            Expands the results of Q_orig by modifying 'a single' subgoal in Q_orig.
            The modification is renaming a variable in a subgoal.
            The varialble should appear more than once in the body of the rule.
            When this variable is replaced with a fresh variable, we will have a mapping 
            from Q_trans to Q_orig but no mapping from Q_orig to Q_trans. Thus expanding the result.
        """

        #print(colored("\n\t\toriginal rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        
        # find a variable that appears more than once in the body consisting of only positive subgoals
        positive_subgoals = [i for i in self.rule.get_real_subgoals() if not i.is_negated()]
        all_vars = list()
        for sub in positive_subgoals:
            all_vars += sub.get_variables()
        multi_variables = list(set([i for i in [j.get_name() for j in all_vars] if [j.get_name() for j in all_vars].count(i) > 1])) 
        multi_variables.sort()  # Because set() messes up the randomness
        if len(multi_variables) == 0:
            #print("\n\t\t ABORT MOD_EXP")
            #print(colored("\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
            #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
            return 1
        
        picked_variable = self.randomness.random_choice(multi_variables)
        #print(colored("\t\tMulti variables ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(multi_variables, "cyan", attrs=["bold"]))
        #print(colored("\t\tPicked variable ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(picked_variable, "cyan", attrs=["bold"]))
        # Find subgoals that contain variables in multi_variables
        subgoal_options = list()
        for sub in positive_subgoals:
            if picked_variable in [i.get_name() for i in sub.get_variables()]:
                subgoal_options.append(sub) # Storing the actual subgoals. not their copies
        picked_subgoal = self.randomness.random_choice(subgoal_options)
        #print(colored("\t\tPicked Subgoal ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(picked_subgoal.get_string(), "cyan", attrs=["bold"]))
        variable_indices = [i for i in range(len(picked_subgoal.get_variables())) if picked_subgoal.get_variables()[i].get_name() == picked_variable]
        #print(colored("\t\tIndices for this variable ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(variable_indices, "cyan", attrs=["bold"]))
        chosen_index = self.randomness.random_choice(variable_indices)
        fresh_var = Variable(self.generate_fresh_var(self.rule.get_all_variables()), picked_subgoal.get_variables()[chosen_index].get_type())
        picked_subgoal.update_variable_at_location(fresh_var, chosen_index)
        #print(colored("\t\tFresh var ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(fresh_var.get_name(), "cyan", attrs=["bold"]))
        #print(colored("\t\tNew subgoal ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(picked_subgoal.get_string(), "cyan", attrs=["bold"]))
        self.rule.update_string()
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))

    def MOD_CON(self):
        """
            Contracts the result of Q_orig by modifying 'all occurrances' of a single variable in 
            Q_orig. 
            If there is only one variable of a particular type in the body, then we cannot do anything and we just return.
            Otherwise we pick a random variable and replace it with another variable. 
        """
        #print(colored("\n\t\tOriginal rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        # Get distinct variables set in the rule
        variables_set = list() # List containing variable objects
        for var in self.rule.get_all_variables(): 
            if var.get_name() not in [i.get_name() for i in variables_set]: 
                variables_set.append(var)
        #print(colored("\t\tVariables set ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored([i.get_name() for i in variables_set], "cyan", attrs=["bold"]))
        # Count the number of distinct variables for each type
        count_dict = dict()
        for var in variables_set:
            if var.get_type() in count_dict.keys():
                count_dict[var.get_type()] += 1
            else:
                count_dict[var.get_type()] = 1
        # Pick a variable of a type which has more than one occurings
        types_used_in_rule = list(count_dict.keys())
        types_used_in_rule.sort()
        #print(colored("\t\tTypes used in rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(types_used_in_rule, "cyan", attrs=["bold"]))
        for _type in types_used_in_rule:
            if count_dict[_type] > 1:
                # Pick a variable of this type. 
                variables_of_this_type = [i.get_name() for i in [j for j in variables_set if j.get_type() == _type]]
                #print(colored("\t\tVariables of this type ->  ", "magenta", attrs=["bold"]), end="")
                #print(colored(variables_of_this_type, "cyan", attrs=["bold"]))
                picked_variable = self.randomness.random_choice(variables_of_this_type)
                #print(colored("\t\tPicked variable ->  ", "magenta", attrs=["bold"]), end="")
                #print(colored(picked_variable + " : " + _type, "cyan", attrs=["bold"]))
                # replace it with a variable of a different name but of the same type
                new_variable = deepcopy(self.randomness.random_choice([i for i in [j for j in variables_set if j.get_type() == _type and j.get_name() != picked_variable]]))
                #print(colored("\t\tNew variable ->  ", "magenta", attrs=["bold"]), end="")
                #print(colored(new_variable.get_name() + " : " + _type, "cyan", attrs=["bold"]))
                # Replace all occurences of picked_variable variable with new_variable including the head.
                for sub in self.rule.get_real_subgoals() + [self.rule.get_head()]:
                    for i, var in enumerate(sub.get_variables()):
                        if var.get_name() == picked_variable: sub.update_variable_at_location(new_variable, i)
                self.rule.update_string()
                # If we were successful in this modification, then we exit
                #print(colored("\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
                #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
                #print(colored("success", "green"))
                return 0
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))


    def MOD_EQU(self):
        # Pick a variable name.
        # TODO: Properly test this befor pushing this
        picked_variable_name = self.randomness.random_choice(self.rule.get_variable_names_as_a_set())
        new_variable_name = self.generate_fresh_var(self.rule.get_all_variables())
        for sub in self.rule.get_real_subgoals() + [self.rule.get_head()]:
            for i, var in enumerate(sub.get_variables()):
                if var.get_name() == picked_variable_name:
                    new_variable = Variable(new_variable_name, var.get_type())
                    sub.update_variable_at_location(new_variable, i)
        self.rule.update_string()


    def REM_EXP(self):
        """
            Expands the result of Q_orig by removing a subgoal. When we remove a subgoal, there is
            always a containment map from Q_trans to Q_orig but not necessarily in the other directions. 
            The absence of a containment map in the other direction expands the result.
        """
        #print(colored("\n\t\tOriginal rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        # randomly pick a positive subgoal from the body
        rule_copy = deepcopy(self.rule)
        positive_subgoal_indexes = [i for i,j in enumerate(rule_copy.get_real_subgoals()) if not j.is_negated()]
        if len(positive_subgoal_indexes) <=1:
            return 1 
        #print(colored("\t\tPositive subgoal indexes ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(positive_subgoal_indexes, "cyan", attrs=["bold"]))
        remove_index = self.randomness.random_choice(positive_subgoal_indexes)
        #print(colored("\t\tRemoval index ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(remove_index, "cyan", attrs=["bold"]))
        del rule_copy.get_real_subgoals()[remove_index]
        rule_copy.update_string()
        #print(colored("\t\tTransformed rule copy->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(rule_copy.get_string(), "cyan", attrs=["bold"]))
        # remove it and check if the rule is still valid. 
        if self.check_rule_validity(rule_copy):
            #print(colored("\t\tThe rule is valid!", "green", attrs=["bold"]))
            del self.rule.get_real_subgoals()[remove_index]
            self.rule.update_string()
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))

    def exists_containment(self, Q_orig, Q_trans, subgoal):
        """
            Returns True if 'subgoal' can be mapped to any subgoal in Q_trans.
        """
        def refresh_cache(rm_vars):
            removed_var_cache = dict()
            for var in rm_vars:
                removed_var_cache[var] = None
            return removed_var_cache
        Q_trans_string = Q_trans.get_string().replace(" ", "")
        original_variables = Q_orig.get_variable_names_as_a_set()
        transformed_rule_variables = Q_trans.get_variable_names_as_a_set()
        removed_variables = [i for i in original_variables if i not in transformed_rule_variables]
        original_variables.sort()
        transformed_rule_variables.sort()
        removed_variables.sort()
        # Replace the variable in the removed subgoal with a wild card.
        original_removed_subgoal_string = deepcopy(subgoal.get_string()).replace(" ", "")
        #print(colored("\t\tCan this subgoal be mapped ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(subgoal.get_string(), "cyan", attrs=["bold"]))
        #print(colored("\t\tTo any subgoal in this rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(Q_trans_string, "cyan", attrs=["bold"]))
        #print(colored("\t\tREMOVED VARIABLES ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(removed_variables, "cyan", attrs=["bold"]))
        # If that subgoal is not present in Q_trans, then NO
        if subgoal.get_name() not in [i.get_name() for i in Q_trans.get_real_subgoals() if not i.is_negated()]:
            #print(colored("\t\tNO!  The subgoal is not even in Q_trans", "red", attrs=["bold"]))
            return False
        # If we reached here that means we have atlest one subgoal with the same name.
        # For each positive subgoal in Q_trans, check if "subgoal" can be mapped to it or not ?
        for pos_subgoal in [i for i in Q_trans.get_real_subgoals() if not i.is_negated() and i.get_name() == subgoal.get_name()]:
            #print(colored("\t\t" + subgoal.get_string(), "red", attrs=["bold"]), end="")
            #print(colored("      <-->   " + pos_subgoal.get_string(), "red", attrs=["bold"]))
            removed_var_cache = refresh_cache(removed_variables)
            match = True
            # compare all variables in subgoal with each variable in pos_subgoal
            for i, var in enumerate([i.get_name() for i in subgoal.get_variables()]):
                if var in removed_variables and removed_var_cache[var] is None:
                    removed_var_cache[var] = pos_subgoal.get_variables()[i].get_name()
                    continue
                if var in removed_variables and removed_var_cache[var] != pos_subgoal.get_variables()[i].get_name():
                    # No need to even continue with this subgoal. We break out of this subgoal loop
                    match = False
                    #print(colored("\t\t\tNO! You are trying to map one varibale to muliple variables !", "red", attrs=["bold"]))
                    break
                if var != pos_subgoal.get_variables()[i].get_name():
                    match = False
                    #print(colored("\t\t\tNO! not possible !", "red", attrs=["bold"]))
                    break
            if match: 
                #print(colored("\t\tYES!", "green", attrs=["bold"]))
                return True
        # It has passed all the checks. 
        #print(colored("\t\tNO!", "red", attrs=["bold"]))
        return False


    def REM_EQU(self):
        """
            Preserves the result of Q_orig while removing a sub-goal and making sure that there is a containment map
            from Q_orig to Q_trans.
        """
        #print(colored("\n\t\tOriginal rule ->     ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
        # Pick a positive subgoal from the original rule.
        rule_copy = deepcopy(self.rule)
        positive_subgoal_indexes = [i for i,j in enumerate(rule_copy.get_real_subgoals()) if not j.is_negated()]
        if len(positive_subgoal_indexes) <= 1:
            #print(colored("\t\tRule too short", "red", attrs=["bold"]))
            return 1 
        remove_index = self.randomness.random_choice(positive_subgoal_indexes)
        #print(colored("\t\tRemoved subgoal ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(rule_copy.get_real_subgoals()[remove_index].get_string(), "cyan", attrs=["bold"]))
        del rule_copy.get_real_subgoals()[remove_index]
        rule_copy.update_string()
        #print(colored("\t\tTransformed rule 1 ->", "magenta", attrs=["bold"]), end="")
        #print(colored(rule_copy.get_string(), "cyan", attrs=["bold"]))
        # remove it and check if the rule is still valid. 
        if self.check_rule_validity(rule_copy):
            # Check if the deleted subgoal can be mapped to any POSITIVE subgoal in rule_copy. 
            if self.exists_containment(self.rule, rule_copy, self.rule.get_subgoals()[remove_index]):
                del self.rule.get_real_subgoals()[remove_index]
                self.rule.update_string()
        else:
            #print(colored("\t\tRule not valid", "red", attrs=["bold"]))
            pass
        #print(colored("\n\t\tTransformed rule ->  ", "magenta", attrs=["bold"]), end="")
        #print(colored(self.rule.get_string(), "cyan", attrs=["bold"]))
