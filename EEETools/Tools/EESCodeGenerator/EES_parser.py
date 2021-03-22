from rply import LexerGenerator, ParserGenerator, Token
from rply.token import BaseBox
from EEETools.costants import get_html_string


class EESCodeAnalyzer:

    def __init__(self):

        self.__init_lexer_generator()
        self.__init_parser_generator()

        self.__init_lexer_generator(init_splitter=True)
        self.__init_splitting_parser_generator()

    def get_code_parts(self, input_string: str, print_token=False):

        if not input_string == "":

            if print_token:

                tokens_res = self.splitting_lexer.lex(input_string)
                for token in tokens_res:
                    print(token)

                print()

            try:

                tokens_res = self.splitting_lexer.lex(input_string)
                parsed_string = self.splitting_parser.parse(tokens_res)

                return_list = list()
                parsed_string.update_list(return_list)

                return return_list

            except:

                if not print_token:
                    self.get_code_parts(input_string, True)
                else:
                    raise

        else:

            return None

    def parse_string(self, input_string: str, print_token=False):

        if not input_string == "":

            if print_token:

                tokens_res = self.lexer.lex(input_string)
                for token in tokens_res:
                    print(token)

                print()

            try:
                tokens_res = self.lexer.lex(input_string)
                parsed_string = self.parser.parse(tokens_res)
                return parsed_string

            except:

                if not print_token:
                    self.parse_string(input_string, True)
                else:
                    raise

        else:

            return None

    # LINE CODE ANALYSIS

    # main lexer generation methods
    def __init_lexer_generator(self, init_splitter=False):

        self.lg = LexerGenerator()

        if init_splitter:
            self.splitting_tokens_list = list()

        else:
            self.tokensList = list()

        self.__define_simple_tokens(init_splitter)
        self.__define_keywords_tokens(init_splitter)
        self.__define_operator_tokens(init_splitter)
        self.__define_bracket_tokens(init_splitter)
        self.__define_other_tokens(init_splitter)

        if not init_splitter:
            self.lg.ignore(r'\s+')

        if init_splitter:
            self.splitting_lexer = self.lg.build()

        else:
            self.lexer = self.lg.build()

    def __define_simple_tokens(self, is_splitter):

        self.__add_token('NUMBER', r'\d+', is_splitter)

    def __define_keywords_tokens(self, is_splitter):

        if is_splitter:
            self.__add_token('OPTIONAL', r'optional', is_splitter)

        self.__add_token('REPEAT_KEYWORD', r'sum|multiply|repeat', is_splitter)

        self.__add_token('INPUT', r'input', is_splitter)
        self.__add_token('BLOCK_INDEX', r'block_index', is_splitter)
        self.__add_token('FLUID', r'fluid', is_splitter)
        self.__add_token('CALL', r'Call', is_splitter)

    def __define_operator_tokens(self, is_splitter):

        self.__add_token('DOLLAR', r'\$', is_splitter)
        self.__add_token('AMPERSAND', r'\&', is_splitter)
        self.__add_token('DOUBLE_QUOTE', r'\"', is_splitter)

        self.__add_token('COMMA', r'\,', is_splitter)
        self.__add_token('PLUS', r'\+', is_splitter)
        self.__add_token('MINUS', r'-', is_splitter)
        self.__add_token('MUL', r'\*', is_splitter)
        self.__add_token('DIV', r'/', is_splitter)
        self.__add_token('EQUAL', r'=', is_splitter)

    def __define_bracket_tokens(self, is_splitter):

        self.__add_token('OPEN_ROUND_BRACKET', r'\(', is_splitter)
        self.__add_token('CLOSE_ROUND_BRACKET', r'\)', is_splitter)
        self.__add_token('OPEN_SQUARED_BRACKET', r'\[', is_splitter)
        self.__add_token('CLOSE_SQUARED_BRACKET', r'\]', is_splitter)
        self.__add_token('OPEN_CURLY_BRACKET', r'\{', is_splitter)
        self.__add_token('CLOSE_CURLY_BRACKET', r'\}', is_splitter)

    def __define_other_tokens(self, is_splitter):

        if is_splitter:
            self.__add_token('SPACE', r'[\s]', is_splitter)

        self.__add_token('IDENTIFIER', r'[_a-zA-Z][_a-zA-Z0-9]*', is_splitter)
        self.__add_token('TEXT', r'[\S]*', is_splitter)

    # main parser generation methods
    def __init_parser_generator(self):

        self.pg = ParserGenerator(

            # A list of all token names, accepted by the parser.
            self.tokensList,

            # A list of precedence rules with ascending precedence, to
            # disambiguate ambiguous production rules.
            precedence=[

                ('left', ['PLUS', 'MINUS']),
                ('left', ['MUL', 'DIV'])
            ]

        )

        self.__add_line_rules()
        self.__add_comment_rules()
        self.__add_expression_rules()
        self.__add_atoms_rules()

        @self.pg.error
        def error_handler(token):
            raise ValueError(
                "Ran into a " + str(token.gettokentype()) + " where it wasn't expected! Token: " + str(token))

        self.parser = self.pg.build()

    def __add_atoms_rules(self):

        # NUMBER
        # e.g. 10
        @self.pg.production('atom : NUMBER')
        def expression_number(p):
            # p is a list of the pieces matched by the right hand side of the
            # rule
            return Number(int(p[0].getstr()))

        # IDENTIFIER
        # e.g. h_iso
        @self.pg.production('atom : IDENTIFIER')
        def expression_number(p):
            # p is a list of the pieces matched by the right hand side of the
            # rule
            return Identifier(p[0].getstr())

        # VARIABLE
        # e.g. P[$0]
        @self.pg.production('atom : IDENTIFIER OPEN_SQUARED_BRACKET DOLLAR NUMBER CLOSE_SQUARED_BRACKET')
        def expression_parens(p):
            return Variable(p[0].getstr(), int(p[3].getstr()))

        # VARIABLE WITH BLOCK INDEX
        # e.g. P[$block_index]
        @self.pg.production('atom : IDENTIFIER OPEN_SQUARED_BRACKET DOLLAR BLOCK_INDEX CLOSE_SQUARED_BRACKET')
        def expression_parens(p):
            return Variable(p[0].getstr(), -1, is_block_index=True)

        # FLUID VARIABLE
        # e.g. $fluid
        @self.pg.production('atom : DOLLAR FLUID')
        def expression_parens(p):
            return Variable("fluid", -1, is_fluid=True)

    def __add_expression_rules(self):

        # REPEAT KEYWORD EXPRESSION
        # e.g. $repeat{ ... }
        @self.pg.production('expression : AMPERSAND REPEAT_KEYWORD OPEN_CURLY_BRACKET expression CLOSE_CURLY_BRACKET')
        def expression_parens(p):
            return RepeatKeywordExpression(p[1].getstr(), p[3])

        # FUNCTION
        # e.g. Enthalpy(fluid, P = P[$0], T = T[$1])
        @self.pg.production('expression : IDENTIFIER OPEN_ROUND_BRACKET arguments CLOSE_ROUND_BRACKET')
        def expression_parens(p):
            return Function(p[0].getstr(), p[2])

        # FUNCTION ARGUMENTS
        # e.g. fluid, ...
        @self.pg.production('arguments : argument COMMA arguments')
        def expression_parens(p):
            return FunctionArgument(p[0], p[2])

        @self.pg.production('arguments : argument')
        def expression_parens(p):
            return FunctionArgument(p[0])

        # FUNCTION ARGUMENT
        # e.g. fluid or P = P[$0]
        @self.pg.production('argument : atom')
        def expression_parens(p):
            return p[0]

        @self.pg.production('argument : atom EQUAL atom')
        def expression_parens(p):
            return BinaryOp(p[0], p[2], "=")

        # ROUND BRACKET EXPRESSION
        # e.g. (10 + 20)
        @self.pg.production('expression : OPEN_ROUND_BRACKET expression CLOSE_ROUND_BRACKET')
        def expression_parens(p):
            return RoundedBracket(p[1])

        @self.pg.production('expression : expression EQUAL expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        @self.pg.production('expression : expression PLUS expression')
        @self.pg.production('expression : expression MINUS expression')
        def expression_binop(p):

            left = p[0]
            right = p[2]

            if p[1].gettokentype() == 'PLUS':
                return BinaryOp(left, right, "+")

            elif p[1].gettokentype() == 'MINUS':
                return BinaryOp(left, right, "-")

            elif p[1].gettokentype() == 'MUL':
                return BinaryOp(left, right, "*")

            elif p[1].gettokentype() == 'DIV':
                return BinaryOp(left, right, "/")

            elif p[1].gettokentype() == 'EQUAL':
                return BinaryOp(left, right, "=")

            else:
                raise AssertionError('Oops, this should not be possible!')

        # BASE EXPRESSION
        @self.pg.production('expression : atom')
        def expression_parens(p):
            return p[0]

    def __add_comment_rules(self):

        @self.pg.production('comments : comment comments')
        def expression_comment_string(p):
            return CommentString(p[0], p[1])

        @self.pg.production('comments : comment')
        def expression_comment_string(p):
            return CommentString(p[0])

        for token in self.tokensList:

            if not token == 'NEW_LINE':
                input_str = 'comment : ' + token

                @self.pg.production(input_str)
                def expression_comment_string(p):
                    return p[0].getstr()

    def __add_line_rules(self):

        # LINE WITH COMMENT
        # e.g. Delta_p[$blockIndex] = $input[2] "in [Pa]"
        @self.pg.production('line : line DOUBLE_QUOTE comments')
        def expression_line(p):
            return Line(p[0], Comment(p[2]))

        # COMMENT LINE
        # e.g. "this is a comment"
        @self.pg.production('line : DOUBLE_QUOTE comments')
        @self.pg.production('line : DOUBLE_QUOTE comments DOUBLE_QUOTE')
        def expression_line(p):
            return Line(input_comment=Comment(p[1]))

        # SIMPLE LINE
        @self.pg.production('line : expression')
        @self.pg.production('line : input_line')
        @self.pg.production('line : call_line')
        def expression_comment(p):
            return Line(input_expression=p[0])

        # INPUT LINE
        # e.g. Delta_p[$blockIndex] = $input[2]
        input_str = 'input_line : expression EQUAL DOLLAR INPUT OPEN_SQUARED_BRACKET NUMBER CLOSE_SQUARED_BRACKET'

        @self.pg.production(input_str)
        def expression_parens(p):

            if type(p[0]) is Identifier or type(p[0]) is Variable:

                input = Variable(p[0].name, int(p[5].getstr()), is_input=True)
                return InputBlock(p[0], input)

            else:

                error_text = "you provided input as " + str(type(p[0])) + " = $input[#]. "
                error_text += "But input must be written as name = $input[#]!"
                raise ValueError(error_text)

        # FUNCTION CALL
        # e.g. Call calculate_cost(A[$block_index], k_0, k_1)
        @self.pg.production('call_line : CALL expression')
        def expression_parens(p):

            if type(p[1]) is Function:

                p[1].is_called = True
                return p[1]

            else:

                error_text = "you provided function call as Call " + str(type(p[1])) + ". "
                error_text += "But function call must be written as Call FUNCTION!"
                raise ValueError(error_text)

    # CODE SPLITTING PARSER AND LEXER DEFINITION

    # Code Splitting generation methods
    def __init_splitting_parser_generator(self):

        self.splitting_pg = ParserGenerator(

            # A list of all token names, accepted by the parser.
            self.splitting_tokens_list,

            # A list of precedence rules with ascending precedence, to
            # disambiguate ambiguous production rules.
            precedence=[]

        )

        self.__add_main_rules()
        self.__add_code_rules()
        self.__add_token_rules()

        @self.splitting_pg.error
        def error_handler(token):
            raise ValueError(
                "Ran into a " + str(token.gettokentype()) + " where it wasn't expected! Token: " + str(token))

        self.splitting_parser = self.splitting_pg.build()

    def __add_main_rules(self):

        @self.splitting_pg.production('main_code : code_container main_code')
        @self.splitting_pg.production('main_code : code_container')
        def add_optional_code_container(p):
            if len(p) == 2:
                p[0].set_next(p[1])

            return p[0]

    def __add_code_rules(self):

        @self.splitting_pg.production(
            'code_container : code_identifier OPEN_CURLY_BRACKET code_parts CLOSE_CURLY_BRACKET')
        def add_optional_code_container(p):

            __identifier_list = p[0]
            container_type = __identifier_list[0]
            container_name = __identifier_list[1]

            return CodeSection(input_type=container_type, input_name=container_name, expression=p[2])

        @self.splitting_pg.production('code_identifier : AMPERSAND REPEAT_KEYWORD')
        @self.splitting_pg.production(
            'code_identifier : AMPERSAND OPTIONAL OPEN_ROUND_BRACKET IDENTIFIER CLOSE_ROUND_BRACKET')
        def add_code_container_information(p):

            container_type = p[1].getstr()

            if len(p) > 2:
                container_name = p[3].getstr()
            else:
                container_name = ""

            return [container_type, container_name]

        @self.splitting_pg.production('code_container : OPEN_ROUND_BRACKET code_parts CLOSE_ROUND_BRACKET')
        def add_code_in_bracket(p):

            if issubclass(BaseBox, type(p[1])):
                result = p[1]

            elif type(p[0]) is Token:
                result = CodePart(p[1].getstr())

            else:
                result = CodePart(str(p[1]))

            if len(p) == 2:
                result.set_next(p[1])

            result.has_bracket = True

            return result

        @self.splitting_pg.production('code_container : code_parts')
        def add_optional_code_container(p):
            return CodeSection(p[0])

        @self.splitting_pg.production('code_parts : code_part code_parts')
        @self.splitting_pg.production('code_parts : code_part')
        def add_code(p):

            if issubclass(BaseBox, type(p[0])):
                result = p[0]

            elif type(p[0]) is Token:
                result = CodePart(p[0].getstr())

            else:
                result = CodePart(str(p[0]))

            if len(p) == 2:
                result.set_next(p[1])

            return result

    def __add_token_rules(self):

        preserved_token = ["OPEN_CURLY_BRACKET",
                           "CLOSE_CURLY_BRACKET",
                           "OPEN_CURLY_BRACKET",
                           "CLOSE_CURLY_BRACKET",
                           "REPEAT_KEYWORD",
                           "OPTIONAL",
                           "AMPERSAND"]

        for token in self.splitting_tokens_list:

            if token not in preserved_token:
                input_str = 'code_part : ' + token

                @self.splitting_pg.production(input_str)
                def add_code(p):
                    return CodePart(p[0].getstr())

    # SUPPORT FUNCTIONS
    def __add_token(self, name, rule, is_splitting=False):

        self.lg.add(name, rule)

        if is_splitting:
            self.splitting_tokens_list.append(name)

        else:
            self.tokensList.append(name)


# <--------------------- Code Element Classes --------------------->

# Main Parser Classes
class EESBaseBox(BaseBox):

    def __init__(self):

        self.is_input = False
        self.is_variable = False

        self.expression = None
        self.left = None
        self.right = None
        self.next = None

    def append_variable_to_list(self, variable_list: list):

        if self.is_variable:
            variable_list.append(self)

        for element in [self.next, self.expression, self.right, self.left]:

            if element is not None:
                element.append_variable_to_list(variable_list)


class Line(EESBaseBox):

    def __init__(self, input_expression=None, input_comment=None, input_next=None):

        super().__init__()

        if type(input_expression) is Line:

            if input_expression is not None:
                __tmp_expression = input_expression
                input_expression = __tmp_expression.expression
                input_comment = __tmp_expression.comment

        self.expression = input_expression
        self.comment = input_comment
        self.next = input_next

    @property
    def rich_text(self):

        __rich_text = ""

        if self.expression is not None:
            __rich_text += self.expression.rich_text

        if self.comment is not None:
            __rich_text += self.comment.rich_text

        if self.next is not None:
            __rich_text += "<br>"
            __rich_text += self.next.rich_text

        return __rich_text


class Comment(EESBaseBox):

    def __init__(self, comment_string):
        super().__init__()
        self.comment_string = comment_string

    @property
    def rich_text(self):
        __rich_text = get_html_string("comments", "\"")
        __rich_text += self.comment_string.rich_text

        return __rich_text

    def append_variable_to_list(self, variable_list: list):
        # comment does not contain variables
        pass


class CommentString(EESBaseBox):

    def __init__(self, text, next_input=None):
        super().__init__()
        self.text = text
        self.next = next_input

    @property
    def rich_text(self):
        __rich_text = get_html_string("comments", self.text)

        if not self.next is None:
            __rich_text += get_html_string("comments", " ")
            __rich_text += self.next.rich_text

        return __rich_text


class Variable(EESBaseBox):

    def __init__(self, name, index, is_block_index=False, is_input=False, is_fluid=False):

        super().__init__()
        self.name = name
        self.index = index

        self.is_variable = True
        self.is_block_index = is_block_index
        self.is_input = is_input
        self.is_fluid = is_fluid

    @property
    def rich_text(self):

        if self.is_input:

            __rich_text = get_html_string("variable", "$input[" + str(self.index) + "]")

        elif self.is_fluid:

            __rich_text = get_html_string("variable", "$fluid")

        else:

            __rich_text = get_html_string("default", str(self.name) + "[")

            if self.is_block_index:
                __rich_text += get_html_string("variable", "$block_index")

            else:
                __rich_text += get_html_string("variable", "$" + str(self.index))

            __rich_text += get_html_string("default", "]")

        return __rich_text


class Number(EESBaseBox):

    def __init__(self, value):
        super().__init__()
        self.value = value

    @property
    def rich_text(self):
        __rich_text = get_html_string("default", str(self.value))
        return __rich_text


class Identifier(EESBaseBox):

    def __init__(self, name):
        super().__init__()
        self.name = name

    @property
    def rich_text(self):
        __rich_text = get_html_string("default", str(self.name))
        return __rich_text


class RepeatKeywordExpression(EESBaseBox):

    def __init__(self, key_word, expression):
        super().__init__()
        self.key_word = key_word
        self.expression = expression

    @property
    def rich_text(self):
        __rich_text = get_html_string("repeated_keyword", "&" + str(self.key_word))

        __rich_text += get_html_string("default", "{")
        __rich_text += self.expression.rich_text
        __rich_text += get_html_string("default", "}")

        return __rich_text


class Function(EESBaseBox):

    def __init__(self, name, expression):
        super().__init__()
        self.name = name
        self.expression = expression
        self.is_called = False

    @property
    def rich_text(self):
        __rich_text = ""

        if self.is_called:
            __rich_text = get_html_string("known_keyword", "Call ")

        __rich_text += get_html_string("unknown_function", str(self.name))

        __rich_text += get_html_string("default", "(")
        __rich_text += self.expression.rich_text
        __rich_text += get_html_string("default", ")")

        return __rich_text


class FunctionArgument(EESBaseBox):

    def __init__(self, expression, input_next=None):
        super().__init__()
        self.expression = expression
        self.next = input_next

    @property
    def rich_text(self):
        __rich_text = self.expression.rich_text

        if not self.next is None:
            __rich_text += get_html_string("default", ", ")
            __rich_text += self.next.rich_text

        return __rich_text


class RoundedBracket(EESBaseBox):

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    @property
    def rich_text(self):
        __rich_text = get_html_string("default", "(")
        __rich_text += self.expression.rich_text
        __rich_text += get_html_string("default", ")")

        return __rich_text


class InputBlock(EESBaseBox):

    def __init__(self, variable: Variable, input: Variable):
        super().__init__()
        self.variable = variable
        self.input = input

        self.input.is_input = True
        self.input.name = self.variable.name

    @property
    def rich_text(self):
        __rich_text = self.variable.rich_text
        __rich_text += get_html_string("default", " = ")
        __rich_text += self.input.rich_text

        return __rich_text

    def append_variable_to_list(self, variable_list: list):
        self.variable.append_variable_to_list(variable_list)
        self.input.append_variable_to_list(variable_list)


class BinaryOp(EESBaseBox):

    def __init__(self, left, right, type):
        super().__init__()
        self.left = left
        self.right = right

        self.type = type

    @property
    def rich_text(self):
        __rich_text = self.left.rich_text
        __rich_text += get_html_string("default", " " + str(self.type) + " ")
        __rich_text += self.right.rich_text

        return __rich_text


# Splitting Parser Classes
class CodeSection(BaseBox):

    def __init__(self, expression, input_name="main", input_type="default", input_next=None):
        super().__init__()
        self.name = input_name
        self.type = input_type

        if issubclass(BaseBox, type(expression)):
            self.expression = expression

        else:
            self.expression = CodePart(str(expression))

        self.next = input_next

    def set_next(self, input_next):
        self.next = input_next

    def update_list(self, input_list: list):

        if len(input_list) > 0:

            if self.type == "default" and input_list[-1]["type"] == "default":
                self.__extend_list_expression(input_list)

            elif self.type not in ["optional", "default"]:
                self.__extend_list_expression(input_list)

            else:
                self.__append_to_list(input_list)

        else:
            self.__append_to_list(input_list)

        if self.next is not None:
            self.next.update_list(input_list)

    def __append_to_list(self, input_list):

        input_list.append({"name": self.name, "type": self.type, "expression": self.plain_text})

    def __extend_list_expression(self, input_list):

        input_list[-1]["expression"] += self.plain_text

    @property
    def plain_text(self):

        if self.type not in ["optional", "default"]:

            return "&" + self.type + "{" + self.expression.plain_text + "}"

        else:
            return self.expression.plain_text


class CodePart(BaseBox):

    def __init__(self, input_expression, input_next=None, has_bracket=False):
        self.expression = input_expression
        self.next = input_next
        self.has_bracket = has_bracket

    @property
    def plain_text(self):

        if self.has_bracket:
            __plain_text = "("

        else:
            __plain_text = ""

        __plain_text += str(self.expression)

        if self.has_bracket:
            __plain_text += ")"

        if self.next is not None:
            __plain_text += self.next.plain_text

        return __plain_text

    def set_next(self, input_next):
        self.next = input_next

    def __str__(self):
        return self.plain_text
