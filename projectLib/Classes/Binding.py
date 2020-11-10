class Binding:

    def __init__(self, file=None, ind=-1):
        self.file = file
        self.ind = ind

    def __repr__(self):
        result_binding = []

        if self.file:
            result_binding.append(self.file)

        result_binding.append(self.ind)

        return str(result_binding)

    def __eq__(self, other):
        if self.file == other.file and self.ind == other.ind:
            return True
        return False