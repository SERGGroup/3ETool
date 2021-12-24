from EEETools.MainModules.main_module import ArrayHandler
from EEETools.Tools.GUIElements.gui_base_classes import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys


class CheckConnectionWidget(QDialog):

    # noinspection PyArgumentList
    def __init__(self, array_hander: ArrayHandler):

        super().__init__()

        self.array_hander = array_hander
        self.setWindowTitle("Topology Inspection Window")

        self.main_layout = QVBoxLayout(self)
        self.__init_tab_widget()
        self.setLayout(self.main_layout)

        self.__update_tab("Blocks")
        self.__update_tab("Connections")

    def __init_tab_widget(self):

        self.tab_widget = QTabWidget()

        self.__init_tab_block()
        self.__init_tab_connection()

        self.main_layout.addWidget(self.tab_widget)

    def __init_tab_block(self):

        self.tab_block = QWidget()
        self.tab_block_layout = QVBoxLayout()

        self.__init_block_h_layout(0)
        self.__init_block_h_layout(1)
        self.__init_block_h_layout(2)
        self.__init_block_h_layout(3)

        self.tab_block.setLayout(self.tab_block_layout)
        self.tab_widget.addTab(self.tab_block, "Blocks")

    def __init_block_h_layout(self, layout_layer):

        h_layout_new = QHBoxLayout()

        if layout_layer == 0:

            name_label = QLabel("Block ID")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.block_ID_combobox = QComboBox()

            for ID in self.array_hander.standard_block_IDs:
                self.block_ID_combobox.addItem(str(ID))

            self.block_ID_combobox.currentIndexChanged.connect(self.on_combo_box_changed)
            self.block_ID_combobox.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.block_ID_combobox)

        elif layout_layer == 1:

            name_label = QLabel("Block Name:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.name_label = QLabel("Block Name")
            self.name_label.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.name_label)

        elif layout_layer == 2:

            name_label = QLabel("Block Type:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.type_label = QLabel("Block Type")
            self.type_label.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.type_label)

        else:

            h_layout_new.addLayout(self.__init_connections_tablesview())

        self.tab_block_layout.addLayout(h_layout_new)

    def __init_connections_tablesview(self):

        self.tables = dict()

        v_layout_right = QVBoxLayout()

        v_splitter = QSplitter(Qt.Vertical)
        v_splitter = self.init_table_view(v_splitter, "Input Connections")
        v_splitter = self.init_table_view(v_splitter, "Output Connections")

        v_layout_right.addWidget(v_splitter)

        return v_layout_right

    def init_table_view(self, layout, title_str):

        widget = QWidget()
        v_layout = QVBoxLayout()
        title_label_input = QLabel(title_str)
        title_label_input.setFont(QFont('Helvetica 30 bold'))

        new_table = CheckerAbstractTable(self, title_str)

        header = new_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        v_layout.addWidget(title_label_input)
        v_layout.addWidget(new_table)

        widget.setLayout(v_layout)
        layout.addWidget(widget)
        self.tables.update({title_str: new_table})

        return layout

    def __init_tab_connection(self):

        self.tab_connection = QWidget()
        self.tab_conn_layout = QVBoxLayout()

        self.__init_conn_h_layout(0)
        self.__init_conn_h_layout(1)
        self.__init_conn_h_layout(2)
        self.__init_conn_h_layout(3)

        self.tab_connection.setLayout(self.tab_conn_layout)
        self.tab_widget.addTab(self.tab_connection, "Connections")

    def __init_conn_h_layout(self, layout_layer):

        h_layout_new = QHBoxLayout()

        if layout_layer == 0:

            name_label = QLabel("Conn ID")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.conn_ID_combobox = QComboBox()

            for ID in self.array_hander.standard_conn_IDs:
                self.conn_ID_combobox.addItem(str(ID))

            self.conn_ID_combobox.currentIndexChanged.connect(self.on_combo_box_changed)
            self.conn_ID_combobox.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.conn_ID_combobox)

        elif layout_layer == 1:

            name_label = QLabel("Conn Name:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.conn_name_label = QLabel("Conn Name")
            self.conn_name_label.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.conn_name_label)

        elif layout_layer == 2:

            name_label = QLabel("From Block:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.from_block_label = QLabel("From Block:")
            self.from_block_label.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.from_block_label)

        else:

            name_label = QLabel("To Block:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.to_block_label = QLabel("To Block:")
            self.to_block_label.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.to_block_label)

        self.tab_conn_layout.addLayout(h_layout_new)

    def on_combo_box_changed(self):

        sender = self.sender()
        if sender == self.block_ID_combobox:

            self.__update_tab("Blocks")

        else:

            self.__update_tab("Connections")

    def __update_tab(self, tab_to_update):

        if tab_to_update == "Blocks":

            try:

                new_index = int(self.block_ID_combobox.currentText())
                new_block = self.array_hander.find_block_by_ID(new_index)

            except:

                new_block = None

            if new_block is not None:

                self.name_label.setText(new_block.name)
                self.type_label.setText(new_block.type)

            else:

                self.name_label.setText("")
                self.type_label.setText("")

            for key in self.tables.keys():

                new_model = CheckerIndexSetterTableModel(self, key)
                self.tables[key].setModel(new_model)

        else:

            try:

                new_index = int(self.conn_ID_combobox.currentText())
                new_conn = self.array_hander.find_connection_by_ID(new_index)

            except:

                new_conn = None

            if new_conn is not None:

                self.conn_name_label.setText(new_conn.name)

                block_labels = self.get_connection_string(new_conn)

                self.from_block_label.setText(block_labels["from"])
                self.to_block_label.setText(block_labels["to"])

            else:

                self.name_label.setText("")
                self.type_label.setText("")

    @staticmethod
    def get_connection_string(connection):

        reutrn_dict = dict()

        if connection.is_system_input:

            reutrn_dict.update({"from": "System Input - cost: {}€/kJ".format(connection.rel_cost)})

        else:

            other_block = connection.from_block
            reutrn_dict.update({"from": "{} - {}".format(other_block.get_main_ID, other_block.get_main_name)})

        if connection.is_system_output:

            if connection.is_loss:
                reutrn_dict.update({"to": "System Loss"})

            else:
                reutrn_dict.update({"to": "System Useful Effect"})

        else:

            other_block = connection.to_block
            reutrn_dict.update({"to": "{} - {}".format(other_block.get_main_ID, other_block.get_main_name)})

        return reutrn_dict

    @classmethod
    def launch(cls, array_handler):

        app = QApplication(sys.argv)
        new_self = cls(array_handler)
        new_self.show()
        app.exec_()


