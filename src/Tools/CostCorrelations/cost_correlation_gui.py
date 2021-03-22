from src.Tools.CostCorrelations.cost_correlation_classes import CostCorrelationHandler
from src.Tools.CostCorrelations.cost_correlation_classes import AbstractCostCorrelation
from src.Tools.CostCorrelations.cost_correlation_classes import Parameter
from src.Tools.GUIElements.gui_base_classes import *
from PyQt5.QtGui import QKeySequence, QFont, QDoubleValidator
from shutil import copy2 as copy_file
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import os


class CostCorrelationFilesManager(AbstractFilesManager):

    def __init__(self, flags=None, *args, **kwargs):

        super().__init__(flags, *args, **kwargs)

        self.title = "Cost Correlation Manager"
        self.modules_handler = CostCorrelationHandler()

    def on_button_add_pressed(self):

        if not os.path.isdir(self.selected_element_path):

            self.dir_name = os.path.dirname(self.selected_element_path)

        else:

            self.dir_name = self.selected_element_path

        warning_text = "Select a correlation format"

        self.add_new_dialog = WarningDialog(self)
        self.add_new_dialog.set_label_text(warning_text)
        self.add_new_dialog.set_buttons_on_click(self.on_add_new_dialog_clicked)

        self.add_combo_box = QComboBox()
        self.add_combo_box.addItems(self.modules_handler.list_modules())

        combo_box_layout = QHBoxLayout()
        combo_box_layout.addWidget(self.add_combo_box)
        self.add_new_dialog.set_layout(combo_box_layout)

        self.add_new_dialog.set_button_text("Add", set_button_yes=True)
        self.add_new_dialog.set_button_text("Cancel", set_button_yes=False)

        self.add_new_dialog.show()

    def on_add_new_dialog_clicked(self):

        sender = self.sender()

        if sender.is_yes_button:

            __sub_class_name = self.add_combo_box.currentText()
            __sub_class = self.modules_handler.import_correct_sub_class(__sub_class_name)()

            component_type = self.__get_component_type()
            __sub_class.component_type = component_type

            modify_widget = __sub_class.edit_correlation_widget
            modify_widget.show()

        self.add_new_dialog.close()

    def on_button_modify_pressed(self):

        __sub_class = self.modules_handler.open_file(self.selected_element_path)

        modify_widget = __sub_class.edit_correlation_widget
        modify_widget.show()

    def on_button_delete_pressed(self):

        dir_name = os.path.dirname(self.selected_element_path)

        dir_name = os.path.basename(dir_name)
        filename = os.path.basename(self.selected_element_path)

        warning_text = "Do you really want to delete file "
        warning_text += os.path.join(dir_name, filename)
        warning_text += "?"

        self.delete_warning_dialog = WarningDialog(self)
        self.delete_warning_dialog.set_label_text(warning_text)
        self.delete_warning_dialog.set_buttons_on_click(self.on_delete_warning_clicked)
        self.delete_warning_dialog.set_button_text("Yes", set_button_yes=True)
        self.delete_warning_dialog.set_button_text("No", set_button_yes=False)

        self.delete_warning_dialog.show()

    def on_delete_warning_clicked(self):

        sender = self.sender()

        if sender.is_yes_button:
            if os.path.exists(self.selected_element_path):
                os.remove(self.selected_element_path)

        self.__enable_buttons()
        self.delete_warning_dialog.close()

    def on_button_rename_pressed(self):

        dir_name = os.path.dirname(self.selected_element_path)

        dir_name = os.path.basename(dir_name)
        filename = os.path.basename(self.selected_element_path)

        label_text = "insert new name for file "
        label_text += os.path.join(dir_name, filename)

        self.rename_line_edit = QLineEdit()
        hint_label = QLabel("new name:")

        hLayout = QHBoxLayout()
        hLayout.addWidget(hint_label)
        hLayout.addWidget(self.rename_line_edit)

        self.rename_warning_dialog = WarningDialog(self)
        self.rename_warning_dialog.set_layout(hLayout)
        self.rename_warning_dialog.set_label_text(label_text)
        self.rename_warning_dialog.set_buttons_on_click(self.on_rename_warning_clicked)
        self.rename_warning_dialog.set_button_text("Rename", set_button_yes=True)
        self.rename_warning_dialog.set_button_text("Cancel", set_button_yes=False)

        self.rename_warning_dialog.show()

    def on_rename_warning_clicked(self):

        sender = self.sender()

        if sender.is_yes_button:
            new_name = self.rename_line_edit.text()
            self.__rename_file(new_name, self.selected_element_path)
            self.__enable_buttons()

        self.rename_warning_dialog.close()

    def on_button_duplicate_pressed(self):

        dir_name = os.path.dirname(self.selected_element_path)

        dir_name = os.path.basename(dir_name)
        filename = os.path.basename(self.selected_element_path)

        warning_text = "Do you really want to duplicate file "
        warning_text += os.path.join(dir_name, filename)
        warning_text += "?"

        self.duplicate_warning_dialog = WarningDialog(self)

        self.duplicate_warning_dialog.set_label_text(warning_text)

        self.duplicate_warning_dialog.set_button_text("Yes", set_button_yes=True)
        self.duplicate_warning_dialog.set_button_text("No", set_button_yes=False)
        self.duplicate_warning_dialog.set_buttons_on_click(self.on_duplicate_warning_pressed)

        self.duplicate_warning_dialog.show()

    def on_duplicate_warning_pressed(self):

        sender = self.sender()

        if sender.is_yes_button:

            if os.path.exists(self.selected_element_path):

                dir_name = os.path.dirname(self.selected_element_path)
                filename = os.path.basename(self.selected_element_path)

                if ".dat" in filename:
                    filename = filename.split(".dat")[0]
                    file_extension = ".dat"

                elif ".xml" in filename:
                    filename = filename.split(".xml")[0]
                    file_extension = ".xml"

                else:

                    file_extension = ""

                i = 1
                new_path = os.path.join(dir_name, filename + "(1)" + file_extension)

                while os.path.exists(new_path):
                    i += 1
                    new_path = os.path.join(dir_name, filename + "(" + str(i) + ")" + file_extension)

                copy_file(self.selected_element_path, new_path)

        self.duplicate_warning_dialog.close()

    def __rename_file(self, new_name, file_path):

        self.modules_handler.rename_file(new_name, file_path)
        super(CostCorrelationFilesManager, self).__rename_file(new_name, file_path)

    def __get_component_type(self):

        if not os.path.isdir(self.selected_element_path):

            dir_name = os.path.dirname(self.selected_element_path)

        else:

            dir_name = self.selected_element_path

        return os.path.basename(dir_name)


