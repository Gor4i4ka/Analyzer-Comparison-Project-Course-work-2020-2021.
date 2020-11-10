import copy

# Internal imports
from projectLib.Classes.ErrorInfo import ErrorInfo


class FileInfo:

    def __init__(self, file="", errors=[]):
        self.file = copy.deepcopy(file)
        self.errors = copy.deepcopy(errors)

    def append(self, element: ErrorInfo):
        self.errors.append(copy.deepcopy(element))

    def remove(self, value: ErrorInfo):
        self.errors.remove(value)

    def has_errors(self):
        if len(self.errors) > 0:
            return True
        return False

    def __repr__(self):
        return str([self.file, self.errors])

    def __str__(self):
        return self.file

    def __getitem__(self, item):
        return self.errors[item]

    def __setitem__(self, key, value):
        self.errors[key] = value
        return 0