class CheckerAbstractTable(QTableView):

    def __init__(self, main_window, title):

        super().__init__()
        new_model = self.table_model(main_window, title)
        self.setModel(new_model)

        self.currentRow = 0
        self.currentCol = 0
        self.__set_actions()

    def contextMenuEvent(self, event: QContextMenuEvent):

        menu = QMenu(self)
        menu.addAction(self.show_action)
        menu.exec(event.globalPos())

    def __set_actions(self):
        self.show_action = QAction(self)
        self.show_action.setText("&Show")
        self.show_action.triggered.connect(self.onShowPressed)

    def onShowPressed(self):

        try:

            item = self.selectedIndexes()[0]
            self.model().onShowPressed(item.row(), item.column())

        except:

            pass

    @property
    def table_model(self):
        return CheckerIndexSetterTableModel


class CheckerIndexSetterTableModel(QAbstractTableModel):

    def __init__(self, main_window: CheckConnectionWidget, type):

        super().__init__()

        self.type = type
        self.main_window = main_window

        self.row_count = 0
        self.column_count = 3

        self.data_dict = dict()

        self.additional_info_list = list()
        self.names_list = list()
        self.index_list = list()

        self.change_data_type()

    def change_data_type(self):

        __current_block_ID = str(self.main_window.block_ID_combobox.currentText())
        __block = self.main_window.array_hander.find_block_by_ID(__current_block_ID)

        if __block is None:

            connection = []

        elif self.type == "Input Connections":

            connection = __block.external_input_connections

        else:

            connection = __block.external_output_connections

        self.load_connections(connection)

    def load_connections(self, connection_list):

        self.names_list = list()
        self.index_list = list()
        self.additional_info_list = list()

        self.connection_list = connection_list

        if len(connection_list) > 0:

            for connection in connection_list:

                self.names_list.append(str(connection.name))
                self.index_list.append(str(connection.index))
                self.additional_info_list.append(self.__get_connection_string(connection))

        else:

            self.names_list.append("")
            self.index_list.append("")
            self.additional_info_list.append("")

        self.row_count = len(self.names_list)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    # noinspection PyMethodOverriding
    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole:

            if orientation == Qt.Horizontal:

                if self.type == "Input Connections":
                    name_tuple = ("Conn Name", "Conn Index", "from Block")

                else:
                    name_tuple = ("Conn Name", "Conn Index", "to Block")

                return name_tuple[section]

            else:
                return "{}".format(section)

        else:

            return None

    def data(self, index, role=Qt.DisplayRole):

        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:

            if column == 0:
                return self.names_list[row]

            elif column == 1:
                return self.index_list[row]

            elif column == 2:
                return str(self.additional_info_list[row])

        elif role == Qt.BackgroundRole:
            return QColor(Qt.white)

        elif role == Qt.TextAlignmentRole:

            if column == 0:
                return Qt.AlignLeft | Qt.AlignVCenter

            elif column == 1:
                return Qt.AlignCenter

            else:

                return Qt.AlignCenter

        return None

    def flags(self, index):

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def onShowPressed(self, row, col):

        if col == 2:

            value = str(self.additional_info_list[row])
            block_ID = int(value.split(" - ")[0])

            index = self.main_window.block_ID_combobox.findData(block_ID)

            if not index == -1:

                self.main_window.block_ID_combobox.setCurrentIndex(index)
                self.main_window.on_combo_box_changed()

        else:

            connection = self.connection_list[row]
            index = self.main_window.conn_ID_combobox.findData(connection.ID)

            if not index == -1:

                self.main_window.conn_ID_combobox.setCurrentIndex(index)
                self.main_window.tab_widget.setCurrentIndex(1)
                self.main_window.on_combo_box_changed()

    def __get_connection_string(self, connection):

        if self.type == "Input Connections":

            return self.main_window.get_connection_string(connection)["from"]

        else:

            return self.main_window.get_connection_string(connection)["to"]