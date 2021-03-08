import numpy
from copy import deepcopy
from scipy.sparse import csc_matrix, linalg


class MatrixAnalyzer():

    def __init__(self, matrix: numpy.ndarray):

        self.matrix = deepcopy(matrix)
        self.residual_matrix = deepcopy(matrix)
        self.ordered_matrix = numpy.zeros(self.matrix.shape)
        self.r_cond = numpy.linalg.cond(self.matrix)

        self.variable_set_equations = list()
        self.matrix_blocks = list()

        self.n_row = self.matrix.shape[0]
        self.n_col = self.matrix.shape[1]

        self.columns = MatrixElementList()
        self.rows = MatrixElementList()

        self.empty_columns = list()
        self.dependent_columns = list()

        self.empty_rows = list()
        self.dependent_rows = list()

        self.__check(check_col=True)
        self.__check(check_col=False)

        self.__identify_variable_set_equation()
        self.__reorder_matrix()

    def solve(self, vector: numpy.ndarray):

        A = linalg.lsmr(self.matrix, vector, btol=1E-10)
        B = numpy.linalg.lstsq(self.matrix, vector, rcond=self.r_cond)
        C = numpy.linalg.solve(self.matrix, vector)

    @property
    def is_solvable(self):

        for element in [self.empty_columns, self.dependent_columns, self.empty_rows, self.dependent_rows]:

            if not len(element) == 0:

                return False

        return (self.n_row == self.n_col)

    def __check(self, check_col):

        if check_col:

            n_elements = self.n_col
            matrix = self.matrix

            list = self.columns
            empty_list = self.empty_columns
            dependence_list = self.dependent_columns

        else:

            n_elements = self.n_row
            matrix = numpy.transpose(self.matrix)

            list = self.rows
            empty_list = self.empty_rows
            dependence_list = self.dependent_rows

        for i in range(n_elements):

            __vector = matrix[:, i]
            __element = list.add_to_list(__vector, i)

            if list[-1].module == 0:

                empty_list.append({i: __element})

            else:

                for j in range(i + 1, n_elements):

                    __new_vector = matrix[:, j]
                    __new_element = list.add_to_list(__new_vector, j)

                    if __element == __new_element:
                        dependence_list.append({str(i) + "; " + str(j): [__element, __new_element]})

    def __reorder_matrix(self):

        self.ordered_matrix = numpy.zeros(self.matrix.shape)

        self.rows.sort()
        self.columns.sort()

        __tmp_matrix = numpy.zeros(self.matrix.shape)

        for i in range(len(self.rows)):

            __tmp_matrix[i, :] = self.rows[i].vector
            i += 1

        for j in range(len(self.columns)):

            self.ordered_matrix[:, j] = __tmp_matrix[:, self.columns[j].initial_position]

    def __identify_variable_set_equation(self):

        for i in range(self.residual_matrix.shape[0]):

            non_zero_elements = 0

            for j in range(self.residual_matrix.shape[1]):

                if self.residual_matrix[i, j] != 0:
                    non_zero_elements += 1

            if non_zero_elements < 2:

                # append equation
                # TODO!!!
                self.variable_set_equations.append(i)


class MatrixElement:

    def __init__(self, vector: numpy.ndarray, initial_position):

        self.vector = deepcopy(vector)
        self.module = self.__vector_module()
        self.norm_vector = vector/self.module
        self.initial_position = initial_position

    def __vector_module(self):

        module = 0
        vector = self.vector
        shape = vector.shape[0]

        for j in range(shape):
            module += pow(vector[j], 2)

        return pow(module, 0.5)

    def __gt__(self, other):

        # enables comparison
        # self > other

        return self.module < other.module

    def __lt__(self, other):

        # enables comparison
        # self < other

        return self.module > other.module

    def __le__(self, other):

        return not self.__gt__(other)

    def __ge__(self, other):

        return not self.__lt__(other)

    def __eq__(self, other):

        shape = self.norm_vector.shape[0]

        for j in range(shape):

            try:
                if not self.norm_vector[j] == other.norm_vector[j]:
                    return False

            except:
                return False

        return True


class MatrixElementList(list):

    def __init__(self):
        super().__init__()

    def __get_from_list(self, initial_position):

        for element in self:

            if element.initial_position == initial_position:

                return element

        return None

    def add_to_list(self, vector: numpy.ndarray, initial_position):

        new_element = self.__get_from_list(initial_position)

        if new_element is None:

            new_element = MatrixElement(vector, initial_position)
            self.append(new_element)

        return new_element