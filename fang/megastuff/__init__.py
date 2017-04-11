def func_compare(self, argument, standard_value, compare_value):
    compare_operator = {
        '<=': self.compare_lessorequal,
        '>=': self.compare_largerorequal,
        '=': self.compare_equal,
        '>': self.compare_larger,
        '<': self.compare_lessthan,
        '<>': self.compare_notequal,
        '&': self.compare_final_equal,
        '|': self.compare_final_or,
        'contains': self.compare_contants
    }
    func = compare_operator.get(argument)
    return func(standard_value, compare_value)


def compare_contants(self, standard_value=None, compare_value=None):  # compare check string in
    return standard_value in compare_value


def compare_lessorequal(self, standard_value=None, compare_value=None):  # compare int
    return compare_value <= standard_value


def compare_largerorequal(self, standard_value=None, compare_value=None):  # compare int
    return compare_value >= standard_value


def compare_equal(self, standard_value=None, compare_value=None):  # compare int
    return compare_value == standard_value


def compare_larger(self, standard_value=None, compare_value=None):  # compare int
    return compare_value > standard_value


def compare_lessthan(self, standard_value=None, compare_value=None):  # compare int
    return compare_value < standard_value


def compare_notequal(self, standard_value=None, compare_value=None):  # compare int
    return compare_value != standard_value


def compare_final_equal(self, output_value=None, output_value_=None):  # compare true or false
    return output_value == output_value_


def compare_final_or(self, output_value=None, output_value_=None):  # compare true or false
    return output_value == output_value_