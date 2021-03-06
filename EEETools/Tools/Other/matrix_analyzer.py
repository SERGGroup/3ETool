from scipy.linalg import diagsvd
from copy import deepcopy
import numpy.linalg


class MatrixAnalyzer:

    def __init__(self, matrix: numpy.ndarray, vector: numpy.ndarray, main_matrix=None, try_system_decomposition=False):

        self.matrix = deepcopy(matrix)
        self.vector = vector

        self.__inv_matrix = None
        self.re_matrix = self.matrix
        self.re_vector = self.vector

        self.main_matrix = main_matrix
        self.sub_matrix = None

        self.has_assignment = False

        self.n_row = self.matrix.shape[0]
        self.n_col = self.matrix.shape[1]

        self.elements = list()

        self.vector_list = None
        self.columns = MatrixLineList(contains_rows=False)
        self.rows = MatrixLineList(contains_rows=True)

        self.__initialize_matrix()

        self.rows.check()
        self.columns.check()
        self.__check_assignments()

        self.__ill_conditioned_matrix_warning = False
        self.try_system_decomposition = try_system_decomposition

    def __initialize_matrix(self):

        for i in range(self.n_row):

            row_list = list()
            for j in range(self.n_col):
                new_element = MatrixElement(self.matrix[i, j], [i, j])
                row_list.append(new_element)

            self.elements.append(row_list)
            self.rows.add_to_list(row_list, i)

        for j in range(self.n_col):

            col_list = list()
            for i in range(self.n_row):
                element = self.elements[i][j]
                col_list.append(element)

            self.columns.add_to_list(col_list, j)

        __tmp_vector_list = list()

        for i in range(self.n_row):
            __tmp_vector_list.append(MatrixElement(self.vector[i], [i, -1]))

        self.vector_list = MatrixColumn(__tmp_vector_list, -1)

    def __check_assignments(self):

        for row in self.rows:

            if row.is_assignment:
                self.has_assignment = True

    def solve(self):

        if self.has_assignment:

            non_assignment_rows_indices = self.__calculate_assignment()

            if len(non_assignment_rows_indices) > 0:

                __return = self.__identify_new_matrix_and_vector(non_assignment_rows_indices)
                non_solved_columns = self.columns.non_solved

                self.sub_matrix = MatrixAnalyzer(__return["new_matrix"], __return["new_vector"], self)
                sub_solution = self.sub_matrix.solve()

                for i in range(len(non_solved_columns)):
                    non_solved_columns[i].set_solution(sub_solution[i])

        else:

            self.re_matrix, self.re_vector = self.__rearrange_matrix(self.matrix, self.vector)

            try:

                sol = self.__std_solve()

            except:

                if self.try_system_decomposition:

                    try:

                        A, B = self.__decompose_matrix()

                        sol_prev = self.__svd_solve(A, self.vector)
                        matrix = B
                        matrix_prev = A

                        counter = 0
                        while True:

                            sol = self.__svd_solve(matrix, self.vector - matrix_prev.dot(sol_prev))
                            error = abs(numpy.max(numpy.abs(sol_prev - sol)) / numpy.max(sol_prev))

                            if error < 0.01:

                                break

                            else:

                                sol_prev = (sol + sol_prev) / 2
                                matrix_tmp = matrix_prev
                                matrix_prev = matrix
                                matrix = matrix_tmp

                                counter += 1

                                if counter > 100:
                                    raise

                    except:

                        sol = self.__lstsq_solve()

                else:

                    sol = self.__lstsq_solve()

            for i in range(len(self.columns)):
                self.columns[i].set_solution(sol[i])

        return self.solution

    def __calculate_assignment(self) -> list:

        non_assignment_rows_indices = list()

        for row in self.rows:

            if row.is_assignment:

                assignment_elem = row.non_zero_element[0]
                assignment_vector = self.vector_list.get_from_list(assignment_elem.initial_position[0])
                solution = assignment_vector.value / assignment_elem.value

                assignment_column = self.columns.get_from_list(assignment_elem.initial_position[1])
                assignment_column.set_solution(solution)

            else:

                non_assignment_rows_indices.append(row.initial_position)

        return non_assignment_rows_indices

    def __identify_new_matrix_and_vector(self, non_assignment_rows_indices):

        # prepare new sub_matrix
        n_elements = len(non_assignment_rows_indices)
        new_matrix = numpy.zeros((n_elements, n_elements))
        new_vector = self.vector_list.return_numpy_array(indices=non_assignment_rows_indices)

        i = 0
        for column in self.columns:

            row_element = column.return_numpy_array(indices=non_assignment_rows_indices)

            if column.is_solved:

                new_vector -= row_element * column.solution

            else:

                new_matrix[:, i] = row_element
                i += 1

        return {"new_matrix": new_matrix,
                "new_vector": new_vector}

    def __decompose_matrix(self):

        m, n = self.matrix.shape
        u, s, vt = numpy.linalg.svd(self.matrix)
        s_new = s

        for i in range(len(s)):

            if i <= len(s) * 4 / 5:

                s_new[i] = s[i]

            else:

                s_new[i] = 0

        s_mat = diagsvd(s_new, m, n)
        A = u.dot(s_mat).dot(vt)

        # ext_a = (numpy.min(A), numpy.max(A))
        # A = numpy.round(A / (ext_a[1] - ext_a[0]), 3) * (ext_a[1] - ext_a[0])

        B = self.matrix - A

        return A, B

    def __std_solve(self):

        new_matrix, new_vector, deleted_rows = self.__identify_empty_lines(self.re_matrix, self.re_vector)
        self.__inv_matrix = numpy.linalg.inv(new_matrix)
        sol = self.__inv_matrix.dot(new_vector)
        return self.__append_zeroes_if_needed(sol, deleted_rows)

    def __lstsq_solve(self):

        new_matrix, new_vector, deleted_rows = self.__identify_empty_lines(self.re_matrix, self.re_vector)
        sol = numpy.linalg.lstsq(new_matrix, new_vector)
        self.__ill_conditioned_matrix_warning = True
        return self.__append_zeroes_if_needed(sol[0], deleted_rows)

    @staticmethod
    def __svd_solve(matrix, vector):

        m, n = matrix.shape
        u, s, vt = numpy.linalg.svd(matrix)
        r = numpy.linalg.matrix_rank(matrix)

        s[:r] = 1 / s[:r]
        s_inv = diagsvd(s, m, n)

        return vt.T.dot(s_inv).dot(u.T).dot(vector)

    @staticmethod
    def __rearrange_matrix(matrix, vector):

        m, n = matrix.shape
        new_matrix = numpy.ones((m, n))
        new_vector = numpy.ones(m)

        for i in range(m):

            row = matrix[i, :]
            ext_row = (numpy.min(row), numpy.max(row))

            if not (ext_row[1] - ext_row[0]) == 0:

                new_matrix[i, :] = row / (ext_row[1] - ext_row[0])
                new_vector[i] = vector[i] / (ext_row[1] - ext_row[0])

            else:

                new_matrix[i, :] = matrix[i, :]
                new_vector[i] = vector[i]

        return new_matrix, new_vector

    @staticmethod
    def __identify_empty_lines(matrix, vector):

        m, n = matrix.shape
        deleted_rows = []

        new_matrix = numpy.copy(matrix)
        new_vector = numpy.copy(vector)

        for i in range(m):

            row = matrix[i, :]
            ext_row = (numpy.min(row), numpy.max(row))

            if (ext_row[1] - ext_row[0]) == 0 and ext_row[0] == 0:

                if vector[i] == 0:

                    del_i = i - len(deleted_rows)
                    new_matrix = numpy.delete(new_matrix, del_i, 0)
                    new_matrix = numpy.delete(new_matrix, del_i, 1)
                    new_vector = numpy.delete(new_vector, del_i)
                    deleted_rows.append(i)

                else:

                    raise

        return new_matrix, new_vector, deleted_rows

    def __append_zeroes_if_needed(self, sol, deleted_rows):

        for i in deleted_rows:

            sol = numpy.insert(sol, i, 0)

            if self.__inv_matrix is not None:

                m, n = self.__inv_matrix.shape

                new_row = numpy.zeros(m)
                new_col = numpy.zeros(n + 1)

                self.__inv_matrix = numpy.insert(self.__inv_matrix, i, [new_row], axis=0)
                self.__inv_matrix = numpy.insert(self.__inv_matrix, i, [new_col], axis=1)

        return sol

    @property
    def is_solvable(self):

        for element in [self.columns.empty_lines, self.columns.dependent_lines,
                        self.rows.empty_lines, self.rows.dependent_lines]:

            if not len(element) == 0:
                return False

        return self.n_row == self.n_col

    @property
    def solution(self):

        sol_vector = numpy.zeros(len(self.vector))

        for i in range(len(self.columns)):

            solution = self.columns[i].solution

            if solution is not None:
                sol_vector[i] = solution

        return sol_vector

    @property
    def is_ill_conditioned(self):

        if self.sub_matrix is None:

            return self.__ill_conditioned_matrix_warning

        else:

            return self.sub_matrix.is_ill_conditioned

    @property
    def inverse_matrix(self):

        return self.__inv_matrix


