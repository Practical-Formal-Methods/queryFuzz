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
from queryfuzz.utils.file_operations import create_file

class Logging(object):
    def __init__(self):
        self.log_file_path = None
        self.log_file_name = None
        self.log_text = "\n --- LOGS --- \n"
    
    def set_log_file_path(self, log_file_path):
        self.log_file_path = log_file_path

    def set_log_file_name(self, file_name):
        self.log_file_name = file_name

    def add_log_text(self, text):
        self.log_text += "\n" + text

    def dump_log_file(self):
        self.log_text += "\n\n"
        create_file(self.log_text, os.path.join(self.log_file_path, self.log_file_name))

    def refresh_log_text(self):
        self.log_text = ""
    
    def get_log_file_path(self):
        return os.path.join(self.log_file_path, self.log_file_name)