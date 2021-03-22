from src.Tools.EESCodeGenerator.EES_parser import EESCodeAnalyzer
from src.Tools.Other.fernet_handler import FernetHandler
from src.Tools.modules_handler import ModulesHandler
from src.costants import get_html_string
import xml.etree.ElementTree as ETree
import os


class Code:

    def __init__(self, modify_widget=None):

        self.modify_widget = modify_widget
        self.code_analyzer = EESCodeAnalyzer()
        self.modules_handler = ModulesHandler()

        self.blocks = list()
        self.inputs = dict()
        self.options = list()

        self.plain_text = ""
        self.rich_text = ""
        self.parsed_code = None

        self.update()

    def update(self):

        if self.modify_widget is not None:

            text = self.modify_widget.input_script.toPlainText()

        else:

            text = self.plain_text

        self.blocks = list()

        try:
            __block_list = self.code_analyzer.get_code_parts(text)

        except:
            self.blocks.append(CodeBlock(input_text=text))

        else:

            for __block_element in __block_list:
                __name = __block_element["name"]
                __type = __block_element["type"]
                __text = __block_element["expression"]

                self.blocks.append(CodeBlock(input_name=__name, input_type=__type, input_text=__text))

        self.plain_text = text
        self.set_rich_text()
        self.__update_inputs()

    def set_rich_text(self):

        self.rich_text = "<!DOCTYPE html>"
        self.rich_text += "<html><head>"
        self.rich_text += "<style>tab{margin-left: 10px;display:block;}</style>"
        self.rich_text += "</head><body><div contenteditable><p>"

        for line in self.blocks:
            self.rich_text += line.rich_text

        self.rich_text += "</p></div></body></html>"

    def __update_inputs(self):

        self.inputs = dict()

        for block in self.blocks:

            if block.has_input:
                self.inputs.update(block.inputs)

    def __update_options(self):

        self.options = list()

        for block in self.blocks:

            if block.type == "optional":
                self.options.append(block.name)

    # <----------------- READ & SAVE METHODS --------------->

    def save(self):

        # This class save the code data to a .dat file containing an encrypted xml tree. Encryption is useful in
        # order to prevent the user from modifying the file manually without going through the editor.
        #
        # The method generate the xml tree and pass it to the "__save_to_file" method that is in charge of the
        # encryption and file saving processes.
        #
        # here is an example of EES code xml file:
        #
        #   <data>
        #
        #     <header name="standard" component_type="Expander">
        #
        #         <options>
        #
        #             <option name="set_delta_P"/>
        #
        #         </options>
        #         <inputs>
        #
        #             <input name="Eff",     index="1",  related_option = "none"/>
        #             <input name="Delta_P", index="0",  related_option = "set_delta_P"/>
        #
        #         </inputs>
        #
        #         <variables>
        #
        #             <variable name="power input",  index="0",  multiple_check="False" />
        #             <variable name="flow input",   index="1",  multiple_check="False" />
        #             <variable name="flow output",  index="2",  multiple_check="False" />
        #
        #         </variables>
        #
        #     </header>
        #
        #     <EESCode>
        #
        #       "Turbine "
        #       Eff[$block_index] = $input[0]
        #
        #       &optional(set_delta_P){
        #
        #           Delta_P[$block_index] = $input[1]
        #           P[$2] = P[$1] - Delta_P[$block_index]
        #
        #       }
        #
        #       h_iso[$2] = enthalpy($fluid, P = P[$1], s = s[$1])
        #
        #       h[$2] = h[$1] + (h_iso[$2] - h[$1]) * Eff[$block_index]
        #       s[$2] = entropy($fluid, P = P[$2], h = h[$2])
        #       T[$2] = temperature($fluid, P = P[$2], h = h[$2])
        #
        #       m_dot[$2] = m_dot[$1]
        #       W[$0] = (h[$1] - h[$2]) * m_dot[$1]
        #
        #     </EESCode>
        #
        #   </data>

        if self.modify_widget is not None:

            data = ETree.Element("data")

            # <--------- HEADER DEFINITION --------->
            header = ETree.SubElement(data, "header")

            code_name = self.modify_widget.name_edit_text.text().lower()
            component_type = self.modify_widget.type_combobox.currentText()

            header.set("name", code_name)
            header.set("component_type", component_type)

            # <--------- OPTIONS DEFINITION --------->
            options = ETree.SubElement(header, "options")

            for option in self.options:
                input_element = ETree.SubElement(options, "option")
                input_element.set("name", str(option))

            # <--------- INPUTS DEFINITION --------->
            inputs = ETree.SubElement(header, "inputs")

            inputs_dict = self.inputs
            for key in inputs_dict.keys():
                input_element = ETree.SubElement(inputs, "input")
                input_element.set("name", str(key))
                input_element.set("index", str(inputs_dict[key][0]))
                input_element.set("related_option", str(inputs_dict[key][1]))

            # <--------- VARIABLES DEFINITION --------->
            variables = ETree.SubElement(header, "variables")

            variable_dict = self.modify_widget.tables["Input Indices"].model().data_dict
            for key in variable_dict.keys():
                variable = ETree.SubElement(variables, "variable")
                variable.set("name", str(key))
                variable.set("index", str((variable_dict[key])[0]))
                variable.set("multiple_check", str((variable_dict[key])[1]))

            # <--------- EES CODE DEFINITION --------->
            EES_code = ETree.SubElement(data, "EESCode")
            EES_code.text = self.plain_text

            # <--------- FILE PATH DEFINITION --------->
            main_folder = self.modules_handler.data_folder
            folder_name = self.modules_handler.get_module_name(component_type)
            file_name = code_name + ".dat"

            file_path = os.path.join(main_folder, folder_name, file_name)

            self.__save_to_file(data, file_path)

        else:

            folder_name = ""
            file_name = ""

        return [folder_name, file_name]

    def read_file(self, file_path):

        root = self.__read_file(file_path)

        EES_code = root.find("EESCode").text
        self.plain_text = EES_code

        return root

    @classmethod
    def rename_file(cls, new_name, file_path):

        root = cls.__read_file(file_path)

        header = root.find("header")
        header.attrib["name"] = new_name

        cls.__save_to_file(root, file_path)

    @staticmethod
    def __read_file(file_path):

        if ".xml" not in file_path:

            fernet = FernetHandler()
            root = fernet.read_file(file_path)

        else:

            data = file_path
            tree = ETree.parse(data)
            root = tree.getroot()

        return root

    @staticmethod
    def __save_to_file(root: ETree.Element, file_path):

        fernet = FernetHandler()
        fernet.save_file(file_path, root)


