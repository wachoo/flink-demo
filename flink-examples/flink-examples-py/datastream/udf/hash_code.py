from pyflink.table import ScalarFunction


class HashCode(ScalarFunction):
    def __init__(self):
        self.factor = 5

    def eval(self, s):
        return hash(s) * self.factor


class IntToString(ScalarFunction):
    def eval(self, i):
        return str(i)