class BaseEditCorrelationWidget(QDialog):

    def __init__(self, cost_correlation_class: AbstractCostCorrelation):

        super().__init__()

        self.title = ""
        self.cost_correlation = cost_correlation_class

        self.tab_widget = BaseEditCorrelationTabWidget()
        self.buttons_layout = QHBoxLayout()

        self.button_save = QPushButton()
        self.button_new = QPushButton()

        self.layout_is_set = False

    def show(self):

        if not self.layout_is_set:
            self.__init_main_layout()

        super(BaseEditCorrelationWidget, self).show()

    def enable_buttons(self):

        self.button_save.setEnabled(self.is_ready_for_saving)

    def __init_main_layout(self):

        self.setWindowTitle(self.title)
        self.__init_button_layout()

        __button_widget = QWidget()
        __button_widget.setLayout(self.buttons_layout)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(__button_widget)

        self.setLayout(main_layout)
        self.layout_is_set = True

    def __init_tab_layout(self):

        self.coefficient_widget = CoefficientWidget(self.cost_correlation.coefficient_dict, self)

    def __init_button_layout(self):

        self.button_save.setText("Save (CTRL-S)")
        self.button_save.clicked.connect(self.on_button_pressed)

        self.button_new.setText("New (CTRL-N)")
        self.button_new.clicked.connect(self.on_button_pressed)

        self.__set_buttons_shortcut()

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.button_save)
        self.buttons_layout.addWidget(self.button_new)

        self.enable_buttons()

    def __set_buttons_shortcut(self):

        sequence_save = QKeySequence(Qt.CTRL + Qt.Key_S)
        self.button_save.setShortcut(sequence_save)

        sequence_new = QKeySequence(Qt.CTRL + Qt.Key_N)
        self.button_new.setShortcut(sequence_new)

    @property
    def is_ready_for_saving(self):
        """method to be overloaded"""
        return False

    # <------------------------------------------------->
    # <------------ BUTTON ON CLICK METHODS ------------>
    # <------------------------------------------------->

    def on_button_pressed(self):

        sender = self.sender()

        if "Save" in sender.text():

            warning_text = "Do you want to save the file? Data will be overwritten"
            self.on_click_function = self.__save

        else:

            warning_text = "By clicking \"Continue\" all your progress will be lost"
            self.on_click_function = self.__reset_dialog

        self.warning_dialog = WarningDialog(self)

        self.warning_dialog.set_label_text(warning_text)
        self.warning_dialog.set_buttons_on_click(self.on_warning_clicked)

        self.warning_dialog.set_button_text("Continue", set_button_yes=True)
        self.warning_dialog.set_button_text("Cancel", set_button_yes=False)

        self.warning_dialog.show()

    def on_warning_clicked(self):

        sender = self.sender()
        if sender.is_yes_button:
            self.on_click_function()

        self.warning_dialog.close()

    def __save(self):

        self.__update()
        self.cost_correlation.export_to_file()

    def __reset_dialog(self):
        raise NotImplementedError

    def __update(self):
        raise NotImplementedError

    # <------------------------------------------------->
    # <------------ WIDGETS GETTER AND SETTER ----------->
    # <------------------------------------------------->

    @property
    def header_widget(self):
        return self.tab_widget.tab_main

    @header_widget.setter
    def header_widget(self, input_widget):
        self.tab_widget.add_widget(input_widget, "Main")

    @property
    def parameter_widget(self):
        return self.tab_widget.tab_parameters

    @parameter_widget.setter
    def parameter_widget(self, input_widget):
        self.tab_widget.add_widget(input_widget, "Parameters")

    @property
    def coefficient_widget(self):
        return self.tab_widget.tab_coefficient

    @coefficient_widget.setter
    def coefficient_widget(self, input_widget):
        self.tab_widget.add_widget(input_widget, "Coefficients")


