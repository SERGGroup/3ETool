from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QColor, QContextMenuEvent, QIcon
from PyQt5.QtWidgets import *
import os


class AbstractFilesManager(QDialog):

    def __init__(self, flags=None, *args, **kwargs):

        super().__init__(flags, *args, **kwargs)

        self.file_edit = None
        self.title = ""
        self.modules_handler = None
        self.selected_element_path = ""

    def __init_file_tree(self, dir_path):

        layout = QVBoxLayout()

        layout.addWidget(self.__get_tree_widget(dir_path))
        layout.addWidget(self.__get_buttons_widget())

        self.setLayout(layout)

    def __get_tree_widget(self, dir_path) -> QWidget:

        self.model = QFileSystemModel()
        self.model.setRootPath(dir_path)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(dir_path))
        self.tree.clicked.connect(self.on_selection_changed)
        self.tree.setColumnWidth(0, 250)

        return self.tree

    def __get_buttons_widget(self) -> QWidget:

        buttons_widget = QWidget()
        v_layout = QHBoxLayout()

        self.add_button = QPushButton()
        self.add_button.setText("Add")
        self.add_button.setEnabled(False)
        self.add_button.clicked.connect(self.on_button_add_pressed)

        self.rename_button = QPushButton()
        self.rename_button.setText("Rename")
        self.rename_button.clicked.connect(self.on_button_rename_pressed)
        self.rename_button.setEnabled(False)

        self.modify_button = QPushButton()
        self.modify_button.setText("Modify")
        self.modify_button.clicked.connect(self.on_button_modify_pressed)
        self.modify_button.setEnabled(False)

        self.delete_button = QPushButton()
        self.delete_button.setText("Delete")
        self.delete_button.clicked.connect(self.on_button_delete_pressed)
        self.delete_button.setEnabled(False)

        self.duplicate_button = QPushButton()
        self.duplicate_button.setText("Duplicate")
        self.duplicate_button.clicked.connect(self.on_button_duplicate_pressed)
        self.duplicate_button.setEnabled(False)

        v_layout.addWidget(self.add_button)
        v_layout.addWidget(self.rename_button)
        v_layout.addWidget(self.modify_button)
        v_layout.addWidget(self.delete_button)
        v_layout.addWidget(self.duplicate_button)

        buttons_widget.setLayout(v_layout)

        return buttons_widget

    def __enable_buttons(self):

        if not os.path.exists(self.selected_element_path):
            self.add_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.modify_button.setEnabled(False)
            self.duplicate_button.setEnabled(False)

        if os.path.isdir(self.selected_element_path):

            self.add_button.setEnabled(True)
            self.delete_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.modify_button.setEnabled(False)
            self.duplicate_button.setEnabled(False)

        elif os.path.isfile(self.selected_element_path):

            self.add_button.setEnabled(False)
            self.delete_button.setEnabled(True)
            self.rename_button.setEnabled(True)
            self.modify_button.setEnabled(True)
            self.duplicate_button.setEnabled(True)

        else:

            self.add_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.rename_button.setEnabled(False)
            self.modify_button.setEnabled(False)
            self.duplicate_button.setEnabled(False)

    def __rename_file(self, new_name, file_path):

        dir_path = os.path.dirname(file_path)
        new_path = os.path.join(dir_path, new_name + ".dat")

        self.selected_element_path = new_path
        os.rename(file_path, new_path)

    def on_selection_changed(self, signal):

        self.selected_element_path = self.model.filePath(signal)
        self.__enable_buttons()

    def on_button_add_pressed(self):
        raise NotImplementedError

    def on_button_rename_pressed(self):
        raise NotImplementedError

    def on_button_modify_pressed(self):
        raise NotImplementedError

    def on_button_delete_pressed(self):
        raise NotImplementedError

    def on_button_duplicate_pressed(self):
        raise NotImplementedError

    def show(self):

        self.setWindowTitle(self.title)
        self.setGeometry(300, 300, 650, 300)

        self.modules_handler.check_data_folder()
        self.selected_element_path = self.modules_handler.data_folder
        self.__init_file_tree(self.modules_handler.data_folder)

        super(AbstractFilesManager, self).show()


class WarningDialog(QDialog):

    # noinspection PyArgumentList
    def __init__(self, flags=None, *args, **kwargs):

        super().__init__(flags, *args, **kwargs)

        self.setWindowTitle("Warning")

        self.show_only_one_button = False
        self.button_on_click = None
        self.layout_is_set = False

        self.label = QLabel()
        self.yes_button = WarningButton()
        self.no_button = WarningButton()

        self.__init_layout()

    def __init_layout(self):

        self.button_on_click = self.__default_button_on_click
        self.yes_button.set_state(is_yes=True)
        self.no_button.set_state(is_yes=False)

    def set_label_text(self, text: str):
        self.label.setText(text)

    def set_layout(self, input_layout: QLayout = None):

        v_layout = QVBoxLayout()
        v_layout.addWidget(self.label)

        if not input_layout is None:
            __tmp_widget = QWidget()
            __tmp_widget.setLayout(input_layout)
            v_layout.addWidget(__tmp_widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.yes_button)

        if not self.show_only_one_button:
            button_layout.addWidget(self.no_button)

        __tmp_widget = QWidget()
        __tmp_widget.setLayout(button_layout)
        v_layout.addWidget(__tmp_widget)

        self.setLayout(v_layout)
        self.layout_is_set = True

    def set_button_text(self, text: str, set_button_yes=True):

        if set_button_yes:

            self.yes_button.setText(text)

        else:

            self.no_button.setText(text)

    def set_buttons_on_click(self, function):

        self.button_on_click = function

    def show(self):

        if not self.layout_is_set:
            self.set_layout()

        self.yes_button.clicked.connect(self.button_on_click)
        self.no_button.clicked.connect(self.button_on_click)

        super(WarningDialog, self).show()

    def __default_button_on_click(self):

        self.close()


