from src.Tools.EESCodeGenerator.EES_code import Code
from src.Tools.modules_handler import ModulesHandler
from src.Tools.GUIElements.gui_base_classes import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt
from shutil import copy2 as copy_file
import os
from src import costants


class DefineEESTextWidget(QDialog):

    # noinspection PyArgumentList
    def __init__(self, flags=None, *args, **kwargs):

        super().__init__(flags, *args, **kwargs)
        self.modules_handler = ModulesHandler()

        self.init_title()
        self.tables = dict()

        self.main_layout = QVBoxLayout(self)

        self.init_h_layout(0)
        self.init_h_layout(1)
        self.init_h_layout(2)
        self.init_h_layout(3)

        self.setLayout(self.main_layout)

        self.file_manager = None
        self.__enable_buttons()

    def init_title(self, EES_code_name="New EES code"):

        self.EES_code_name = EES_code_name
        self.is_saved = False
        self.__update_title()

    def init_h_layout(self, layout_layer):

        h_layout_new = QHBoxLayout()

        if layout_layer == 0:

            name_label = QLabel("Insert a name:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.name_edit_text = QLineEdit()
            self.name_edit_text.setFont(QFont("Helvetica 20 Bold"))
            self.name_edit_text.textChanged.connect(self.on_text_changed)

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.name_edit_text)

        elif layout_layer == 1:

            name_label = QLabel("Select the Type:")
            name_label.setFont(QFont("Helvetica 20"))
            name_label.setMinimumWidth(100)
            name_label.setMaximumWidth(100)

            self.type_combobox = QComboBox()
            self.type_combobox.addItems(self.modules_handler.name_list)
            self.type_combobox.currentIndexChanged.connect(self.on_combo_box_changed)
            self.type_combobox.setFont(QFont("Helvetica 20 Bold"))

            h_layout_new.addWidget(name_label)
            h_layout_new.addWidget(self.type_combobox)

        elif layout_layer == 2:

            h_layout_new.addLayout(self.init_left_layout())
            h_layout_new.addLayout(self.init_right_layout())

        else:

            self.button_save = QPushButton()
            self.button_save.setText("Save (CTRL-S)")
            self.button_save.clicked.connect(self.on_save_button_pressed)

            self.button_new = QPushButton()
            self.button_new.setText("New (CTRL-N)")
            self.button_new.clicked.connect(self.on_new_button_pressed)

            self.__set_buttons_shortcut()

            h_layout_new.addWidget(self.button_save)
            h_layout_new.addWidget(self.button_new)

            self.__enable_buttons()

        self.main_layout.addLayout(h_layout_new)

    def init_left_layout(self):

        font = QFont()
        font.setFamily(costants.EES_CODE_FONT_FAMILY)
        font.setBold(True)

        self.input_script = QTextEdit("\"insert here your EES code ...\"")
        self.input_script.setMinimumWidth(400)
        self.input_script.setAcceptRichText(True)
        self.input_script.textChanged.connect(self.on_text_changed)
        self.input_script.setFont(font)

        self.code = Code(self)
        self.on_format_pressed()

        self.button_format = QPushButton()
        self.button_format.setText("Format Code (CTRL-F)")
        self.button_format.pressed.connect(self.on_format_pressed)

        v_layout_left = QVBoxLayout()
        v_layout_left.addWidget(self.input_script)
        v_layout_left.addWidget(self.button_format)

        return v_layout_left

    def init_right_layout(self):

        self.tables = dict()

        v_layout_right = QVBoxLayout()

        v_splitter = QSplitter(Qt.Vertical)
        v_splitter = self.init_table_view(v_splitter, "Input Indices")
        v_splitter = self.init_table_view(v_splitter, "Parameters Indices")
        v_splitter = self.init_table_view(v_splitter, "Equations")

        v_layout_right.addWidget(v_splitter)

        return v_layout_right

    def init_table_view(self, layout, title_str):

        widget = QWidget()
        v_layout = QVBoxLayout()
        title_label_input = QLabel(title_str, font=QFont('Helvetica 30 bold'))

        new_table = AbstractTable(self, title_str)
        new_table.setMinimumWidth(350)
        new_table.setMaximumWidth(350)

        header = new_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        if title_str in ["Input Indices", "Parameters Indices"]:
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        v_layout.addWidget(title_label_input)
        v_layout.addWidget(new_table)

        widget.setLayout(v_layout)
        layout.addWidget(widget)
        self.tables.update({title_str: new_table})

        return layout

    def open_file(self, file_path):

        try:
            root = self.code.read_file(file_path)

        except:

            save_warning_dialog = WarningDialog(self)

            save_warning_dialog.set_label_text("The file has been compromised and cannot be opened.\n"
                                               "An empty file will be opened instead")

            save_warning_dialog.show_only_one_button = True
            save_warning_dialog.set_button_text("ok", set_button_yes=True)
            save_warning_dialog.show()

            self.__reset_dialog()

        else:

            header = root.find("header")
            code_name = header.get("name")
            component_type = header.get("component_type")

            EES_code = root.find("EESCode").text

            self.name_edit_text.setText(code_name)
            self.input_script.setText(EES_code)
            self.set_combobox_name(component_type)

            file_name = code_name + ".xml"
            folder_name = self.modules_handler.get_module_name(component_type)
            self.EES_code_name = os.path.join(folder_name, file_name)

            self.__update_title()
            self.on_format_pressed()

    def set_combobox_name(self, name):

        index = self.modules_handler.get_name_index(name)

        if index == -1:
            index = 0

        self.type_combobox.setCurrentIndex(index)

    def on_combo_box_changed(self):

        new_model = IndexSetterTableModel(self, "Input Indices")
        self.tables["Input Indices"].setModel(new_model)

        new_model = IndexSetterTableModel(self, "Equations")
        self.tables["Equations"].setModel(new_model)

    def on_text_changed(self):

        try:

            self.__enable_buttons()
            self.is_saved = False
            self.__update_title()

        except:

            pass

    def on_new_button_pressed(self):

        self.new_warning_dialog = WarningDialog(self)
        self.new_warning_dialog.set_label_text("By clicking \"Continue\" all your progress will be lost")
        self.new_warning_dialog.set_buttons_on_click(self.on_new_warning_clicked)
        self.new_warning_dialog.set_button_text("Continue", set_button_yes=True)
        self.new_warning_dialog.set_button_text("Cancel", set_button_yes=False)

        self.new_warning_dialog.show()

    def on_new_warning_clicked(self):

        sender = self.sender()
        if sender.is_yes_button:
            self.__reset_dialog()

        self.new_warning_dialog.close()

    def on_save_button_pressed(self):

        self.save_warning_dialog = WarningDialog(self)
        self.save_warning_dialog.set_label_text("Do you want to save the file? Data will be overwritten")
        self.save_warning_dialog.set_buttons_on_click(self.on_save_warning_clicked)
        self.save_warning_dialog.set_button_text("Continue", set_button_yes=True)
        self.save_warning_dialog.set_button_text("Cancel", set_button_yes=False)

        self.save_warning_dialog.show()

    def on_save_warning_clicked(self):

        sender = self.sender()
        if sender.is_yes_button:
            self.__save()

        self.save_warning_dialog.close()

    def on_format_pressed(self):

        self.code.update()
        self.input_script.setHtml(self.code.rich_text)
        self.input_script.repaint()

        if hasattr(self, 'tables'):
            if "Parameters Indices" in self.tables.keys():
                new_model = IndexSetterTableModel(self, "Parameters Indices")
                new_model.load_data(self.code.inputs)
                self.tables["Parameters Indices"].setModel(new_model)
                self.tables["Parameters Indices"].repaint()

    def __enable_buttons(self):

        self.button_save.setEnabled(self.is_ready_for_saving)

    def __reset_dialog(self):

        self.init_title()
        self.name_edit_text.setText("")
        self.input_script.setText("\"insert here your EES code ...\"")

        self.name_edit_text.setEnabled(True)
        self.type_combobox.setEnabled(True)

        self.on_format_pressed()

    def __save(self):

        return_list = self.code.save()

        folder_name = return_list[0]
        file_name = return_list[1]

        self.is_saved = True
        self.EES_code_name = os.path.join(folder_name, file_name)
        self.name_edit_text.setEnabled(False)
        self.type_combobox.setEnabled(False)
        self.__update_title()

    def __set_buttons_shortcut(self):

        sequence_save = QKeySequence(Qt.CTRL + Qt.Key_S)
        self.button_save.setShortcut(sequence_save)

        sequence_new = QKeySequence(Qt.CTRL + Qt.Key_N)
        self.button_new.setShortcut(sequence_new)

        sequence_format = QKeySequence(Qt.CTRL + Qt.Key_F)
        self.button_format.setShortcut(sequence_format)

    def __update_title(self):

        title = self.EES_code_name + " - "

        if not self.is_saved:
            title += "Not "

        title += "Saved"

        self.setWindowTitle(title)

    @property
    def is_ready_for_saving(self):

        __name = self.name_edit_text.text()
        __input_script = self.input_script.toPlainText()

        return not __name == "" and not (__input_script == "" or __input_script == "\"insert here your EES code ...\"")


