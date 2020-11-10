import copy

class ErrorInfo:

    def __init__(self, file=None, lines=[], type="", hash=None, bindings=[]):
        self.file = copy.deepcopy(file)
        self.lines = copy.deepcopy(lines)
        self.type = copy.deepcopy(type)
        self.hash = copy.deepcopy(hash)
        self.bindings = copy.deepcopy(bindings)

    def has_bindings(self):
        if len(self.bindings) > 0:
            return True
        return False

    def __repr__(self):
        result_list = []

        if self.file:
            result_list.append(self.file)

        result_list.append(self.lines)
        result_list.append(self.type)

        if self.hash:
            result_list.append(self.hash)

        if len(self.bindings) > 0:
            result_list.append(self.bindings)

        return str(result_list)

    def __eq__(self, other):
        if self.file == other.file and \
           self.lines == other.lines and \
           self.type == other.type and \
           self.hash == other.hash and \
           self.bindings == other.bindings:
            return True

        return False