class BaseEditCorrelationTabWidget(QTabWidget):

    def __init__(self):

        super().__init__()

        self.tab_main = None
        self.tab_parameters = None
        self.tab_coefficient = None

    def add_widget(self, widget: QWidget, widget_type):

        found = True

        if widget_type == "Main" and self.tab_main is None:
            self.tab_main = widget

        elif  widget_type == "Parameters" and self.tab_parameters is None:
            self.tab_parameters = widget

        elif  widget_type == "Coefficients" and self.tab_coefficient is None:
            self.tab_coefficient = widget

        else:
            found = False

        if found:
            self.addTab(widget, widget_type)


class ParametersWidget(QWidget):

    def __init__(self, parameter_dict: dict, parent_class: BaseEditCorrelationWidget):

        super().__init__()
        self.splitter = QSplitter()
        self.parameter_dict = parameter_dict

        self.list_view = None
        self.parameters_widgets = dict()

    def init_layout(self):

        self.list_view = QListView()
        self.list_view.clicked.connect(self.__on_list_view_clicked)

        row = 0
        for key in self.parameter_dict.keys():

            self.list_view.insertItem(row, key)
            row += 1


    #
    # def __on_list_view_clicked(self):
    #
    #
    #
    # def __show_currect_widget(self, item_key: str):
    #
    #


    @property
    def is_ready_for_saving(self):

        for edit_text in [self.unit_edit, self.note_edit, self.range_low_edit, self.range_high_edit]:

            if edit_text.text() == "":
                return False

        return True