class EESTextFilesManager(AbstractFilesManager):

    def __init__(self, flags=None, *args, **kwargs):

        super().__init__(flags, *args, **kwargs)

        self.title = "EES File Manager"
        self.modules_handler = ModulesHandler()

    def on_button_add_pressed(self):

        self.file_edit = DefineEESTextWidget(self)

        if not os.path.isdir(self.selected_element_path):

            dir_name = os.path.dirname(self.selected_element_path)

        else:

            dir_name = self.selected_element_path

        self.file_edit.set_combobox_name(os.path.basename(dir_name))
        self.file_edit.type_combobox.setEnabled(False)
        self.file_edit.show()

    def on_button_modify_pressed(self):

        self.file_edit = DefineEESTextWidget(self)

        self.file_edit.open_file(self.selected_element_path)
        self.file_edit.name_edit_text.setEnabled(False)
        self.file_edit.type_combobox.setEnabled(False)
        self.file_edit.show()

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
        self.duplicate_warning_dialog.set_buttons_on_click(self.on_duplicate_warning_pressed)
        self.duplicate_warning_dialog.set_button_text("Yes", set_button_yes=True)
        self.duplicate_warning_dialog.set_button_text("No", set_button_yes=False)

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

        Code.rename_file(new_name, file_path)
        super(EESTextFilesManager, self).__rename_file(new_name, file_path)