class MatrixElement:

    def __init__(self, value: float, initial_position: list):
        self.value = value
        self.solution = None
        self.initial_position = initial_position

        self.row = None
        self.col = None

    @property
    def is_empty(self) -> bool:
        return self.value == 0


class MatrixLine:

    def __init__(self, vector, initial_position):

        self.vector = vector
        self.module = self.__vector_module()
        self.initial_position = initial_position

        self.is_row = None
        self.solution = None

        self.non_zero = self.__count_non_zero_elements()

    def __vector_module(self) -> float:

        module = 0

        for element in self.vector:
            module += pow(element.value, 2)

        return pow(module, 0.5)

    def __count_non_zero_elements(self) -> int:

        counter = 0

        for element in self.vector:

            if not element.is_empty:
                counter += 1

        return counter

    def return_numpy_array(self, indices=None) -> numpy.ndarray:

        if indices is None:

            return_vector = numpy.zeros(len(self.vector))

            for i in range(len(self.vector)):
                return_vector[i] = self.vector[i].value

        else:

            i = 0
            return_vector = numpy.zeros(len(indices))

            for index in indices:
                return_vector[i] = self.vector[index].value
                i += 1

        return return_vector

    def get_from_list(self, initial_position):

        if self.is_row:
            i = 1
        else:
            i = 0

        for element in self.vector:

            if element.initial_position[i] == initial_position:
                return element

        return None

    @property
    def non_zero_element(self):

        return_list = list()

        for element in self.vector:

            if not element.is_empty:
                return_list.append(element)

        return return_list

    @property
    def is_empty(self):

        return self.module == 0

    @property
    def dim(self):

        return len(self.vector)

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

        if self.dim == other.dim and self.is_row == other.is_row:

            if self.non_zero == other.non_zero:

                for i in range(self.dim):

                    if self.vector[i].value / self.module != other.vector[i].value / other.module:
                        return False

                return True

        return False