class SingleParameterWidget(QWidget):

    def __init__(self, parameter_class: Parameter, parent_class: BaseEditCorrelationWidget):

        super().__init__()

        self.set_edit_layout = False
        self.parameter = parameter_class
        self.parent_class = parent_class

        self.main_layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

    def init_layout(self):

        if self.set_edit_layout:

            self.__init_edit_objects()
            self.__init_edit_layout()

        else:
            self.__init_set_objects()
            self.__init_set_layout()

        self.setLayout(self.main_layout)

    def __init_edit_objects(self):

        self.unit_edit = QLineEdit()
        self.note_edit = QTextEdit()
        self.range_low_edit = QLineEdit()
        self.range_high_edit = QLineEdit()

        self.range_low_edit.setValidator(QDoubleValidator())
        self.range_high_edit.setValidator(QDoubleValidator())

        self.unit_edit.setText(self.parameter.measure_unit)
        self.note_edit.setText(self.parameter.note)
        self.range_low_edit.setText(str(self.parameter.range.low))
        self.range_high_edit.setText(str(self.parameter.range.high))

        self.unit_edit.setObjectName("unit_edit")
        self.note_edit.setObjectName("note_edit")
        self.range_low_edit.setObjectName("range_low_edit")
        self.range_high_edit.setObjectName("range_high_edit")

        self.unit_edit.textChanged.connect(self.on_text_edit_change)
        self.note_edit.textChanged.connect(self.on_text_edit_change)
        self.range_low_edit.textChanged.connect(self.on_text_edit_change)
        self.range_high_edit.textChanged.connect(self.on_text_edit_change)

    def __init_set_objects(self):

        self.value_edit = QLineEdit()
        self.unit_edit = QLabel()
        self.note_edit = QLabel()
        self.range_low_edit = QLabel()
        self.range_high_edit = QLabel()

        self.note_edit.setWordWrap(True)
        self.value_edit.setObjectName("value_edit")
        self.value_edit.textChanged.connect(self.on_text_edit_change)
        self.value_edit.setValidator(QDoubleValidator())

        self.value_edit.setText(str(self.parameter.value))
        self.unit_edit.setText(self.parameter.measure_unit)
        self.note_edit.setText(self.parameter.note)
        self.range_low_edit.setText(str(self.parameter.range.low))
        self.range_high_edit.setText(str(self.parameter.range.high))

    def __init_edit_layout(self):

        # <----------- FIRST ROW ----------->

        title_label_input = QLabel()
        title_label_input.setText(self.parameter.name)
        title_label_input.setFont(QFont('Helvetica 30 bold'))

        self.grid_layout.addWidget(title_label_input, 0, 0)

        # <----------- SECOND ROW ----------->

        measure_unit_label = QLabel()
        measure_unit_label.setText("Measurement Unit")

        self.grid_layout.addWidget(measure_unit_label, 1, 0)
        self.grid_layout.addWidget(self.unit_edit, 1, 1)

        # <----------- THIRD ROW ----------->

        range_label = QLabel()
        range_label.setText("Range")

        range_layout = QHBoxLayout()
        range_layout.addWidget(self.range_low_edit)
        range_layout.addWidget(QLabel("->"))
        range_layout.addWidget(self.range_high_edit)

        range_widget = QWidget()
        range_widget.setLayout(range_layout)

        self.grid_layout.addWidget(range_label, 2, 0)
        self.grid_layout.addWidget(range_widget, 2, 1)

        # <----------- FINAL ROW ----------->

        grid_layout_widget = QWidget()
        grid_layout_widget.setLayout(self.grid_layout)

        self.main_layout.addWidget(grid_layout_widget)
        self.main_layout.addWidget(self.note_edit)

    def __init_set_layout(self):

        # <----------- FIRST ROW ----------->

        title_label_input = QLabel()
        title_label_input.setText(self.parameter.name)
        title_label_input.setFont(QFont('Helvetica 30 bold'))

        self.grid_layout.addWidget(title_label_input, 0, 0)

        # <----------- SECOND ROW ----------->

        measure_unit_label = QLabel()
        measure_unit_label.setText("Measurement Unit")

        self.grid_layout.addWidget(measure_unit_label, 1, 0)
        self.grid_layout.addWidget(self.unit_edit, 1, 1)

        # <----------- THIRD ROW ----------->

        range_label = QLabel()
        range_label.setText("Range")

        range_layout = QHBoxLayout()
        range_layout.addWidget(self.range_low_edit)
        range_layout.addWidget(QLabel("->"))
        range_layout.addWidget(self.range_high_edit)

        range_widget = QWidget()
        range_widget.setLayout(range_layout)

        self.grid_layout.addWidget(range_label, 2, 0)
        self.grid_layout.addWidget(range_widget, 2, 1)

        # <----------- FINAL ROW ----------->

        grid_layout_widget = QWidget()
        grid_layout_widget.setLayout(self.grid_layout)

        self.main_layout.addWidget(grid_layout_widget)
        self.main_layout.addWidget(self.note_edit)

    def on_text_edit_change(self):

        name = self.sender().objectName()

        if name == "value_edit":

            try:
                self.parameter.value = float(self.value_edit.text())
            except:
                self.parameter.value = 0.0

        elif name == "unit_edit":

            self.parameter.measure_unit = self.unit_edit.text()

        elif name == "note_edit":

            self.parameter.note = self.note_edit.toPlainText()

        elif name == "range_low_edit" or name == "range_high_edit":

            try:
                low = float(self.range_low_edit.text())
            except:
                low = 0.0

            try:
                high = float(self.range_high_edit.text())
            except:
                high = 0.0

            self.parameter.range.initialize([low, high])

        self.parent_class.enable_buttons()

    @property
    def is_ready_for_saving(self):

        for edit_text in [self.unit_edit, self.note_edit, self.range_low_edit, self.range_high_edit]:

            if edit_text.text() == "":
                return False

        return True


