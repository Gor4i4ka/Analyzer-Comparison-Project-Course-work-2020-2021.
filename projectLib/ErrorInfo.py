from copy import deepcopy as dc
# Internal imports
from projectLib.Binding import Binding


class ErrorInfo:

    def __init__(self, file=None, lines=[], type="", hash=None, bindings=[], msg="", traces_info=[], main_line = 0):
        self.file = dc(file)
        self.lines = dc(lines)
        self.type = dc(type)
        self.hash = dc(hash)
        self.bindings = dc(bindings)
        # For visualisation
        self.msg = dc(msg)
        self.traces_info = dc(traces_info)
        self.main_line = dc(main_line)

    def has_bindings(self):
        if len(self.bindings) > 0:
            return True
        return False

    def binding_already_present(self, el: Binding):
        for binding in self.bindings:
            if el == binding:
                return True
        return False

    def append(self, value: Binding):
        self.bindings.append(value)

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

        result_list.append(self.msg)
        result_list.append(self.traces_info)
        result_list.append(self.main_line)

        return str(result_list)

    def __eq__(self, other):
        if self.file == other.file and \
           self.lines == other.lines and \
           self.type == other.type and \
           self.hash == other.hash and \
           self.bindings == other.bindings and \
           self.msg == other.msg and \
           self.traces_info == other.traces_info and \
           self.main_line == other.main_line:
            return True

        return False