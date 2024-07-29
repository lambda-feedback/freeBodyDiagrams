import copy
from sympy import Matrix, zeros, shape

from expression_utilities import create_sympy_parsing_params
from expression_utilities import parse_expression

def parse_matrix(m_strings, parsing_params):
    matrix = []
    for (i, row) in enumerate(m_strings):
        matrix_row = []
        for(j, element) in enumerate(row):
            try:
                matrix_row.append(parse_expression(element, parsing_params))
            except Exception as e:
                raise Exception(f"Element on row {i} in column {j} could not be parsed.") from e
        matrix.append(matrix_row)
    return Matrix(matrix)

def check_matrix_equivalence(m0, m1):
    r0 = m0.rank()
    r1 = m1.rank()
    r = m0.row_join(m1).rank()
    return (r0 == r1) and (r0 == r)

if __name__ == "__main__":
    m0_strings = [
        ["-1","1","0","0","2L"],
        ["0","-1","1","0","L"],
        ["0","0","-1","1","2L"],
        ["1","0","0","0","0"]
    ]
    m1_strings = [
        ["1","0","0","0","0"],
        ["0","1","0","0","2L"],
        ["0","0","1","0","3L"],
        ["0","0","0","1","5L"]
    ]
    params = {
        "strict_syntax": False,
        "elementary_functions": True,
    }
    parsing_params = create_sympy_parsing_params(params)
    m0 = parse_matrix(m0_strings, parsing_params)
    m1 = parse_matrix(m1_strings, parsing_params)
    print(m0)
    print(m1)
    print(check_matrix_equivalence(m0, m1))