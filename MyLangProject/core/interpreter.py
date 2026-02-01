import sys
from locales.manager import t


class Interpreter:
    def __init__(self, console_callback=print):
        self.console_callback = console_callback
        self.variables = {}

    def execute(self, code):
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Сохраняем оригинальную строку для вывода, но парсим стрипнутую
            original_line = line
            stripped_line = line.strip()

            if not stripped_line or stripped_line.startswith('#'):
                continue

            try:
                self.parse_line(stripped_line)
            except Exception as e:
                # ОБРАБОТКА ОШИБОК
                if isinstance(e.args[0], tuple):
                    msg, error_col = e.args[0]

                    # error_col - это индекс в stripped_line.
                    # Нам нужно найти этот индекс в original_line, учитывая отступы
                    indent = len(original_line) - len(original_line.lstrip())
                    real_col = indent + error_col

                    pointer = " " * real_col + "^"

                    full_error = (
                        f"{t.get('error_file')} \"main.mylang\", {t.get('error_line')} {line_num}\n"
                        f"    {original_line}\n"
                        f"    {pointer}\n"
                        f"{t.get('syntax_error')}: {msg}"
                    )
                    self.console_callback(full_error, is_error=True)
                else:
                    self.console_callback(f"Line {line_num}: {str(e)}", is_error=True)
                return

    def parse_line(self, line):
        tokens = self.tokenize(line)
        if not tokens: return

        command = tokens[0]
        if command == 'текст' or command == 'print':
            self.handle_print(tokens)
        elif command == 'перем' or command == 'var':
            self.handle_var(tokens)
        else:
            raise Exception(f"{t.get('unknown_command')} '{command}'")

    def tokenize(self, line):
        tokens = []
        i = 0
        length = len(line)

        while i < length:
            char = line[i]

            if char.isspace():
                i += 1
                continue

            if char in ['(', ')', '=', '+', '-', '*', '/']:
                tokens.append(char)
                i += 1
                continue

            if char == '"' or char == "'":
                quote_type = char
                start_col = i
                i += 1
                value = ""
                found_end = False

                while i < length:
                    if line[i] == quote_type:
                        found_end = True
                        break
                    value += line[i]
                    i += 1

                if not found_end:
                    # Бросаем позицию начала кавычки
                    raise Exception((t.get('unterminated_string'), start_col))

                tokens.append(f"STR:{value}")
                i += 1
                continue

            value = ""
            while i < length and not line[i].isspace() and line[i] not in ['(', ')', '=', '"', "'"]:
                value += line[i]
                i += 1
            if value: tokens.append(value)

        return tokens

    def handle_print(self, tokens):
        if len(tokens) < 3 or tokens[1] != '(':
            raise Exception((t.get('syntax_error'), 0))
        if tokens[-1] != ')':
            raise Exception((t.get('expected_bracket'), len(tokens)))  # Указываем на конец

        args = tokens[2:-1]
        result = self.evaluate_expression(args)
        self.console_callback(result)

    def handle_var(self, tokens):
        if len(tokens) < 4 or tokens[2] != '=': raise Exception("Invalid variable declaration")
        var_name = tokens[1]
        value = self.evaluate_expression(tokens[3:])
        self.variables[var_name] = value

    def evaluate_expression(self, tokens):
        result = ""
        is_number = True
        current_sum = 0
        for token in tokens:
            if token == '+': continue
            val = token
            if str(token).startswith("STR:"):
                val = token[4:]
                is_number = False
                result += str(val)
            elif token in self.variables:
                val = self.variables[token]
                if isinstance(val, int) and is_number:
                    current_sum += val
                else:
                    is_number = False
                    result += str(val)
            elif str(token).isdigit():
                if is_number:
                    current_sum += int(token)
                else:
                    result += token
            else:
                result += str(token)
        return current_sum if is_number and result == "" else (str(current_sum) if is_number else result)