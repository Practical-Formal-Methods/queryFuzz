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

import os
import shutil
from termcolor import colored
import json

def create_fact_file_with_data(data, path):
    file  = open(path, "w")
    for row in data:
        file.write(row + "\n")
    file.close()

def load_parameters(home):
    with open(os.path.join(home, "params.json")) as f:
        data = json.load(f)
    return data

def create_server_directory(temp_dir, server):
    server_dir = os.path.join(temp_dir, server)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    # If the server directory exists, then leave it
    if not os.path.exists(server_dir):
        os.mkdir(server_dir)

def create_core_directory(temp_dir, server, core):
    core_dir = os.path.join(temp_dir, server, "core_" + str(core))
    if os.path.exists(core_dir):
        shutil.rmtree(core_dir)
    os.mkdir(core_dir)
    return core_dir

def create_file(data, path):
    file = open(path, "w")
    file.write(data)
    file.close()

def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.read().splitlines()
        for i in range(0,len(lines)):
            lines[i] = lines[i].replace("\t", "-")
    return lines

def pick_seed_program(randomness, path_to_engine_seed_folder):
    for r,d,f in os.walk(path_to_engine_seed_folder):
        picked_seed = randomness.random_choice(d)
        return os.path.join(path_to_engine_seed_folder, picked_seed)

def export_buggy_instance_for_soundness(path_to_db_instance, parent_temp_dir):    
    # check if the soundness folder exists
    path_to_soundness_folder = os.path.join(parent_temp_dir, "soundness")
    number_of_directories = 0
    for r,d,f in os.walk(path_to_soundness_folder):
        number_of_directories = len(d)
        break
    if not os.path.exists(path_to_soundness_folder):
        print(colored("Creating a soundness folder at: ", "red"), end="")
        print(colored(parent_temp_dir, "red"))
        os.mkdir(path_to_soundness_folder)
    path_to_copied_db_instance = os.path.join(path_to_soundness_folder, str(number_of_directories))
    shutil.copytree(path_to_db_instance, path_to_copied_db_instance, copy_function = shutil.copy)
    print(colored("Buggy program exported at: " + path_to_copied_db_instance, "red"))

def export_errored_out_instance(path_to_db_instance, home, fuzzed_instance):
    main_temp_dir = os.path.join(home, "temp")
    path_to_fuzzed_error_instances = os.path.join(main_temp_dir, "errors", "Original_Instances")
    if fuzzed_instance:
        path_to_fuzzed_error_instances = os.path.join(main_temp_dir, "errors", "Fuzzed_Instances")
    print("Creating Errors folder at: ", end="")
    print(path_to_fuzzed_error_instances)
    # check if the error folder exists
    path_to_error_folder = os.path.join(main_temp_dir, "errors")
    if not os.path.exists(path_to_error_folder):
        os.mkdir(path_to_error_folder)
    number_of_directories = 0
    for r, d, f in os.walk(path_to_fuzzed_error_instances):
        number_of_directories = len(d)
        break
    if not os.path.exists(path_to_fuzzed_error_instances):
        os.mkdir(path_to_fuzzed_error_instances)
    path_to_copied_db_instance = os.path.join(path_to_fuzzed_error_instances, str(number_of_directories))
    shutil.copytree(path_to_db_instance, path_to_copied_db_instance, copy_function=shutil.copy)
    print("Errored out database instance's exported at: " + path_to_copied_db_instance)
    
def get_dir_names(dir_path):
    for r,d,f in os.walk(dir_path):
        d.sort()
        return [i for i in d if i != "errors" and i != "soundness"]
