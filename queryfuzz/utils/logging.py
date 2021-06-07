"""
    We are going to save everything. 
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