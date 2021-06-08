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
from queryfuzz.utils.file_operations import read_file
import string
import os
from queryfuzz.utils.file_operations import create_file, export_buggy_instance_for_soundness


def generate_comparison_queries(output_relation, original_result, transformed_result, oracle, program_path, transformation_number, type_decls, engine):
    # Type declarations will be needed in the future
    # Determine the types of the attributes in the result files
    type_declarations = ""
    for type_decl in type_decls:
        type_declarations += type_decl + "\n"
    if engine == "z3":
        type_declarations = ".type Z <: number"
    if engine == "ddlog":
        type_declarations = ".type string <: symbol"

    # original result declaration string
    orig_result_decl_string = ".decl orig_result("
    for i,var in enumerate(output_relation.get_variables()):
        orig_result_decl_string += string.ascii_uppercase[i] + ":" + var.get_type() + ", "
    orig_result_decl_string = orig_result_decl_string[:-2] + ")"
    # import original results
    orig_result_input = '.input orig_result(filename="' + original_result + '")'
    # Transformed result declaration string
    trans_result_decl_string = orig_result_decl_string.replace("orig_result", "trans_result")
    # import transformed result
    trans_result_input = '.input trans_result(filename="' + transformed_result + '")'
    variable_string = "".join(i + "," for i in string.ascii_lowercase[:output_relation.get_arity()])[:-1]
    # Comparison query 1
    comp_decl_string_1 = orig_result_decl_string.replace("orig_result", "comparison_result1")
    query_1 = "comparison_result1(" + variable_string + ") :- orig_result(" + variable_string + ") , !trans_result(" + variable_string + ")." 
    # Comparison query 2
    comp_decl_string_2 = orig_result_decl_string.replace("orig_result", "comparison_result2")
    query_2 = "comparison_result2(" + variable_string + ") :- trans_result(" + variable_string + ") , !orig_result(" + variable_string + ")." 

    # Final query string
    query_file_string = type_declarations
    query_file_string += "\n\n// Original result\n" + orig_result_decl_string + "\n" + orig_result_input
    query_file_string += "\n\n// Transformation result\n" + trans_result_decl_string + "\n" + trans_result_input
    query_file_string += "\n\n\n\n// Comparison query 1\n" + comp_decl_string_1 + "\n" + query_1
    query_file_string += "\n\n// Comparison query 2\n" + comp_decl_string_2 + "\n" + query_2
    query_file_string += "\n\n\n\n.output comparison_result1\n.output comparison_result2"

    comparison_query_path = ""
    if oracle == "EQU":
        query_file_string += "\n\n\n// EQU QUERY \n// comparison_results1 should always be empty \n// comparison_results2 should always be empty\n"
        comparison_query_path = os.path.join(program_path, "EQU_" + str(transformation_number) + ".dl" )
        create_file(query_file_string, comparison_query_path)
    if oracle == "EXP":
        query_file_string += "\n\n\n// EXP QUERY \n// comparison_results1 SHOULD ALWAYS be empty. Both in case of EXP_EQU and strict EXP transformations" \
                        "  \n// comparison_results2 will be empty in case of EXP_EQU transformation and will not be empty in case of strict EXP transformation\n"
        comparison_query_path = os.path.join(program_path, "EXP_" + str(transformation_number) + ".dl")
        create_file(query_file_string, comparison_query_path)
    if oracle == "CON":
        query_file_string += "\n\n\n// CON QUERY \n// comparison_result1 will NOT be empty in case of strict CON transformation. It will be empty in case of EQU_CON transformation" \
                        "  \n// comparison_results2 SHOULD ALWAYS BE empty. Both in case of CON_EQU and strict CON transformations\n"
        comparison_query_path = os.path.join(program_path, "CON_" + str(transformation_number) + ".dl")
        create_file(query_file_string, comparison_query_path)
    return comparison_query_path