class CodeBlock:

    def __init__(self, input_type="default", input_name="", input_text=""):

        self.code_analyzer = EESCodeAnalyzer()
        self.modules_handler = ModulesHandler()

        self.lines = list()
        self.inputs = dict()

        self.type = input_type
        self.name = input_name

        self.plain_text = input_text
        self.rich_text = ""
        self.parsed_code = None

        self.update(self.plain_text)

    def update(self, text):

        self.lines = list()
        self.plain_text = text

        if not text == "":

            for line_text in text.splitlines():
                new_code_line = CodeLine(self.code_analyzer, line_text)
                self.lines.append(new_code_line)

            self.set_rich_text()
            self.__update_inputs()

    def set_rich_text(self):

        self.rich_text = ""
        __tabulation = ""

        if self.type == "optional":
            self.rich_text += "<br>"
            self.rich_text += get_html_string("repeated_keyword", "&optional")
            self.rich_text += get_html_string("default", "(")
            self.rich_text += get_html_string("variable", self.name)
            self.rich_text += get_html_string("default", ")")
            self.rich_text += get_html_string("default", "{")
            self.rich_text += "<tab>"

        self.rich_text += self.lines[0].rich_text

        if len(self.lines) > 1:

            for line in self.lines[1:]:
                self.rich_text += "<br>"
                self.rich_text += line.rich_text

        if self.type == "optional":
            self.rich_text += "</tab>"
            self.rich_text += "<br>"
            self.rich_text += get_html_string("default", "}")

    def __update_inputs(self):

        self.inputs = dict()

        if self.type == "default":
            __related_option = "none"

        else:
            __related_option = self.name

        for line in self.lines:

            if line.has_input:
                self.inputs.update(line.inputs)

        for key in self.inputs.keys():
            self.inputs[key].append(__related_option)

    @property
    def has_input(self):

        return not len(self.inputs) == 0


class CodeLine:

    def __init__(self, code_analyzer: EESCodeAnalyzer, plain_text: str):

        self.code_analyzer = code_analyzer
        self.parsed_text = None
        self.plain_text = plain_text
        self.rich_text = ""
        self.comment = ""

        self.inputs = dict()
        self.variables = list()

        self.__parse_text()

    def __parse_text(self):

        try:

            self.parsed_text = self.code_analyzer.parse_string(self.plain_text)

        except:

            self.has_error = True
            self.parsed_text = None
            self.rich_text = get_html_string("error", self.plain_text)

        else:

            self.has_error = False

            if not self.parsed_text is None:
                self.rich_text = self.parsed_text.rich_text

        self.__find_variables()

    def __find_variables(self):

        self.inputs = dict()
        self.variables = list()

        if self.parsed_text is not None:

            __tmp_variables = list()
            self.parsed_text.append_variable_to_list(__tmp_variables)

            for variable in __tmp_variables:

                self.variables.append(variable)

                if variable.is_input:
                    self.inputs.update({variable.name: [variable.index]})

    @property
    def has_input(self):

        return not len(self.inputs) == 0