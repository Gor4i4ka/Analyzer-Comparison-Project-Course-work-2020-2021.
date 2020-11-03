# Internal imports
from projectLib.ErrorInfo import ErrorInfo


class FileInfo:

    def __init__(self, file="", errors=[]):
        self.file = file
        self.errors = errors

    def append(self, element: ErrorInfo):
        self.errors.append(element)

    def remove(self, value: ErrorInfo):
        self.errors.remove(value)