class MatrixColumn(MatrixLine):

    def __init__(self, vector, initial_position):

        super().__init__(vector, initial_position)

        self.is_row = False

        for elem in vector:
            elem.col = self

    def set_solution(self, solution):

        self.solution = solution
        for elem in self.vector:
            elem.solution = solution

    @property
    def is_solved(self):

        return self.solution is not None


class MatrixRow(MatrixLine):

    def __init__(self, vector, initial_position):
        super().__init__(vector, initial_position)
        self.is_row = True

        for elem in vector:
            elem.row = self

    @property
    def is_assignment(self):
        return self.non_zero == 1


class MatrixLineList(list):

    def __init__(self, contains_rows):

        super().__init__()
        self.contains_rows = contains_rows

        self.empty_lines = list()
        self.dependent_lines = list()

    def get_from_list(self, initial_position):

        for element in self:

            if element.initial_position == initial_position:
                return element

        return None

    def add_to_list(self, vector, initial_position: int):

        new_element = self.get_from_list(initial_position)

        if new_element is None:

            if self.contains_rows:
                new_element = MatrixRow(vector, initial_position)

            else:
                new_element = MatrixColumn(vector, initial_position)

            self.append(new_element)

        return new_element

    def check(self):

        self.empty_lines = list()
        self.dependent_lines = list()

        for i in range(len(self)):

            if self[i].is_empty:

                self.empty_lines.append({i: self[i]})

            else:

                for j in range(i + 1, len(self)):

                    if self[i] == self[j]:
                        self.dependent_lines.append({str(i) + "; " + str(j): [self[i], self[j]]})

    @property
    def non_solved(self):

        return_list = list()

        for element in self:

            if not element.is_solved:
                return_list.append(element)

        return return_list

    @property
    def sorted_indices(self) -> list:

        sorted_indices = list()
        self.sort()

        for element in self:
            sorted_indices.append(element.initial_position)

        return sorted_indices
