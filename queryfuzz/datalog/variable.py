from abc import ABC, abstractmethod

class Variable(object):
    def __init__(self, name, vtype):
        self.name = name
        self.type = vtype

    def set_name(self, name):
        self.name = name
    def set_type(self, vtype):
        self.type = vtype
    def get_name(self):
        return self.name
    def get_type(self):
        return self.type
