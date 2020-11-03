class ErrorInfo:

    def __init__(self, file=None, lines=[], type="", hash=None, bindings=[]):
        self.file = file
        self.lines = lines
        self.type = type
        self.hash = hash
        self.bindings = bindings