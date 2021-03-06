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

from abc import ABC, abstractmethod

class BaseRunner(object):

    def __init__(self, params, program, stats):
        self.params = params
        self.path_to_engine = None
        self.program = program
        self.stats = stats
        self.clean_data = ""
        self.program_name = None

    @abstractmethod
    def run_original(self):
        pass

    @abstractmethod
    def run_transformed(self):
        pass

    @abstractmethod
    def process_output(self, std_output, orig, transformation_number):
        pass

    @abstractmethod
    def process_standard_error(self):
        pass

    @abstractmethod
    def process_standard_output(self):
        pass


    @abstractmethod
    def compile_datalog_into_rust(self):
        pass

    @abstractmethod
    def compile_rust_into_an_executable(self):
        pass

    @abstractmethod
    def run_ddlog_program(self, orig):
        pass

    def set_program_name(self, name):
        self.program_name = name