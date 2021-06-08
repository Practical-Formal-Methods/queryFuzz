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
from termcolor import colored
import os
from queryfuzz.utils.file_operations import create_fact_file_with_data
import shutil

class DDlogRunner(BaseRunner):

    def process_output(self, standard_output, orig, transformation_number=0):
        def parse_ddlog_standard_output(std_output):
            """
                JTKG{.a = "4Dumgdnpgi", .b = "1e3PUPow3z", .c = "4Dumgdnpgi"}
                JTKG{.a = "4Dumgdnpgi", .b = "o54nS4Dumg", .c = "4Dumgdnpgi"}
                JTKG{.a = "Pow3z", .b = "1e3PUPow3z", .c = "Pow3z"}
                JTKG{.a = "Pow3z", .b = "o54nS4Dumg", .c = "Pow3z"}
                YJXZ{.a = "lm1xdGq3R0", .b = "lm1xdGq3R0", .c = "C75fA"}
                OAZM{.a = "vOYyDVIa2Z", .b = "vOYyDVIa2Z"}
                UKVN{.a = "390742D3SH", .b = "5OZ6H"}
                UKVN{.a = "390742D3SH", .b = "KVIP8Q2UP7"}
                UKVN{.a = "A90vPkOAKF", .b = "5OZ6H"}
                UKVN{.a = "A90vPkOAKF", .b = "KVIP8Q2UP7"}
                UKVN{.a = "tRtCTj7Ygx", .b = "5OZ6H"}
                UKVN{.a = "tRtCTj7Ygx", .b = "KVIP8Q2UP7"}
                KVRW{.a = "KDhAk"}
                KVRW{.a = "eQZOpBTRBT"}
            """
            lines = std_output.split("\n")
            clean_data = list()
            for line in lines:
                if line.find("{") == -1:
                    # This is not a data row. ignore this
                    continue
                data_line = line.replace("\t", "")
                data_line = data_line.replace(" ", "")
                data_line = data_line[data_line.find("{") + 1:data_line.find("}")]
                data_row = data_line.split(",")
                for i in range(len(data_row)):
                    data_row[i] = data_row[i][data_row[i].find("=") + 1:]
                row_string = "".join(i + "\t" for i in data_row)
                clean_data.append(row_string)
            for i in clean_data:
                print(colored(i, "green", attrs=["bold"]))
            print(colored("length of rows = " + str(len(clean_data)), "yellow", attrs=["bold"]))
            return clean_data        


        parsed_result = parse_ddlog_standard_output(standard_output)
        if orig: 
            results_file_name = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            results_file_name = os.path.join(self.program.get_program_path(), "trans_" + str(transformation_number) + ".facts")            
    
        print("####### Exporting (as .facts) ddlog's stdout result to : ", end="")
        print(colored(results_file_name, "blue", attrs=["bold"]))
        create_fact_file_with_data(parsed_result, results_file_name)



    def process_standard_error(self, standard_error, file_type):
        if standard_error.find("is both declared and used inside relational atom") != -1:
            # We are tolerating this for now
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("spurious network error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("Bus error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("unexpected reserved word") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 3

        if standard_error.find("panicked") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Failed to parse input file") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("No such file or directory") != -1 or standard_error.find("failed to run command") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("Unknown constructor") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1

        if standard_error.find("ddlog: Module ddlog_rt imported by") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            print(colored("RUN: export DDLOG_HOME=/home/numair/differential-datalog/", "red", attrs=["bold"]))
            return 1

        if standard_error.find("Killed") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            print(colored("EXPERIENCED A TIMEOUT", "red", attrs=["bold"]))
            return 3

        if standard_error.find("Error") != -1 or standard_error.find("error") != -1:
            print(colored(standard_error, "red", attrs=["bold"]))
            return 1
        return 0
    

    def compile_datalog_into_rust(self):
        TIMEOUT = 60
        command = "export DDLOG_HOME=" + self.params["path_to_ddlog_home_dir"] + " && "
        command += "timeout -s SIGKILL " + str(TIMEOUT) + "s " + self.path_to_engine + " -i " + self.program.get_program_file_path()
        
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()
        
        print("\tDDLOG -> RUST   COMMAND = " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error=standard_error, file_type="")
        return signal


    def compile_rust_into_an_executable(self):
        command = 'cd ' + self.program.get_program_file_path()[:-3] + '_ddlog/ && export CARGO_PROFILE_RELEASE_sOPT_LEVEL= && timeout -s SIGKILL 1500s cargo build --release'
        self.program.add_log_text("\tCommand: " + command)
        self.program.dump_program_log_file()
                
        print("running:")
        print("\tRUST -> EXE   COMMAND = " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()

        self.program.add_log_text("\nSTANDARD ERROR: " + standard_error)
        self.program.add_log_text("\nSTANDARD OUTPUT: " + standard_output)
        self.program.dump_program_log_file()
        signal = self.process_standard_error(standard_error, "")
        return signal



    def run_ddlog_program(self, orig, transformation_number=0):
        TIMEOUT = 60
        command = "timeout -s SIGKILL " + str(TIMEOUT) + "s " + self.program.get_program_file_path()[:-3] + "_ddlog/target/release/" + self.program_name + "_cli < " + self.program.get_program_path() + "facts.dat"
        print("RUN command -> " + command)
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        standard_error = p.stderr.read().decode()
        standard_output = p.stdout.read().decode()
        signal = self.process_standard_error(standard_error, "")
        print(colored(standard_output, "green", attrs=["bold"]))
        print("")
        print(colored(standard_error, "red", attrs=["bold"]))
        print("")
        self.process_output(standard_output=standard_output, orig=orig, transformation_number=transformation_number)
        
        
        if orig: 
            output_file_path = os.path.join(self.program.get_program_path(), "orig.facts")
        else:
            output_file_path = os.path.join(self.program.get_program_path(), "trans_" + str(transformation_number) + ".facts")
        
        if not os.path.exists(output_file_path):
            print(colored("NO OUTPUT FILE PRODUCED", "red", attrs=["bold"]))
            self.program.add_log_text("WARNING: NO OUTPUT FILE PRODUCED")
            self.program.dump_program_log_file()
            return 1

        self.program.set_output_result_path(output_file_path)
        self.program.add_log_text("Everything seems to be ok")
        self.program.dump_program_log_file()


    def run_original(self, engine_options):
        self.program.add_log_text(" ================== ")
        self.program.add_log_text("  Running Original ")
        self.program.add_log_text(" ================== ")
        
        self.path_to_engine = self.params["path_to_ddlog_engine"]
        signal = self.compile_datalog_into_rust()
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable()
        if signal != 0: return signal
        self.run_ddlog_program(orig=True)
        shutil.rmtree(os.path.join(self.program.get_program_path(), "orig_rules_ddlog"))
        return 0


    def run_transformed(self, transformation_number, engine_options):
        self.program.add_log_text(" ===================== ")
        self.program.add_log_text("  Running Transformed ")
        self.program.add_log_text(" ===================== ")

        self.path_to_engine = self.params["path_to_ddlog_engine"]
        signal = self.compile_datalog_into_rust()
        if signal != 0: return signal
        signal = self.compile_rust_into_an_executable()
        if signal != 0: return signal
        self.run_ddlog_program(orig=False, transformation_number=transformation_number)

        
        shutil.rmtree(os.path.join(self.program.get_program_path(), "transformed_rules_" + str(transformation_number) + "_ddlog") )
        return 0