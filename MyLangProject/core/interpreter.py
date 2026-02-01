import sys
from locales.manager import t


class Interpreter:
    def __init__(self, console_callback=print):
        self.console_callback = console_callback
        self.variables = {}

    def execute(self, code):
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            try:
                self.parse_line(line)
            except Exception as e:
                # --- ЛОГИКА ОТОБРАЖЕНИЯ ОШИБКИ ---
                # Если ошибка содержит позицию (msg, col)
                if isinstance(e.args[0], tuple):
                    msg, col = e.args[0]

                    # Формируем стрелочку
                    # col - это индекс начала ошибки.
                    pointer = " " * col + "^"

                    full_error = (
                        f"{t.get('error_file')} \"main.mylang\", {t.get('error_line')} {line_num}\n"
                        f"    {line}\n"
                        f"    {pointer}\n"
                        f"{t.get('syntax_error')}: {msg}"
                    )
                    self.console_callback(full_error, is_error=True)
                else:
                    # Обычная ошибка
                    self.console_callback(f"Line {line_num}: {str(e)}", is_error=True)
                return

    def parse_line(self, line):
        tokens = self.tokenize(line)
        if not tokens:
            return

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

            # Пропускаем пробелы
            if char.isspace():
                i += 1
                continue

            # Спецсимволы
            if char in ['(', ')', '=', '+', '-', '*', '/']:
                tokens.append(char)
                i += 1
                continue

            # Строки
            if char == '"' or char == "'":
                quote_type = char
                start_col = i  # <--- ЗАПОМИНАЕМ ГДЕ НАЧАЛАСЬ СТРОКА
                i += 1
                value = ""

                while i < length and line[i] != quote_type:
                    value += line[i]
                    i += 1

                # Если дошли до конца строки, а кавычку не нашли
                if i >= length:
                    # БРОСАЕМ start_col (начало), а не i (конец)
                    raise Exception((t.get('unterminated_string'), start_col))

                tokens.append(f"STR:{value}")
                i += 1
                continue

            # Числа и слова
            value = ""
            while i < length and not line[i].isspace() and line[i] not in ['(', ')', '=', '"', "'"]:
                value += line[i]
                i += 1

            if value:
                tokens.append(value)

        return tokens

    def handle_print(self, tokens):
        # Простая проверка скобок
        if len(tokens) < 3 or tokens[1] != '(':
            # Указываем на команду, если нет скобки
            raise Exception((t.get('syntax_error'), 0))

        if tokens[-1] != ')':
            # Указываем в конец, если нет закрывающей
            raise Exception((t.get('expected_bracket'), len(tokens)))

        args = tokens[2:-1]
        result = self.evaluate_expression(args)
        self.console_callback(result)

    def handle_var(self, tokens):
        if len(tokens) < 4 or tokens[2] != '=':
            raise Exception("Invalid variable declaration")

        var_name = tokens[1]
        value = self.evaluate_expression(tokens[3:])
        self.variables[var_name] = value

    def evaluate_expression(self, tokens):
        result = ""
        is_number = True
        current_sum = 0

        for token in tokens:
            if token == '+':
                continue

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