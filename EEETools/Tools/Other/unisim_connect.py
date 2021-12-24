import win32com.client


class UNISIMConnector:

    def __init__(self, filepath=None):

        self.app = win32com.client.Dispatch('UnisimDesign.Application')

        self.__doc = None
        self.solver = None
        self.block_names = list()
        self.stream_names = list()

        self.open(filepath)

    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        try:

            self.doc.Visible = False
            self.__doc.Close()

        except:

            pass

        self.app.Visible = False
        self.app.Quit()

    def get_spreadsheet(self, spreadsheet_name):

        try:

            spreadsheet = UNISIMSpreadsheet(self, spreadsheet_name)

        except:

            return None

        return spreadsheet

    def generate_excel_file(self):

        pass

    def show(self):

        try:

            self.app.Visible = True
            self.doc.Visible = True

        except:

            pass

    def open(self, filepath):

        if self.is_ready:

            self.__doc.Close()

        if filepath is None:

            self.doc = self.app.SimulationCases.Add()

        else:

            self.doc = self.app.SimulationCases.Open(filepath)

    def get_block(self, block_name):

        if block_name not in self.block_names:

            return None

        else:

            return self.doc.Flowsheet.Operations.Item(block_name)

    def get_stream(self, stream_name):

        if stream_name not in self.stream_names:

            return None

        else:

            return self.doc.Flowsheet.Streams.Item(stream_name)

    @property
    def doc(self):

        return self.__doc

    @doc.setter
    def doc(self, doc):

        try:

            self.solver = doc.Solver

        except:

            self.__doc = None
            self.solver = None
            self.block_names = list()
            self.stream_names = list()

        else:

            self.__doc = doc
            self.block_names = self.doc.Flowsheet.Operations.Names
            self.stream_names = self.doc.Flowsheet.Streams.Names

    @property
    def is_ready(self):

        return self.__doc is not None

    def wait_solution(self):

        try:

            while self.solver.IsSolving:

                pass

        except:

            pass


class UNISIMSpreadsheet:

    def __init__(self, parent:UNISIMConnector, spreadsheet_name):

        self.parent = parent
        self.spreadsheet = parent.doc.Flowsheet.Operations.Item(spreadsheet_name)

    def set_cell_from_list(self, input_list: list):

        for value_dict in input_list:

            self.set_cell_value(value_dict["cell name"], value_dict["value"])

    def get_value_from_list(self, input_list: list):

        return_dict = dict()

        for cell_name in input_list:

            return_dict.update({cell_name: self.get_cell_value(cell_name)})

    def set_cell_value(self, cell_name, value):

        try:

            cell = self.spreadsheet.Cell(cell_name)
            cell.CellValue = value

        except:

            pass

    def get_cell_value(self, cell_name):

        try:

            cell = self.spreadsheet.Cell(cell_name)
            value = cell.CellValue

        except:

            return None

        return value