class WarningButton(QPushButton):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.is_yes_button = False

    def set_state(self, is_yes):
        self.is_yes_button = is_yes


class AbstractTable(QTableView):

    def __init__(self, main_window, title):

        super().__init__()

        new_model = IndexSetterTableModel(main_window, title)
        self.setModel(new_model)

        self.currentRow = 0
        self.__set_actions()

    def contextMenuEvent(self, event: QContextMenuEvent):

        menu = QMenu(self)

        # Populating the menu with actions
        menu.addAction(self.add_action)
        menu.addAction(self.delete_action)
        menu.addAction(self.modify_action)

        self.currentRow = self.rowAt(event.pos().y())
        self.__enable_actions()

        # Launching the menu
        menu.exec(event.globalPos())

    def __set_actions(self):

        self.modify_action = QAction(self)
        self.modify_action.setText("&Modify")
        self.modify_action.setIcon(QIcon(":icon-modify"))
        self.modify_action.triggered.connect(self.onModifyPressed)

        self.delete_action = QAction(self)
        self.delete_action.setText("&Delete")
        self.delete_action.setIcon(QIcon(":icon-delete"))
        self.delete_action.triggered.connect(self.onDeletePressed)

        self.add_action = QAction(self)
        self.add_action.setText("&Add")
        self.add_action.setIcon(QIcon(":icon-add"))
        self.add_action.triggered.connect(self.onAddPressed)

    def __enable_actions(self):

        model = self.model()

        self.modify_action.setEnabled(model.context_action_activation(self.currentRow, "modify"))
        self.delete_action.setEnabled(model.context_action_activation(self.currentRow, "delete"))
        self.add_action.setEnabled(model.context_action_activation(self.currentRow, "add"))

    def onAddPressed(self):
        self.model().onAddClicked(self.currentRow)

    def onDeletePressed(self):
        self.model().onDeleteClicked(self.currentRow)

    def onModifyPressed(self):
        self.model().onModifyClicked(self.currentRow)


class IndexSetterTableModel(QAbstractTableModel):

    def __init__(self, main_window, type):

        super().__init__()

        self.type = type
        self.main_window = main_window

        self.row_count = 0
        if self.type in ["Input Indices", "Parameters Indices"]:
            self.column_count = 3

        else:
            self.column_count = 2

        self.data_dict = dict()

        self.additional_info_list = list()
        self.names_list = list()
        self.index_list = list()

        self.change_data_type()

    def change_data_type(self):

        if self.type == "Input Indices":

            __current_type_name = str(self.main_window.type_combobox.currentText())
            __current_type_class = self.main_window.modules_handler.import_correct_sub_class(__current_type_name)
            data: dict = __current_type_class.return_EES_needed_index()

        elif self.type == "Parameters Indices":

            data = dict()

        else:

            __current_type_name = str(self.main_window.type_combobox.currentText())
            __current_type_class = self.main_window.modules_handler.import_correct_sub_class(__current_type_name)
            data: dict = __current_type_class.return_EES_base_equations()

        self.load_data(data)

    def load_data(self, data):

        self.names_list = list()
        self.index_list = list()
        self.additional_info_list = list()

        self.data_dict = data

        for key in data.keys():

            self.names_list.append(str(key))

            if self.type in ["Input Indices", "Parameters Indices"]:

                self.index_list.append(data[key][0])
                self.additional_info_list.append(data[key][1])

            else:

                self.index_list.append(len(data[key]["variables"]))

        self.row_count = len(self.names_list)

    def rowCount(self, parent=QModelIndex()):
        return self.row_count

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    # noinspection PyMethodOverriding
    def headerData(self, section, orientation, role):

        if role == Qt.DisplayRole:

            if orientation == Qt.Horizontal:

                if self.type == "Input Indices":
                    name_tuple = ("Index Name", "Index Reference", "Multiple Input")

                elif self.type == "Parameters Indices":
                    name_tuple = ("Index Name", "Index Reference", "Related Option")

                else:
                    name_tuple = ("Name", "n° Connections", "")

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

                if self.type == "Input Indices":
                    return Qt.AlignCenter

                elif self.type == "Parameters Indices":
                    return Qt.AlignLeft | Qt.AlignVCenter

                else:
                    return Qt.AlignCenter

        elif role == Qt.CheckStateRole:

            if index.column() == 2 and self.type == "Input Indices":

                if self.additional_info_list[row]:
                    return Qt.Checked

                else:
                    return Qt.Unchecked

        return None

    def flags(self, index):

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def context_action_activation(self, row, action):

        if self.type in ["Input Indices", "Parameters Indices"]:

            return False

        else:

            return True

    # <------------ MENU ON CLICK METHODS ------------>

    def onAddClicked(self, row):

        if self.type in ["Input Indices", "Parameters Indices"]:

            pass

        else:

            pass

    def onModifyClicked(self, row):

        if self.type in ["Input Indices", "Parameters Indices"]:

            pass

        else:

            pass

    def onDeleteClicked(self, row):

        if self.type in ["Input Indices", "Parameters Indices"]:

            pass

        else:

            pass