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

from queryfuzz.runner.base_runner import BaseRunner
import subprocess
import os
from termcolor import colored


from termcolor import colored

class SouffleRunner(BaseRunner):

    def generate_command(self, time_out, options):
        command = "timeout -s SIGKILL " + str(time_out) + "s "
        command += self.path_to_engine
        command += " --fact-dir=" + self.program.get_program_path()
        command += " --output-dir=" + self.program.get_program_path()
        command += options
        command += " " + self.program.get_program_file_path()
        return command

    def run_original(self, engine_options):
        self.path_to_engine = self.params["path_to_souffle_engine"]
        
        command_line_options = " -w" + " " + engine_options
        
        # Compiler mode - path for temp CPP file
        if command_line_options.find("-c") != -1:
            command_line_options += " --generate=" + self.program.get_program_path() + "file.cpp"

        command = self.generate_command(time_out=self.params["original_timeout"], options=command_line_options)
        #print(command)
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("  Running Original ")
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()

        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()

        #print(colored(standard_error, "red", attrs=["bold"]))
        error_signal = self.process_standard_error(standard_error=standard_error, file_type="orig")

        self.program.add_log_text("ERROR SIGNAL: " + str(error_signal))
        
        if error_signal != 0:
            self.program.dump_program_log_file()
            return error_signal


        output_file_path = os.path.join(self.program.get_program_path(), self.program.get_output_relation_name() + ".csv")
        
        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            return 1

        # rename original output file with orig.csv
        new_output_file_path = output_file_path.replace(self.program.get_output_relation_name()+".csv", "orig.facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_output_result_path(new_output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()
        return 0
        

    def run_transformed(self, transformation_number, engine_options):
        self.path_to_engine = self.params["path_to_souffle_engine"]
        command_line_options = " -w" + " " + engine_options
        
        # Compiler mode - path for temp CPP file
        if command_line_options.find("-c") != -1:
            command_line_options += " --generate=" + self.program.get_program_path() + "file.cpp"
        
        command = self.generate_command(time_out=self.params["transformed_timeout"], options=command_line_options)
        #print(command)
        self.program.add_log_text(" ===================== ")
        self.program.add_log_text("  Running Transformed ")
        self.program.add_log_text(" ===================== ")
        self.program.add_log_text("\tCommand: " + command)

        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        #print(colored(standard_error, "red", attrs=["bold"]))

        self.program.add_log_text("\n\tSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\n\tSTANDARD OUTPUT: " + standard_output)
        error_signal = self.process_standard_error(standard_error=standard_error, file_type="trans")

        self.program.add_log_text("\tSignal = " + str(error_signal))
        self.program.dump_program_log_file()

        if error_signal != 0:
            self.program.add_log_text(" XXX Something wnet wrong XXX")
            self.program.dump_program_log_file()
            return error_signal

        output_file_path = os.path.join(self.program.get_program_path(), self.program.get_output_relation_name() + ".csv")

        # Check if output file produced
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text(" ERROR. No output file produced !")
            self.program.dump_program_log_file()
            return 1

        # rename original output file with orig.csv
        new_output_file_path = output_file_path.replace(self.program.get_output_relation_name()+".csv", "trans_" + str(transformation_number)+".facts")
        os.rename(output_file_path, new_output_file_path)
        self.program.set_output_result_path(new_output_file_path)
        return 0


    def process_standard_error(self, standard_error, file_type):
        """
            OUTPUT COMMANDS:
                0 : OK
                1 : FATAL ERROR - This can cause the whole system to crash
                2 : RECOVERABLE ERROR - But we will record this. and possibly even the file.
                3 : DONT CARE - An error but we don't care about this
        """
        # KEYWORDS
        if standard_error.find("Redefinition") != -1 or \
            standard_error.find("lxor") != -1 or \
            standard_error.find("lnot") != -1 or \
            standard_error.find("brie") != -1 or \
            standard_error.find("land") != -1 or \
            standard_error.find("bxor") != -1 or \
            standard_error.find("bnot") != -1 or \
            standard_error.find("mean") != -1 or \
            standard_error.find("bshr") != -1 or \
            standard_error.find("true") != -1 or \
            standard_error.find("band") != -1 or \
            standard_error.find("bshl") != -1:
            
            # We don't care about these errors one bit
            if file_type == "orig": self.stats.inc_total_orig_uninteresting_errors()
            if file_type == "trans": self.stats.inc_total_trans_uninteresting_errors()
            return 3

        # TIMEOUT
        if standard_error.find("Killed") != -1:
            print(colored("TIMEOUT", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Timeout")
            # Update stats object
            if file_type == "orig": self.stats.inc_total_orig_timeouts()
            if file_type == "trans": self.stats.inc_total_trans_timeouts()
            return 3    # We don't care about this

        # ASSERTION FAILURE
        if standard_error.find("assertion") != -1 or standard_error.find("Assertion") != -1:
            if standard_error.find("ast2ram/ValueTranslator.cpp:52") != -1 or \
                    standard_error.find("ast2ram/seminaive/ValueTranslator.cpp:47") != -1 or \
                    standard_error.find("ast/transform/MaterializeAggregationQueries.cpp:309") != -1:
                # Known assertion failure in souffle
                print(colored("KNOWN ASSERTION FAILURE", "red", attrs=["bold"]))
                self.program.add_log_text("\tError Type: Known assertion failure")
                if file_type == "orig": self.stats.inc_total_orig_known_assertion_failures()
                if file_type == "trans": self.stats.inc_total_trans_known_assertion_failures()    
                return 3    # We don't care about this
            print(colored("ASSERTION FAILURE", "red", attrs=["bold"]))
            # Update stats object
            self.program.add_log_text("\tError Type: Assertion Failure")
            if file_type == "orig": self.stats.inc_total_orig_assertion_failures()
            if file_type == "trans": self.stats.inc_total_trans_assertion_failures()
            return 2

        if standard_error.find("syntax error") != -1:
            print(colored("SYNTAX ERROR", "red", attrs=["bold"]))
            # Update stats object
            self.program.add_log_text("\tError Type: syntax error")
            if file_type == "orig": self.stats.inc_total_orig_syntax_errors()
            if file_type == "trans": self.stats.inc_total_trans_syntax_errors()
            return 2

        if standard_error.find("Segmentation fault") != -1 or standard_error.find("segmentation fault") != -1:
            print(colored("SEGFAULT", "red", attrs=["bold"]))
            # update stats object
            self.program.add_log_text("\tError Type: Segmentation fault")
            if file_type == "orig": self.stats.inc_total_orig_seg_faults()
            if file_type == "trans": self.stats.inc_total_trans_seg_faults()
            return 3

        # UNGROUNDED VARIABLE ERROR
        if standard_error.find("Error: Ungrounded variable") != -1:
            print(colored("Error: Ungrounded variable", "red", attrs=["bold"]))
            # update stats object
            self.program.add_log_text("\tError Type: Error: Ungrounded variable")
            if file_type == "orig": self.stats.inc_total_orig_unknown_errors()
            if file_type == "trans": self.stats.inc_total_trans_unknown_errors()
            return 3

        if standard_error.find("Floating-point arithmetic exception") != -1:
            print(colored("Floating-point arithmetic exception", "red", attrs=["bold"]))
            # update stats object
            self.program.add_log_text("\tError : Floating-point arithmetic exception")
            if file_type == "orig": self.stats.inc_total_orig_floating_point_exceptions()
            if file_type == "trans": self.stats.inc_total_trans_floating_point_exceptions()
            return 3    # We don't care about this

        if standard_error.find("Unable to stratify") != -1:
            print(colored("unable to stratify error", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Unable to stratify")
            if file_type == "orig": self.stats.inc_total_orig_uninteresting_errors()
            if file_type == "trans": self.stats.inc_total_trans_uninteresting_errors()
            return 3    # We don't care about this

        if standard_error.find("Cannot inline cyclically dependent relations") != -1:
            print(colored("Cannot inline cyclically dependent relations", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: Cannot inline cyclically dependent relations")
            if file_type == "orig": self.stats.inc_total_orig_inline_errors()
            if file_type == "trans": self.stats.inc_total_trans_inline_errors()
            return 3    # We dont care about this

        if standard_error.find("terminate called after throwing an instance of 'std::out_of_range'") != -1:
            print(colored("terminate called after throwing an instance of 'std::out_of_range'", "red", attrs=["bold"]))
            self.program.add_log_text("\tError Type: terminate called after throwing an instance of 'std::out_of_range'")
            if file_type == "orig": self.stats.inc_total_orig_uninteresting_errors()
            if file_type == "trans": self.stats.inc_total_trans_uninteresting_errors()
            return 3    # We don't care about this

        if standard_error.find("Error") != -1 or standard_error.find("error") != -1:
            print(colored("Some unknown error", "red", attrs=["bold"]))
            # update stats object
            self.program.add_log_text("\tError Type: UNKNOWN ERROR. Please investigate!")
            if file_type == "orig": self.stats.inc_total_orig_unknown_errors()
            if file_type == "trans": self.stats.inc_total_trans_unknown_errors()
            return 1

        # Seems like everything is OK 
        return 0