def compare_results(original_result, transformed_result, oracle, verbose, params, animate, output_relation, program_path, transformation_number, seed, new_program, stats, engine):
    """
        original_result: Path to a csv file
        transformed_result: Path to a csv file
        oracle: Transformation type
    """
    def print_results():
        len_orig_result = len(read_file(original_result))
        len_trans_result = len(read_file(transformed_result))

        if animate: print("")
        print("     [" + oracle + "] ", end="")
        if oracle == "EQU":
            if len_orig_result == len_trans_result:
                print(str(len_orig_result) + " == " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " == " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ The above (in)equality holds")
            else:
                print(str(len_orig_result) + " != " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " NOT == " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ WARNING!")

        if oracle == "EXP":
            if len_orig_result <= len_trans_result:
                print(str(len_orig_result) + " <= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " <= " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ The above (in)equality holds")
            else:
                print(str(len_orig_result) + " ! >= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " NOT <= " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ WARNING!")

        if oracle == "CON":
            if len_orig_result >= len_trans_result:
                print(str(len_orig_result) + " >= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u2714', "green", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " >= " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ The above (in)equality holds")
            else:
                print(str(len_orig_result) + " ! <= " + str(len_trans_result) + " ", end="")
                print(colored(u'\u274c', "red", attrs=["bold"]), end="")
                new_program.add_log_text("\t" + str(len_orig_result) + " NOT >= " + str(len_trans_result) + " ")
                new_program.add_log_text("\t^^^^^^ WARNING!")

        new_program.dump_program_log_file()
        if len_orig_result != len_trans_result:
            return True
        else:
            return False

        new_program.add_log_text(" ===================== ")
        new_program.add_log_text("   Comparing Results  ")
        new_program.add_log_text(" ===================== ")
    new_result = print_results()

    # Generate comparison query
    comparison_query_path = generate_comparison_queries(output_relation, original_result, transformed_result, oracle, program_path, transformation_number, new_program.get_type_declarations(), engine)
    
    # Run comparison query
    command = "timeout 500s " + params["path_to_souffle_engine"] + " -w --output-dir=" + program_path + " " + comparison_query_path
    os.system(command)

    # Compare results
    path_to_compairson_result_1 = os.path.join(program_path, "comparison_result1.csv")
    path_to_compairson_result_2 = os.path.join(program_path, "comparison_result2.csv")
    # If both the files exist then we proceed
    if os.path.exists(path_to_compairson_result_1) and os.path.exists(path_to_compairson_result_2):
        comp_data_1 = read_file(path_to_compairson_result_1)
        comp_data_2 = read_file(path_to_compairson_result_2)
        print("   Comparison query:", end="")
        if oracle == "CON":
            # For CON we need to check that the result of the transformed query is contained the original query
            # The second query should always be empty
            if len(comp_data_2) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                new_program.add_log_text("\tWARNING: Comparison queries say that something is wrong!!!")
                stats.inc_total_trans_soundness_errors()
                new_program.dump_program_log_file()
                stats.dump_data()
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")
        if oracle == "EQU":
            # Both comparison files should be empty
            if len(comp_data_1) != 0 or len(comp_data_2) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                new_program.add_log_text("\tWARNING: Comparison queries say that something is wrong!!!")
                stats.inc_total_trans_soundness_errors()
                new_program.dump_program_log_file()
                stats.dump_data()
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")
        if oracle == "EXP":
            # For EXP, we need to check that the first query is empty
            if len(comp_data_1) != 0:
                print(" " + colored("SOUNDNESS BUG FOUND", "white", "on_red", attrs=["bold"]))
                new_program.add_log_text("\tWARNING: Comparison queries say that something is wrong!!!")
                stats.inc_total_trans_soundness_errors()
                new_program.dump_program_log_file()
                stats.dump_data()
                return 1
            else:
                print(" " + colored(u'\u2714', "green", attrs=["bold"]), end="")
    # Print if we were able to change the result
    if new_result: print("  " + colored("New Result", "white", "on_green", attrs=["bold"]))
    else: print("")
    # Delete comparison results file even if the comparison was unsuccessful. 
    # No need to communicate the failure upstream.
    os.remove(comparison_query_path)
    try: 
        os.remove(os.path.join(program_path, "comparison_result1.csv"))
        os.remove(os.path.join(program_path, "comparison_result2.csv"))
    except:
        print("FAILED TO DELETE")

    