class CoefficientWidget(QWidget):

    def __init__(self, coefficient_dict: dict, parent_class: BaseEditCorrelationWidget):

        super().__init__()

        self.coefficient_dict = coefficient_dict
        self.parent_class = parent_class

        self.main_layout = QGridLayout()
        self.widget_dict = dict()

        self.__init_layout()

    def __init_layout(self):

        row = 0

        for key in self.coefficient_dict.keys():

            self.__extend_grid_layout(key, row)
            row += 1

        self.setLayout(self.main_layout)

    def __extend_grid_layout(self, key, row):

        col = 1
        coefficient = self.coefficient_dict[key]

        title_label_input = QLabel()
        title_label_input.setText("<b>"+ key + ":<b>")
        title_label_input.setAlignment(Qt.AlignRight)

        self.grid_layout.addWidget(title_label_input, row, col)

        i = 0
        col += 1
        first_col = col
        edit_test_list = list()

        while i < coefficient["array size"]:

            col = first_col + i

            edit_text = QLineEdit()
            edit_text.setValidator(QDoubleValidator())
            edit_text.textChanged.connect(self.on_text_edit_change)

            edit_test_list.append(edit_text)
            self.grid_layout.addWidget(edit_text, row, col)

            i += 1

        self.widget_dict.update({key: edit_test_list})

    def on_text_edit_change(self):

        self.parent_class.enable_buttons()

    @property
    def coefficient_values(self):

        return_dict = dict()

        for key in self.widget_dict.keys():

            return_list = list()

            for edit_text in self.widget_dict[key]:

                try:
                    return_list.append(float(edit_text.text()))

                except:
                    return_list.append(0.0)

            return_dict.update({key: return_list})

        return return_dict

    @property
    def is_ready_for_saving(self):

        for key in self.widget_dict.keys():

            for edit_text in self.widget_dict[key]:

                if edit_text.text() == "":

                    return False

        return True